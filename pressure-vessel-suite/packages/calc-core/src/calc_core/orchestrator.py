"""CalculationOrchestrator — hesap sırası yönetimi (kaynak §8).

Hesap sırası:
  A) Ön kontroller
  B) Malzeme değerleri
  C) Basınç taşıyan parçalar (gövde, bombeler)
  D) Nozul ve açıklıklar (Faz 3)
  E) MAWP
  F) Test basıncı
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from calc_core.code_interface import DesignCode
from calc_core.hydrostatics import static_head_pressure
from calc_core.result import CalculationResult
from calc_core.load_engine import aggregate_load_case, combine_load_cases, governing_state
from domain.enums import CalculationStatus
from domain.project import VesselProject


@dataclass
class OrchestratorResult:
    """Orchestrator'ın tüm hesap sonuçlarını bir arada tutan nesnesi."""
    project_number: str = ""
    project_name: str = ""
    code: str = ""
    edition: str = ""
    results: List[CalculationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add(self, result: CalculationResult) -> None:
        self.results.append(result)

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def all_passed(self) -> bool:
        if self.has_errors:
            return False
        return all(r.status == CalculationStatus.PASS for r in self.results)

    def get_results_by_component(self, component_id: str) -> List[CalculationResult]:
        """Belirli bir bileşenin tüm sonuçlarını getir."""
        return [r for r in self.results if r.component_id == component_id]

    def get_global_mawp(self) -> Optional[float]:
        """Global MAWP = min(tüm MAWP sonuçları).

        §19: Eksik/geçersiz bileşen varsa global MAWP None döner (sessizce min'e katılmaz).
        Yöneten bileşen `governing=True` ile işaretlenir.
        """
        mawp_results = [r for r in self.results if r.calculation_type == "mawp"]
        if not mawp_results:
            return None

        # Yalnızca gerçekten hesaplanmış sonuçları al (NOT_CALCULATED, BLOCKED_* hariç)
        blocked_statuses = {
            CalculationStatus.NOT_CALCULATED,
            CalculationStatus.BLOCKED_CODE_DATA,
            CalculationStatus.BLOCKED_MISSING_INPUT,
            CalculationStatus.OUT_OF_SCOPE,
        }
        valid_results = [
            r for r in mawp_results
            if r.status not in blocked_statuses and r.final_result is not None
        ]

        if not valid_results:
            return None

        # En düşük MAWP'yi bul ve governing olarak işaretle
        governing_result = min(valid_results, key=lambda r: r.final_result)
        for r in mawp_results:
            r.governing = False
        governing_result.governing = True

        return governing_result.final_result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_number": self.project_number,
            "project_name": self.project_name,
            "code": self.code,
            "edition": self.edition,
            "results": [r.to_dict() for r in self.results],
            "errors": self.errors,
        }


class CalculationOrchestrator:
    """Hesap sırasını yöneten orchestrator (kaynak §8).

    Kullanım:
        code = ASMEVIII1DesignCode()
        orch = CalculationOrchestrator(code)
        result = orch.run(project)
    """

    def __init__(self, design_code: DesignCode):
        self.design_code = design_code

    def run(self, project: VesselProject) -> OrchestratorResult:
        """Tüm hesap sırasını çalıştır.

        Sıra (kaynak §8):
          A) Ön kontroller
          B) Malzeme değerleri
          C) Basınç taşıyan parçalar
          D) Nozul (Faz 3'te devreye girer)
          E) MAWP
          F) Test basıncı
        """
        result = OrchestratorResult(
            project_number=project.project_number,
            project_name=project.project_name,
            code=self.design_code.code_name,
            edition=self.design_code.code_edition,
        )

        # A) Ön kontroller
        self._pre_checks(project, result)
        self._calculate_global_loads(project, result)

        # B) Malzeme değerleri kontrolü
        self._check_materials(project, result)

        # C) Basınç taşıyan parçalar — gövde
        for shell in project.shell_sections:
            try:
                r = self.design_code.calculate_shell_thickness({
                    "shell": shell,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "welds": project.welds,
                    "code_edition": project.code_edition,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Shell {shell.section_id} thickness calc error: {e}")

        # C) Basınç taşıyan parçalar — bombeler
        for head in project.heads:
            try:
                r = self.design_code.calculate_head_thickness({
                    "head": head,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "welds": project.welds,
                    "code_edition": project.code_edition,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Head {head.head_id} thickness calc error: {e}")

        # C2) Basınç taşıyan parçalar — konik bölümler
        for cone in project.cones:
            try:
                r = self.design_code.calculate_cone_thickness({
                    "cone": cone,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "welds": project.welds,
                    "code_edition": project.code_edition,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Cone {cone.cone_id} thickness calc error: {e}")

        # D) Nozul takviye hesabı
        for nozzle in project.nozzles:
            try:
                r = self.design_code.calculate_nozzle({
                    "nozzle": nozzle,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "shell_sections": project.shell_sections,
                    "heads": project.heads,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Nozzle {nozzle.tag} calc error: {e}")

        # D1) Flanşlar: Appendix 2 tasarım rotası; rating tablosu ayrı metadata'dır.
        for flange in getattr(project, "flanges", []):
            try:
                result.add(self.design_code.calculate_flange({
                    "flange": flange,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                }))
            except Exception as e:
                result.add_error(f"Flange {flange.flange_id} calc error: {e}")

        # D2) Nozul çakışma/geometri kontrolleri
        try:
            for r in self.design_code.check_nozzle_clashes(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"Nozzle clash check error: {e}")

        # D3) Kaynak doğrulama (NDT ↔ kaynak verimi, WPS/PQR, PWHT)
        try:
            for r in self.design_code.validate_welds(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"Weld validation error: {e}")

        # E) MAWP
        for shell in project.shell_sections:
            try:
                r = self.design_code.calculate_mawp({
                    "component_type": "shell",
                    "component": shell,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "welds": project.welds,
                    "nominal_thickness": shell.nominal_thickness,
                    "code_edition": project.code_edition,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Shell {shell.section_id} MAWP calc error: {e}")

        for head in project.heads:
            try:
                r = self.design_code.calculate_mawp({
                    "component_type": "head",
                    "component": head,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "welds": project.welds,
                    "nominal_thickness": head.nominal_thickness,
                    "code_edition": project.code_edition,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Head {head.head_id} MAWP calc error: {e}")

        for cone in project.cones:
            try:
                r = self.design_code.calculate_mawp({
                    "component_type": "cone",
                    "component": cone,
                    "design_conditions": project.design_conditions,
                    "materials": project.materials,
                    "welds": project.welds,
                    "nominal_thickness": cone.nominal_thickness,
                    "code_edition": project.code_edition,
                })
                result.add(r)
            except Exception as e:
                result.add_error(f"Cone {cone.cone_id} MAWP calc error: {e}")

        # E2) Statik kafa düzeltmesi (§19) — test basınçlarından ÖNCE çalışmalı:
        # UG-99(b)/UG-100 tabanı **nihai** MAWP'dir, düzeltme öncesi ham değer değil.
        self._apply_static_head_correction(project, result)

        # F) Test basıncı — taban global MAWP (UG-99(b)); MAWP yoksa design_code
        # endnote muafiyetine düşer ve varsayımı kaydeder.
        global_mawp = result.get_global_mawp()
        try:
            r = self.design_code.calculate_hydrotest_pressure({
                "project": project,
                "design_conditions": project.design_conditions,
                "materials": project.materials,
                "code_edition": project.code_edition,
                "global_mawp": global_mawp,
            })
            result.add(r)
        except Exception as e:
            result.add_error(f"Hydrotest calc error: {e}")

        # F2) Pnömatik test (UG-100)
        try:
            r = self.design_code.calculate_pneumatic_test_pressure({
                "project": project,
                "design_conditions": project.design_conditions,
                "materials": project.materials,
                "code_edition": project.code_edition,
                "global_mawp": global_mawp,
            })
            result.add(r)
        except Exception as e:
            result.add_error(f"Pneumatic test calc error: {e}")

        # G) Dış basınç / vakum kontrolü (UG-28)
        try:
            for r in self.design_code.check_external_pressure(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"External pressure check error: {e}")

        # H) MDMT (ASME'de UCS-66). Eğri grubu girilmemişse standart eklentisi
        #    BLOCKED_MISSING_INPUT döndürür — burada tahmin yapılmaz.
        try:
            for r in self.design_code.check_mdmt(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"MDMT check error: {e}")

        # Koni uç birleşimleri: desteklenmeyen gerçek çözüm yaklaşıklaştırılmaz.
        try:
            for r in getattr(self.design_code, "check_junctions", lambda _project: [])(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"Junction check error: {e}")

        # I) Destekler (eyer/etek/ayak). `project.supports` boşsa hiçbir şey
        #    üretilmez — destek tanımlamamak geçerli bir durumdur.
        try:
            for r in self.design_code.check_supports(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"Support check error: {e}")

        # J) Kod-özel yük kombinasyonları. Desteklenmeyen EN yolları sessizce
        # atlanmamalı; eklenti açık bir NOT_CALCULATED/OUT_OF_SCOPE sonucu döner.
        try:
            for r in self.design_code.check_load_combinations(project):
                result.add(r)
        except Exception as e:
            result.add_error(f"Load combination check error: {e}")

        # J) Basınç tahliye sistemi (ASME VIII-1 UG-125--136).
        try:
            for r in self.design_code.check_pressure_relief(project, result.get_global_mawp()):
                result.add(r)
        except Exception as e:
            result.add_error(f"Pressure relief check error: {e}")

        # (Statik kafa düzeltmesi E2'ye alındı — test basınçları nihai MAWP'yi
        #  kullanabilsin diye. Burada tekrar çağrılmaz: idempotent değildir,
        #  ikinci çağrı düzeltmeyi MAWP'den bir kez daha düşerdi.)

        return result

    def _calculate_global_loads(self, project: VesselProject, result: OrchestratorResult) -> None:
        """Aggregate global forces/moments without pretending to be a code check."""
        if not project.load_cases and not project.load_combinations:
            return
        cases = {case.load_case_id: case for case in project.load_cases}
        states = []
        for case in project.load_cases:
            state = aggregate_load_case(case)
            r = CalculationResult(
                component_id=case.load_case_id, component_type="system",
                calculation_type="global_load_case", code=self.design_code.code_name,
                edition=self.design_code.code_edition, load_case_id=case.load_case_id,
                input_snapshot=case.model_dump(),
            )
            r.add_intermediate("axial_force", state.axial_force_n, "N")
            r.add_intermediate("resultant_shear", state.resultant_shear_n, "N")
            r.add_intermediate("overturning_moment", state.resultant_overturning_moment_nmm, "N-mm")
            r.add_intermediate("torsional_moment", state.torsional_moment_z_nmm, "N-mm")
            for assumption in state.assumptions:
                r.add_assumption(assumption)
            r.set_review_required("Global load aggregation is not a code-specific support or stability check.")
            result.add(r)
            states.append(state)
        combination_states = []
        for combination in project.load_combinations:
            r = CalculationResult(
                component_id=combination.combination_id, component_type="system",
                calculation_type="global_load_combination", code=self.design_code.code_name,
                edition=self.design_code.code_edition, input_snapshot=combination.model_dump(),
            )
            try:
                state = combine_load_cases(cases, combination)
            except ValueError as exc:
                r.set_blocked_missing_input(str(exc))
                result.add(r)
                continue
            r.add_intermediate("axial_force", state.axial_force_n, "N")
            r.add_intermediate("resultant_shear", state.resultant_shear_n, "N")
            r.add_intermediate("overturning_moment", state.resultant_overturning_moment_nmm, "N-mm")
            r.add_intermediate("torsional_moment", state.torsional_moment_z_nmm, "N-mm")
            for assumption in state.assumptions:
                r.add_assumption(assumption)
            r.set_review_required("Load combination envelope requires code-specific structural checks.")
            result.add(r)
            combination_states.append(state)
        governing = governing_state(combination_states or states)
        if governing:
            for item in result.results:
                if item.calculation_type == "global_load_case" and item.load_case_id in governing.load_case_ids:
                    item.governing = True
                if item.calculation_type == "global_load_combination" and tuple(item.input_snapshot.get("load_case_ids", ())) == governing.load_case_ids:
                    item.governing = True

    def _apply_static_head_correction(
        self, project: VesselProject, result: OrchestratorResult
    ) -> None:
        """Statik kafa düzeltmesi uygula (§19).

        Sıvı yoğunluğu ve bileşen referans kotuna göre statik basınç hesaplanır
        ve MAWP sonuçlarına uygulanır.
        """
        dc = project.design_conditions
        fluid_density = dc.fluid_density_kg_m3

        if fluid_density <= 0:
            # K4: atlama sessiz olamaz — hangi sonucu etkilediği yazılır.
            for r in result.results:
                if r.calculation_type == "mawp":
                    r.add_assumption(
                        "Akışkan yoğunluğu girilmedi (0 kg/m³) — statik sıvı sütunu "
                        "basıncı MAWP'ye YANSITILMADI. Sıvı dolu işletmede alt "
                        "bileşenler bu değerden daha yüksek basınç görür."
                    )
            return

        mawp_results = [r for r in result.results if r.calculation_type == "mawp"]

        for mawp_r in mawp_results:
            if mawp_r.final_result is None:
                continue
            if mawp_r.status in (
                CalculationStatus.NOT_CALCULATED,
                CalculationStatus.BLOCKED_CODE_DATA,
                CalculationStatus.BLOCKED_MISSING_INPUT,
                CalculationStatus.OUT_OF_SCOPE,
            ):
                continue

            # Referans kota göre statik kafa hesabı
            ref_elev = mawp_r.reference_elevation_mm
            if ref_elev > 0:
                delta_p = static_head_pressure(fluid_density, ref_elev)
                mawp_r.add_intermediate(
                    "static_head_delta_P", delta_p, "MPa",
                    f"Statik kafa düzeltmesi (h={ref_elev} mm, ρ={fluid_density} kg/m³)"
                )
                # MAWP'yi statik kafa düşürür (alt bileşenler daha yüksek basınç görür)
                corrected_mawp = mawp_r.final_result - delta_p
                mawp_r.add_intermediate(
                    "MAWP_corrected", corrected_mawp, "MPa",
                    "Statik kafa düşülmüş MAWP"
                )
                if corrected_mawp <= 0:
                    mawp_r.add_warning(
                        f"Statik kafa ({delta_p:.4f} MPa) MAWP'yi ({mawp_r.final_result:.4f} MPa) "
                        f"afediyor. Bileşen yetersiz."
                    )
                    mawp_r.set_fail(0.0)
                else:
                    mawp_r.final_result = corrected_mawp

    def _pre_checks(self, project: VesselProject, result: OrchestratorResult) -> None:
        """A) Ön kontroller."""
        dc = project.design_conditions

        # None'a karşı güvenli sayısal değerler (boş alanlar 500'e yol açmasın)
        external_pressure = dc.external_pressure or 0
        operating_pressure = dc.operating_pressure or 0
        design_pressure = dc.design_pressure or 0

        # Basınç tutarlılığı
        if operating_pressure > design_pressure:
            r = CalculationResult(
                component_type="system",
                calculation_type="pressure_consistency",
                code=self.design_code.code_name,
                edition=self.design_code.code_edition,
            )
            r.set_review_required(
                "Operating pressure exceeds design pressure. "
                "This is unusual and requires engineer review."
            )
            result.add(r)

    def _check_materials(self, project: VesselProject, result: OrchestratorResult) -> None:
        """B) Malzeme kontrolü."""
        components = (
            [(x.section_id, "shell", x.material_id) for x in project.shell_sections]
            + [(x.head_id, "head", x.material_id) for x in project.heads]
            + [(x.cone_id, "cone", x.material_id) for x in project.cones]
            + [(x.tag, "nozzle", x.material_id) for x in project.nozzles]
            + [(x.support_id, "support", x.material_id) for x in project.supports]
        )
        for component_id, component_type, material_id in components:
            mat = project.get_material(material_id)
            if mat is None:
                r = CalculationResult(
                    component_id=component_id,
                    component_type=component_type,
                    calculation_type="material_check",
                    code=self.design_code.code_name,
                    edition=self.design_code.code_edition,
                )
                r.set_not_calculated(
                    f"Material '{material_id}' not found in project materials list."
                )
                result.add(r)


__all__ = ["CalculationOrchestrator", "OrchestratorResult"]

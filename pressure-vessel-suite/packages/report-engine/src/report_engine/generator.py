"""Rapor üretici — 23 bölümlük HTML rapor + PDF (kaynak §11).

K6 kuralı: Standart telifli metni kopyalanmaz.
K5 kuralı: Her hesap denetlenebilir — raporda ara değerler gösterilir.

Bölüm yapısı:
  1. Kapak → 2. Proje/revizyon → 3. Standartlar → 4. Tasarım temeli →
  5. Akışkan/koşullar → 6. PED kapsam → 7. Malzeme listesi → 8. Ana geometri →
  9. Gövde hesapları → 10. Bombe hesapları → 11. Nozul hesapları →
  12. Kaynak/NDT → 13. MAWP → 14. Test basıncı → 15. Ağırlık/hacim →
  16. Nozul schedule → 17. Kaynak haritası → 18. İsim plakası →
  19. ESR matrisi → 20. Uyarılar → 21. 2D → 22. 3D → 23. Onay/imza.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from domain.project import VesselProject
from calc_core.orchestrator import OrchestratorResult
from calc_core.volume_mass import VesselVolumeMassReport

from .traceability import TraceabilityBlock, build_traceability, compute_report_hash

try:
    from weasyprint import HTML as WeasyHTML

    WEASYPRINT_AVAILABLE = True
except Exception:
    # ImportError: paket kurulu değil.
    # OSError: paket kurulu ama native kütüphaneler (GTK/libgobject) yüklenemiyor
    # (ör. Windows'ta sistem bağımlılıkları eksik) → HTML-only path'e düş.
    WeasyHTML = None  # type: ignore
    WEASYPRINT_AVAILABLE = False


@dataclass
class ReportResult:
    """Rapor üretim sonucu."""

    html_content: str
    pdf_path: Optional[str] = None
    report_hash: str = ""
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


class ReportGenerator:
    """23 bölümlük basınçlı kap hesap raporu üretici.

    Kullanım:
        gen = ReportGenerator()
        result = gen.generate(project, orchestrator_result, volume_mass_report)
    """

    def generate(
        self,
        project: VesselProject,
        calc_result: OrchestratorResult,
        volume_mass: Optional[VesselVolumeMassReport] = None,
        traceability: Optional[TraceabilityBlock] = None,
        ped_result: Optional[Any] = None,
        compliance: Optional[Any] = None,
    ) -> ReportResult:
        """Tam HTML rapor üret.

        Args:
            project: VesselProject.
            calc_result: Hesap motoru sonuçları.
            volume_mass: Hacim/ağırlık raporu (opsiyonel).
            traceability: İzlenebilirlik bloğu (opsiyonel, otomatik üretilir).
            ped_result: PED sınıflandırma sonucu (ped_2014_68_eu.ClassificationResult,
                opsiyonel — verilirse 6. bölüm gerçek kategori/modülle dolar).
            compliance: ESR matrisi (compliance.ESRMatrix, opsiyonel — verilirse
                19. bölüm gerçek ESR maddeleriyle dolar).

        Returns:
            ReportResult (HTML + opsiyonel PDF).
        """
        if traceability is None:
            traceability = build_traceability(
                project_revision=project.revision,
                input_file_hash=project.input_file_hash or "",
            )

        sections = []
        sections.append(self._section_cover(project))
        sections.append(self._section_project_info(project))
        sections.append(self._section_standards(project))
        sections.append(self._section_design_basis(project))
        sections.append(self._section_fluid_conditions(project))
        sections.append(self._section_ped_scope(project, ped_result))
        sections.append(self._section_materials(project))
        sections.append(self._section_geometry(project))
        sections.append(self._section_shell_calculations(calc_result))
        sections.append(self._section_head_calculations(calc_result))
        sections.append(self._section_nozzle_calculations(calc_result))
        sections.append(self._section_welds(project))
        sections.append(self._section_mawp(calc_result))
        sections.append(self._section_hydrotest(calc_result))
        sections.append(self._section_weight_volume(volume_mass))
        sections.append(self._section_nozzle_schedule(project))
        sections.append(self._section_weld_map(project, calc_result))
        sections.append(self._section_nameplate(project))
        sections.append(self._section_esr_matrix(project, compliance))
        sections.append(self._section_warnings(calc_result))
        sections.append(self._section_2d_views())
        sections.append(self._section_3d_views())
        sections.append(self._section_approval())

        body = "\n".join(sections)
        traceability_html = traceability.to_html()

        html = self._wrap_html(project, body, traceability_html)

        # Rapor hash'i hesapla
        report_hash = compute_report_hash(html)
        traceability.report_hash = report_hash

        # Hash'i güncellenmiş HTML'i yeniden üret
        traceability_html = traceability.to_html()
        html = self._wrap_html(project, body, traceability_html)
        report_hash = compute_report_hash(html)

        # PDF üretimi (WeasyPrint varsa)
        pdf_path = None
        if WEASYPRINT_AVAILABLE:
            try:
                pdf_path = self._generate_pdf(html)
            except Exception as e:
                return ReportResult(
                    html_content=html,
                    report_hash=report_hash,
                    error=f"PDF üretim hatası: {e}",
                )

        return ReportResult(
            html_content=html,
            pdf_path=pdf_path,
            report_hash=report_hash,
        )

    def generate_html_only(
        self,
        project: VesselProject,
        calc_result: OrchestratorResult,
        volume_mass: Optional[VesselVolumeMassReport] = None,
    ) -> ReportResult:
        """Yalnızca HTML rapor üret (PDF yok)."""
        return self.generate(project, calc_result, volume_mass)

    def _generate_pdf(self, html_content: str) -> str:
        """WeasyPrint ile PDF üret."""
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("WeasyPrint kurulu değil. Yüklemek için: pip install weasyprint")

        weasy_doc = WeasyHTML(string=html_content)
        pdf_bytes = weasy_doc.write_pdf()

        # Geçici dosya (gerçek uygulamada dosya yolu parametre olarak gelir)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(pdf_bytes)
            return f.name

    def _wrap_html(self, project: VesselProject, body: str, traceability_html: str) -> str:
        """HTML şablonu sarmala."""
        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>Basınçlı Kap Hesap Raporu — {project.project_number}</title>
<style>
body {{ font-family: Arial, sans-serif; font-size: 11pt; margin: 20mm; color: #222; }}
h1 {{ font-size: 18pt; color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; }}
h2 {{ font-size: 14pt; color: #1a3a5c; margin-top: 24px; }}
h3 {{ font-size: 12pt; color: #333; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 10pt; }}
th {{ background: #f0f4f8; font-weight: bold; }}
.cover {{ text-align: center; margin-top: 80px; }}
.cover h1 {{ font-size: 24pt; border: none; }}
.traceability {{ background: #f9f9f9; margin-top: 30px; }}
.traceability th {{ background: #e8edf2; }}
.status-pass {{ color: green; font-weight: bold; }}
.status-fail {{ color: red; font-weight: bold; }}
.status-nc {{ color: orange; font-weight: bold; }}
.section {{ page-break-inside: avoid; margin-bottom: 16px; }}
.warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 8px; margin: 6px 0; }}
.footer {{ font-size: 9pt; color: #666; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 8px; }}
</style>
</head>
<body>
{body}
<div class="footer">
{traceability_html}
</div>
</body>
</html>"""

    # ── Bölüm üreticileri ─────────────────────────────────────────────────────

    def _section_cover(self, project: VesselProject) -> str:
        customer = project.customer or "—"
        return f"""
<div class="cover">
<h1>BASINÇLI KAP HESAP RAPORU</h1>
<h2>{project.project_name}</h2>
<p>Proje No: {project.project_number}</p>
<p>Revizyon: {project.revision}</p>
<p>Müşteri: {customer}</p>
<p>Hesap Standardı: {project.calculation_code.value} — {project.code_edition}</p>
</div>"""

    def _section_project_info(self, project: VesselProject) -> str:
        return f"""
<div class="section">
<h2>2. Proje ve Revizyon Bilgileri</h2>
<table>
<tr><th>Özellik</th><th>Değer</th></tr>
<tr><td>Proje Numarası</td><td>{project.project_number}</td></tr>
<tr><td>Proje Adı</td><td>{project.project_name}</td></tr>
<tr><td>Müşteri</td><td>{project.customer or '—'}</td></tr>
<tr><td>Revizyon</td><td>{project.revision}</td></tr>
<tr><td>Hesap Standardı</td><td>{project.calculation_code.value}</td></tr>
<tr><td>Standart Sürümü</td><td>{project.code_edition}</td></tr>
<tr><td>Birim Sistemi</td><td>{project.unit_system}</td></tr>
<tr><td>Yön</td><td>{project.orientation.value}</td></tr>
</table>
</div>"""

    def _section_standards(self, project: VesselProject) -> str:
        return f"""
<div class="section">
<h2>3. Kullanılan Standartlar ve Sürümleri</h2>
<table>
<tr><th>Standart</th><th>Sürüm</th></tr>
<tr><td>{project.calculation_code.value}</td><td>{project.code_edition}</td></tr>
<tr><td>ASME Section II (Malzeme)</td><td>2025</td></tr>
</table>
<p><em>Not: Standart metinleri telif hakları nedeniyle bu raporda yer almamaktadır (K6).
Yalnızca madde referansları ve formül sonuçları gösterilmiştir.</em></p>
</div>"""

    def _section_design_basis(self, project: VesselProject) -> str:
        dc = project.design_conditions
        return f"""
<div class="section">
<h2>4. Tasarım Temeli</h2>
<table>
<tr><th>Parametre</th><th>Değer</th></tr>
<tr><td>Çalışma Basıncı</td><td>{dc.operating_pressure} MPa</td></tr>
<tr><td>Tasarım Basıncı</td><td>{dc.design_pressure} MPa</td></tr>
<tr><td>Azami İzin Verilen Basınç (PS)</td><td>{dc.maximum_allowable_pressure_ps} MPa</td></tr>
<tr><td>Çalışma Sıcaklığı</td><td>{dc.operating_temperature} °C</td></tr>
<tr><td>Tasarım Sıcaklığı</td><td>{dc.design_temperature} °C</td></tr>
<tr><td>Asgari Tasarım Sıcaklığı</td><td>{dc.minimum_design_temperature} °C</td></tr>
<tr><td>İç Korozyon Payı</td><td>{dc.corrosion_allowance_internal} mm</td></tr>
<tr><td>Dış Korozyon Payı</td><td>{dc.corrosion_allowance_external} mm</td></tr>
<tr><td>Hidrotest Sıcaklığı</td><td>{dc.hydrotest_temperature} °C</td></tr>
</table>
</div>"""

    def _section_fluid_conditions(self, project: VesselProject) -> str:
        fluid = project.fluid
        if fluid:
            return f"""
<div class="section">
<h2>5. Akışkan ve Çalışma Koşulları</h2>
<table>
<tr><th>Parametre</th><th>Değer</th></tr>
<tr><td>Akışkan</td><td>{fluid.name}</td></tr>
<tr><td>Faz</td><td>{fluid.phase}</td></tr>
<tr><td>Grup</td><td>{fluid.group}</td></tr>
</table>
</div>"""
        return """
<div class="section">
<h2>5. Akışkan ve Çalışma Koşulları</h2>
<p><em>Akışkan bilgisi tanımlanmamış.</em></p>
</div>"""

    def _section_ped_scope(self, project: VesselProject, ped_result: Optional[Any] = None) -> str:
        if ped_result is None:
            return """
<div class="section">
<h2>6. PED Kapsam ve Kategori Hesabı</h2>
<p><em>PED sınıflandırması bu rapor için çalıştırılmadı (ASME VIII-1 rotası).
PED değerlendirmesi için projeyi PED sınıflandırma motoruyla çalıştırın.</em></p>
</div>"""

        def _val(x):
            return x.value if hasattr(x, "value") else x

        modules = ", ".join(_val(m) for m in ped_result.conformity_modules)
        return f"""
<div class="section">
<h2>6. PED Kapsam ve Kategori Hesabı</h2>
<table>
<tr><th>Parametre</th><th>Değer</th></tr>
<tr><td>PED Kapsamı</td><td>{'Evet' if ped_result.in_scope else 'Hayır — ' + ped_result.scope_reason}</td></tr>
<tr><td>Ekipman Türü</td><td>{_val(ped_result.equipment_type)}</td></tr>
<tr><td>Akışkan Fazı</td><td>{_val(ped_result.fluid_phase)}</td></tr>
<tr><td>Akışkan Grubu</td><td>{_val(ped_result.fluid_group)}</td></tr>
<tr><td>Sınıflandırma Tablosu</td><td>{_val(ped_result.classification_table)}</td></tr>
<tr><td>PS × V</td><td>{ped_result.ps_x_v:.1f} MPa·litre</td></tr>
<tr><td><strong>PED Kategorisi</strong></td><td><strong>{_val(ped_result.category)}</strong></td></tr>
<tr><td>Uygunluk Modülleri</td><td>{modules}</td></tr>
<tr><td>Onaylanmış Kuruluş</td><td>{_val(ped_result.notify_body_required)}</td></tr>
<tr><td>CE İşareti</td><td>{'Uygulanabilir' if ped_result.ce_marking_applicable else 'Uygulanamaz'}</td></tr>
</table>
</div>"""

    def _section_materials(self, project: VesselProject) -> str:
        rows = ""
        for mat in project.materials:
            rows += f"""
<tr><td>{mat.material_id}</td><td>{mat.material_designation}</td>
<td>{mat.product_form.value}</td><td>{mat.allowable_stress} MPa</td>
<td>{mat.yield_strength} MPa</td><td>{mat.tensile_strength} MPa</td>
<td>{mat.source_reference}</td></tr>"""
        return f"""
<div class="section">
<h2>7. Malzeme Listesi</h2>
<table>
<tr><th>ID</th><th>Malzeme</th><th>Ürün Formu</th><th>İzin Verilen Gerilme</th>
<th>Akma</th><th>Çekme</th><th>Kaynak</th></tr>
{rows}
</table>
</div>"""

    def _section_geometry(self, project: VesselProject) -> str:
        shell_rows = ""
        for s in project.shell_sections:
            shell_rows += f"""
<tr><td>{s.section_id}</td><td>{s.inside_diameter or '—'}</td>
<td>{s.outside_diameter or '—'}</td><td>{s.tangent_length}</td>
<td>{s.nominal_thickness}</td><td>{s.internal_corrosion_allowance}</td></tr>"""

        head_rows = ""
        for h in project.heads:
            head_rows += f"""
<tr><td>{h.head_id}</td><td>{h.type.value}</td><td>{h.inside_diameter}</td>
<td>{h.nominal_thickness}</td><td>{h.straight_flange_length}</td></tr>"""

        return f"""
<div class="section">
<h2>8. Ana Geometri</h2>
<h3>Gövde Kesitleri</h3>
<table>
<tr><th>ID</th><th>İç Çap (mm)</th><th>Dış Çap (mm)</th><th>Uzunluk (mm)</th>
<th>Kalınlık (mm)</th><th>Korozyon Payı (mm)</th></tr>
{shell_rows}
</table>
<h3>Bombeler</h3>
<table>
<tr><th>ID</th><th>Tip</th><th>İç Çap (mm)</th><th>Kalınlık (mm)</th><th>Düz Flanş (mm)</th></tr>
{head_rows}
</table>
</div>"""

    def _section_shell_calculations(self, calc_result: OrchestratorResult) -> str:
        rows = ""
        for r in calc_result.results:
            if r.component_type == "shell" and r.calculation_type == "thickness":
                status_class = self._status_class(r.status.value)
                rows += f"""
<tr><td>{r.component_id}</td><td>{r.clause_reference}</td>
<td>{r.final_result:.2f} {r.final_result_unit}</td>
<td>{r.allowable_limit:.2f} {r.allowable_limit_unit}</td>
<td>{r.utilization_ratio*100:.1f}%</td>
<td class="{status_class}">{r.status.value}</td></tr>"""
        return f"""
<div class="section">
<h2>9. Gövde Hesapları</h2>
<table>
<tr><th>Bileşen</th><th>Madde Ref.</th><th>Gerekli Kalınlık</th>
<th>Seçilen Kalınlık</th><th>Kullanım</th><th>Durum</th></tr>
{rows}
</table>
</div>"""

    def _section_head_calculations(self, calc_result: OrchestratorResult) -> str:
        rows = ""
        for r in calc_result.results:
            if r.component_type == "head" and r.calculation_type == "thickness":
                status_class = self._status_class(r.status.value)
                rows += f"""
<tr><td>{r.component_id}</td><td>{r.clause_reference}</td>
<td>{r.final_result:.2f} {r.final_result_unit}</td>
<td>{r.allowable_limit:.2f} {r.allowable_limit_unit}</td>
<td>{r.utilization_ratio*100:.1f}%</td>
<td class="{status_class}">{r.status.value}</td></tr>"""
        return f"""
<div class="section">
<h2>10. Bombe Hesapları</h2>
<table>
<tr><th>Bileşen</th><th>Madde Ref.</th><th>Gerekli Kalınlık</th>
<th>Seçilen Kalınlık</th><th>Kullanım</th><th>Durum</th></tr>
{rows}
</table>
</div>"""

    def _section_nozzle_calculations(self, calc_result: OrchestratorResult) -> str:
        blocks = ""
        for r in calc_result.results:
            if r.component_type != "nozzle" or r.calculation_type != "nozzle_reinforcement":
                continue
            status_class = self._status_class(r.status.value)
            # Ara değerlerden alan kalemlerini çıkar (UG-37/UG-40)
            iv = {x["name"]: x for x in r.intermediate_values}
            area_names = ["A1", "A2", "A3", "A4"]
            area_rows = ""
            for name in area_names:
                if name in iv:
                    item = iv[name]
                    area_rows += f"""
<tr><td>{name}</td><td>{item.get('description', '')}</td>
<td style="text-align:right">{item['value']:.1f} {item.get('unit', 'mm²')}</td></tr>"""
            required = iv.get("A_required", {}).get("value")
            total = iv.get("A_total", {}).get("value")
            util = f"{r.utilization_ratio*100:.1f}%" if r.utilization_ratio else "—"
            req_txt = f"{required:.1f} mm²" if required is not None else "—"
            tot_txt = f"{total:.1f} mm²" if total is not None else "—"
            warn = ("<div class='warning'>⚠ " + "; ".join(r.warnings) + "</div>") if r.warnings else ""
            blocks += f"""
<h3>Nozul {r.component_id} — Takviye Alan Analizi ({r.clause_reference})</h3>
<table>
<tr><th>Kalem</th><th>Açıklama</th><th>Alan</th></tr>
<tr><td><strong>Gerekli alan</strong></td><td>A_required = d × t_required</td>
<td style="text-align:right"><strong>{req_txt}</strong></td></tr>
{area_rows}
<tr><td><strong>Toplam mevcut</strong></td><td>A1+A2+A3+A4</td>
<td style="text-align:right"><strong>{tot_txt}</strong></td></tr>
<tr><td colspan="2">Kullanım / Sonuç</td>
<td style="text-align:right" class="{status_class}">{util} — {r.status.value}</td></tr>
</table>
{warn}"""
        if not blocks:
            blocks = "<p><em>Nozul tanımlanmamış.</em></p>"
        return f"""
<div class="section">
<h2>11. Nozul ve Açıklık Hesapları</h2>
{blocks}
</div>"""

    def _section_welds(self, project: VesselProject) -> str:
        rows = ""
        for w in project.welds:
            rows += f"""
<tr><td>{w.joint_id}</td><td>{w.joint_type}</td><td>{w.weld_category or '—'}</td>
<td>{w.joint_efficiency}</td><td>{w.nde_method or '—'}</td>
<td>{w.nde_extent or '—'}</td></tr>"""
        return f"""
<div class="section">
<h2>12. Kaynak ve NDT Özeti</h2>
<table>
<tr><th>ID</th><th>Tip</th><th>Kategori</th><th>Verim (E)</th><th>NDE Yöntemi</th><th>NDE Kapsamı</th></tr>
{rows}
</table>
</div>"""

    def _section_mawp(self, calc_result: OrchestratorResult) -> str:
        rows = ""
        for r in calc_result.results:
            if r.calculation_type == "mawp":
                rows += f"""
<tr><td>{r.component_id}</td><td>{r.component_type}</td>
<td>{r.clause_reference}</td><td>{r.final_result:.3f} {r.final_result_unit}</td></tr>"""
        global_mawp = calc_result.get_global_mawp()
        return f"""
<div class="section">
<h2>13. MAWP (Azami İzin Verilen Çalışma Basıncı)</h2>
<table>
<tr><th>Bileşen</th><th>Tip</th><th>Madde Ref.</th><th>MAWP (MPa)</th></tr>
{rows}
</table>
<p><strong>Global MAWP = {global_mawp:.3f} MPa</strong> (en düşük değer)</p>
</div>"""

    def _section_hydrotest(self, calc_result: OrchestratorResult) -> str:
        for r in calc_result.results:
            if r.calculation_type == "hydrotest":
                return f"""
<div class="section">
<h2>14. Hidrostatik Test Basıncı</h2>
<table>
<tr><th>Parametre</th><th>Değer</th></tr>
<tr><td>Referans</td><td>{r.clause_reference}</td></tr>
<tr><td>Tasarım Basıncı</td><td>{r.input_snapshot.get('P_design_MPa', '—')} MPa</td></tr>
<tr><td>Test Basıncı</td><td>{r.final_result:.3f} {r.final_result_unit}</td></tr>
</table>
</div>"""
        return """
<div class="section">
<h2>14. Hidrostatik Test Basıncı</h2>
<p><em>Hidrotest hesabı yapılamadı.</em></p>
</div>"""

    def _section_weight_volume(self, volume_mass: Optional[VesselVolumeMassReport]) -> str:
        if volume_mass is None:
            return """
<div class="section">
<h2>15. Ağırlık ve Hacim</h2>
<p><em>Hacim/ağırlık hesaplanmamış.</em></p>
</div>"""
        return f"""
<div class="section">
<h2>15. Ağırlık ve Hacim</h2>
<table>
<tr><th>Parametre</th><th>Değer</th></tr>
<tr><td>İç Hacim (Akışkan)</td><td>{volume_mass.total_inner_volume_liters:.1f} litre ({volume_mass.total_inner_volume_m3:.3f} m³)</td></tr>
<tr><td>Toplam Metal Hacmi</td><td>{volume_mass.total_metal_volume_mm3:.0f} mm³</td></tr>
<tr><td>Toplam Metal Ağırlığı</td><td>{volume_mass.total_metal_mass_kg:.1f} kg</td></tr>
</table>
<h3>Bileşen Bazında</h3>
<table>
<tr><th>Bileşen</th><th>Tip</th><th>İç Hacim (mm³)</th><th>Metal Hacmi (mm³)</th></tr>
{''.join(f"<tr><td>{v.component_id}</td><td>{v.component_type}</td><td>{v.inner_volume_mm3:.0f}</td><td>{v.metal_volume_mm3:.0f}</td></tr>" for v in volume_mass.volume_results)}
</table>
</div>"""

    def _section_nozzle_schedule(self, project: VesselProject) -> str:
        rows = ""
        for n in project.nozzles:
            rows += f"""
<tr><td>{n.tag}</td><td>{n.nozzle_type.value}</td><td>{n.axial_position} mm</td>
<td>{n.circumferential_angle}°</td><td>{n.outside_diameter} mm</td>
<td>{n.inside_diameter} mm</td><td>{n.neck_thickness} mm</td></tr>"""
        return f"""
<div class="section">
<h2>16. Nozul Schedule</h2>
<table>
<tr><th>Etiket</th><th>Tip</th><th>Eksenel Konum</th><th>Çevresel Açı</th>
<th>Dış Çap</th><th>İç Çap</th><th>Boyun Kalınlığı</th></tr>
{rows if rows else '<tr><td colspan="7"><em>Nozul tanımlanmamış.</em></td></tr>'}
</table>
</div>"""

    def _section_weld_map(
        self, project: VesselProject, calc_result: Optional[OrchestratorResult] = None
    ) -> str:
        # Kaynak doğrulama sonuçlarını calc_result'tan al
        weld_results = {}
        if calc_result is not None:
            for r in calc_result.results:
                if r.component_type == "weld" and r.calculation_type == "weld_validation":
                    weld_results[r.component_id] = r

        rows = ""
        for w in project.welds:
            vr = weld_results.get(w.joint_id)
            if vr is not None:
                status_class = self._status_class(vr.status.value)
                status_txt = f'<span class="{status_class}">{vr.status.value}</span>'
                note = "; ".join(vr.warnings) if vr.warnings else "—"
            else:
                status_txt = "—"
                note = "—"
            rows += f"""
<tr><td>{w.joint_id}</td><td>{w.joint_type}</td><td>{w.weld_category or '—'}</td>
<td>{w.joint_efficiency}</td><td>{w.nde_method or '—'} / {w.nde_extent or '—'}</td>
<td>{status_txt}</td><td>{note}</td></tr>"""
        if not rows:
            rows = '<tr><td colspan="7"><em>Kaynak tanımlanmamış.</em></td></tr>'
        return f"""
<div class="section">
<h2>17. Kaynak Haritası ve Doğrulama</h2>
<table>
<tr><th>Bağlantı</th><th>Tip</th><th>Kategori</th><th>Verim (E)</th>
<th>NDE (yöntem/kapsam)</th><th>Doğrulama</th><th>Not</th></tr>
{rows}
</table>
</div>"""

    def _section_nameplate(self, project: VesselProject) -> str:
        dc = project.design_conditions
        return f"""
<div class="section">
<h2>18. İsim Plakası Bilgileri</h2>
<table>
<tr><th>Alan</th><th>Değer</th></tr>
<tr><td>Tasarım Basıncı</td><td>{dc.design_pressure} MPa</td></tr>
<tr><td>Azami İzin Verilen Basınç (PS)</td><td>{dc.maximum_allowable_pressure_ps} MPa</td></tr>
<tr><td>Tasarım Sıcaklığı</td><td>{dc.design_temperature} °C</td></tr>
<tr><td>Hesap Standardı</td><td>{project.calculation_code.value} {project.code_edition}</td></tr>
</table>
</div>"""

    def _section_esr_matrix(self, project: VesselProject, compliance: Optional[Any] = None) -> str:
        if compliance is None:
            return """
<div class="section">
<h2>19. PED Temel Güvenlik Gereklilikleri Matrisi</h2>
<p><em>ESR matrisi bu rapor için sağlanmadı. PED/CE değerlendirmesi için compliance
modülünden bir ESR matrisi geçirin.</em></p>
</div>"""

        # ESRMatrix kendi HTML'ini üretir; özet sayaçlarla sarmala
        try:
            matrix_html = compliance.to_html()
            applied = compliance.get_applied_count()
            applicable = compliance.get_applicable_count()
            summary = f"<p>Uygulanan: <strong>{applied}/{applicable}</strong> uygulanabilir madde.</p>"
        except Exception:
            matrix_html = "<p><em>ESR matrisi render edilemedi.</em></p>"
            summary = ""
        return f"""
<div class="section">
<h2>19. PED Temel Güvenlik Gereklilikleri Matrisi</h2>
{summary}
{matrix_html}
</div>"""

    def _section_warnings(self, calc_result: OrchestratorResult) -> str:
        warnings_html = ""
        for r in calc_result.results:
            for w in r.warnings:
                warnings_html += f'<div class="warning">⚠ [{r.component_id or r.component_type}] {w}</div>\n'
            for a in r.assumptions:
                warnings_html += f'<div class="warning">ℹ [{r.component_id or r.component_type}] {a}</div>\n'

        if not warnings_html:
            warnings_html = "<p>Uyarı yok.</p>"

        return f"""
<div class="section">
<h2>20. Uyarılar ve Kapsam Dışı Kontroller</h2>
{warnings_html}
</div>"""

    def _section_2d_views(self) -> str:
        return """
<div class="section">
<h2>21. 2D Görünüşler</h2>
<p><em>2D görünüş diyagramları ileride eklenecektir.</em></p>
</div>"""

    def _section_3d_views(self) -> str:
        return """
<div class="section">
<h2>22. 3D Model Görünümleri</h2>
<p><em>3D model görüntüleri ileride eklenecektir.</em></p>
</div>"""

    def _section_approval(self) -> str:
        return """
<div class="section">
<h2>23. Hesap Onay ve İmza</h2>
<table>
<tr><th>Görev</th><th>İsim</th><th>Tarih</th><th>İmza</th></tr>
<tr><td>Hazırlayan</td><td></td><td></td><td></td></tr>
<tr><td>Kontrol Eden</td><td></td><td></td><td></td></tr>
<tr><td>Onaylayan</td><td></td><td></td><td></td></tr>
</table>
</div>"""

    def _status_class(self, status: str) -> str:
        if status == "PASS":
            return "status-pass"
        elif status == "FAIL":
            return "status-fail"
        elif status in ("NOT CALCULATED", "OUT OF SCOPE"):
            return "status-nc"
        return ""


__all__ = ["ReportGenerator", "ReportResult", "WEASYPRINT_AVAILABLE"]

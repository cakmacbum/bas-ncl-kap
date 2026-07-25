"""PED Classification Engine — 2014/68/EU Ek II sınıflandırma motoru.

PED (Pressure Equipment Directive) 2014/68/EU'ya göre basınçlı ekipman
sınıflandırması yapar. PS×V hesaplayarak Annex II tablolarından kategori
belirler, uygunluk modülü eşleştirmesi yapar ve onaylanmış kuruluş
gerekliliğini tespit eder.

K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı ve
sayısal eşikler kullanılır.

Referans: Directive 2014/68/EU, Annex II, Article 13, Article 14
"""

from __future__ import annotations

from typing import List, Optional

from ped_2014_68_eu.enums import (
    ConformityModule,
    EquipmentType,
    FluidGroupPED,
    FluidPhasePED,
    NotifyBodyRequired,
    PEDCategory,
    PEDClassificationTable,
)
from ped_2014_68_eu.models import (
    ClassificationInput,
    ClassificationResult,
    FluidClassification,
)
from ped_2014_68_eu.tables import get_classification_table


class PEDClassificationEngine:
    """PED 2014/68/EU sınıflandırma motoru.

    Girdileri alır, akışkan grubunu belirler, PS×V hesaplayarak
    Annex II tablosundan kategori seçer, modül eşleştirmesi yapar.

    Kullanım:
        engine = PEDClassificationEngine()
        result = engine.classify(input_data)
    """

    # ── Modül eşleştirmesi (PED Madde 14) ─────────────────────────────────────
    # SEP → CE yok
    # Kategori I → Modül A
    # Kategori II → Modül A2, D1, E1
    # Kategori III → Modül B+D, B+F, B+E, B+C2, H
    # Kategori IV → Modül B+D, B+F, G, H1

    _MODULE_MAP = {
        PEDCategory.SEP: {
            "modules": [ConformityModule.NONE],
            "description": "SEP (Sound Engineering Practice) — CE işaretleme uygulanmaz.",
            "nb_required": NotifyBodyRequired.NOT_REQUIRED,
            "ce_applicable": False,
        },
        PEDCategory.CATEGORY_I: {
            "modules": [ConformityModule.A],
            "description": "Kategori I — Modül A: İç üretim kontrolü.",
            "nb_required": NotifyBodyRequired.NOT_REQUIRED,
            "ce_applicable": True,
        },
        PEDCategory.CATEGORY_II: {
            "modules": [ConformityModule.A2, ConformityModule.D1, ConformityModule.E1],
            "description": (
                "Kategori II — Modül A2 (izlenen teslimatta deneme), "
                "D1 (üretim kalite güvencesi) veya E1 (ürün kalite güvencesi)."
            ),
            "nb_required": NotifyBodyRequired.OPTIONAL,
            "ce_applicable": True,
        },
        PEDCategory.CATEGORY_III: {
            "modules": [
                ConformityModule.B,  # B+D veya B+F veya B+E veya B+C2 veya H
                ConformityModule.H,
            ],
            "description": (
                "Kategori III — Modül B+D (AB tip incelemesi + üretim kalite güvencesi), "
                "B+F (ürün doğrulaması), B+E (ürün kalite güvencesi), "
                "B+C2 (izlenen teslimatta deneme) veya H (tam kalite güvencesi)."
            ),
            "nb_required": NotifyBodyRequired.REQUIRED,
            "ce_applicable": True,
        },
        PEDCategory.CATEGORY_IV: {
            "modules": [
                ConformityModule.B,  # B+D veya B+F veya G veya H1
                ConformityModule.G,
                ConformityModule.H1,
            ],
            "description": (
                "Kategori IV — Modül B+D (AB tip incelemesi + üretim kalite güvencesi), "
                "B+F (ürün doğrulaması), G (birim doğrulama) veya "
                "H1 (tam kalite güvencesi + tasarım incelemesi)."
            ),
            "nb_required": NotifyBodyRequired.REQUIRED,
            "ce_applicable": True,
        },
    }

    def classify(self, input_data: ClassificationInput) -> ClassificationResult:
        """PED sınıflandırması yap.

        Args:
            input_data: Sınıflandırma girdileri.

        Returns:
            ClassificationResult: Tam sınıflandırma sonucu.
        """
        result_intermediates = []

        # 1) Kapsam kontrolü
        in_scope, scope_reason = self._check_scope(input_data)
        if not in_scope:
            result_intermediates.append(("scope_check", "OUT_OF_SCOPE", scope_reason))

        # 2) Akışkan grubunu belirle
        fluid_group, fluid_phase, determining_fluid = self._determine_fluid_group(
            input_data.fluids, input_data.explicit_fluid_group
        )
        result_intermediates.append(("fluid_group", fluid_group.value, determining_fluid))
        result_intermediates.append(("fluid_phase", fluid_phase.value, "Baskın faz"))

        # 3) Sınıflandırma tablosunu seç
        table = get_classification_table(
            fluid_group=fluid_group,
            fluid_phase=fluid_phase,
            equipment_type=input_data.equipment_type,
        )
        result_intermediates.append(("classification_table", table.table_id.value, "Ek II tablosu"))

        # 4) PS×V hesabı
        ps_x_v = input_data.ps_mpa * input_data.volume_liters
        result_intermediates.append(("ps_mpa", input_data.ps_mpa, "Azami izin verilen basınç"))
        result_intermediates.append(("volume_liters", input_data.volume_liters, "Hacim"))
        result_intermediates.append(("ps_x_v", ps_x_v, "PS × V (MPa·litre)"))

        # 5) Kategori belirleme
        category = table.classify(input_data.ps_mpa, input_data.volume_liters)
        result_intermediates.append(("category", category.value, "PED kategorisi"))

        # 6) Modül eşleştirmesi
        module_info = self._MODULE_MAP[category]
        modules = self._get_modules_for_category(category, input_data)
        module_desc = module_info["description"]
        nb_required = module_info["nb_required"]
        ce_applicable = module_info["ce_applicable"]

        result_intermediates.append(("conformity_modules", [m.value for m in modules], "Uygunluk modülleri"))
        result_intermediates.append(("notify_body_required", nb_required.value, "Onaylanmış kuruluş"))

        # 7) Uyarılar
        warnings = []
        assumptions = []

        if input_data.is_assembly:
            assumptions.append(
                "Assembly (montaj) sınıflandırması: Her parça ayrı ayrı sınıflandırılmalı "
                "ve en yüksek kategori tüm montaj için geçerlidir (PED Madde 4(2))."
            )

        if input_data.is_fired and input_data.ps_mpa > 0.05:
            assumptions.append(
                "Ateşlemeli ekipman: Ek II Tablo 7/8 yerine Tablo 1/2 uygulanır "
                "(PED Ek II, 3. madde)."
            )

        if len(input_data.fluids) > 1:
            warnings.append(
                f"Çok akışkanlı sistem: {len(input_data.fluids)} akışkan tanımlı. "
                f"En yüksek kategoriyi oluşturan akışkan esas alındı: {determining_fluid}."
            )

        # 8) Sonuç oluştur
        result = ClassificationResult(
            in_scope=in_scope,
            scope_reason=scope_reason,
            equipment_type=input_data.equipment_type,
            is_assembly=input_data.is_assembly,
            fluid_group=fluid_group,
            fluid_phase=fluid_phase,
            determining_fluid=determining_fluid,
            classification_table=table.table_id,
            ps_mpa=input_data.ps_mpa,
            volume_liters=input_data.volume_liters,
            ps_x_v=ps_x_v,
            category=category,
            conformity_modules=modules,
            module_description=module_desc,
            notify_body_required=nb_required,
            ce_marking_applicable=ce_applicable,
            warnings=warnings,
            assumptions=assumptions,
            intermediate_values=[
                {"name": name, "value": val, "description": desc}
                for name, val, desc in result_intermediates
            ],
        )

        return result

    def _check_scope(self, input_data: ClassificationInput) -> tuple[bool, str]:
        """PED kapsam kontrolü.

        PED Madde 1(2) kapsam dışı durumları kontrol eder.

        Returns:
            (in_scope, reason)
        """
        # PS < 0.5 bar (0.05 MPa) → PED kapsamında değil
        if input_data.ps_mpa < 0.05:
            return False, (
                f"PS = {input_data.ps_mpa} MPa < 0.05 MPa (0.5 bar). "
                "PED 2014/68/EU kapsamı dışında (Madde 1(2)(a))."
            )

        return True, ""

    def _determine_fluid_group(
        self,
        fluids: List[FluidClassification],
        explicit_group: Optional[FluidGroupPED],
    ) -> tuple[FluidGroupPED, FluidPhasePED, str]:
        """Akışkan grubunu ve fazını belirle.

        Çok akışkanda en yüksek kategoriyi oluşturan esas alınır.
        (PED Ek II, 3. madde)

        Returns:
            (fluid_group, fluid_phase, determining_fluid_name)
        """
        if explicit_group:
            # Doğrudan belirtilmiş grup
            phase = fluids[0].phase if fluids else FluidPhasePED.GAS
            return explicit_group, phase, fluids[0].fluid_name if fluids else "Unknown"

        if not fluids:
            return FluidGroupPED.GROUP_2, FluidPhasePED.GAS, "Unknown"

        # Grup 1 akışkan var mı?
        group1_fluids = [f for f in fluids if f.is_group1]

        if group1_fluids:
            # Grup 1 akışkan fazını kullan
            # Gaz fazı baskın (gaz > sıvı kategorilendirmesi genellikle daha yüksek)
            gas_fluids = [f for f in group1_fluids if f.phase == FluidPhasePED.GAS]
            if gas_fluids:
                return FluidGroupPED.GROUP_1, FluidPhasePED.GAS, gas_fluids[0].fluid_name
            return FluidGroupPED.GROUP_1, group1_fluids[0].phase, group1_fluids[0].fluid_name

        # Hepsi Grup 2
        gas_fluids = [f for f in fluids if f.phase == FluidPhasePED.GAS]
        if gas_fluids:
            return FluidGroupPED.GROUP_2, FluidPhasePED.GAS, gas_fluids[0].fluid_name
        return FluidGroupPED.GROUP_2, fluids[0].phase, fluids[0].fluid_name

    def _get_modules_for_category(
        self,
        category: PEDCategory,
        input_data: ClassificationInput,
    ) -> List[ConformityModule]:
        """Kategoriye göre uygunluk modüllerini döndür.

        Kategori III ve IV için birden fazla seçenek vardır;
        varsayılan olarak en yaygın olanı döndürür.

        Args:
            category: PED kategorisi.
            input_data: Sınıflandırma girdileri.

        Returns:
            Uygunluk modülleri listesi.
        """
        if category == PEDCategory.SEP:
            return [ConformityModule.NONE]

        if category == PEDCategory.CATEGORY_I:
            return [ConformityModule.A]

        if category == PEDCategory.CATEGORY_II:
            # Varsayılan: A2 (en basit)
            return [ConformityModule.A2]

        if category == PEDCategory.CATEGORY_III:
            # Varsayılan: B+D (en yaygın)
            return [ConformityModule.B, ConformityModule.D]

        if category == PEDCategory.CATEGORY_IV:
            # Varsayılan: G (birim doğrulama) veya H1
            return [ConformityModule.G]

        return [ConformityModule.NONE]


__all__ = ["PEDClassificationEngine"]

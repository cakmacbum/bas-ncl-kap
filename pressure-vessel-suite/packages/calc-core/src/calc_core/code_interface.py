"""DesignCode soyut arayüzü (kaynak §7).

Her standart (ASME VIII-1, EN 13445) bu arayüzü uygular.
K7 kuralı: Domain modelinden bağımsız; hesap kuralları burada tanımlanır.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from calc_core.result import CalculationResult

if TYPE_CHECKING:
    from domain.project import VesselProject


class DesignCode(ABC):
    """Hesap standardı arayüzü.

    Her code plugin bu sınıfı genişletir ve metodları uygular.
    """

    @property
    @abstractmethod
    def code_name(self) -> str:
        """Standart adı (ör. 'ASME VIII-1')."""

    @property
    @abstractmethod
    def code_edition(self) -> str:
        """Standart sürümü (ör. '2025')."""

    @abstractmethod
    def calculate_shell_thickness(self, input_data: dict) -> CalculationResult:
        """Silindirik gövde iç basınç et kalınlığı hesabı."""

    @abstractmethod
    def calculate_head_thickness(self, input_data: dict) -> CalculationResult:
        """Bombe et kalınlığı hesabı."""

    @abstractmethod
    def calculate_mawp(self, input_data: dict) -> CalculationResult:
        """MAWP hesabı (her bileşen için ayrı → global min)."""

    @abstractmethod
    def calculate_hydrotest_pressure(self, input_data: dict) -> CalculationResult:
        """Hidrostatik test basıncı hesabı."""

    def calculate_nozzle(self, input_data: dict) -> CalculationResult:
        """Nozul takviye hesabı (opsiyonel — varsayılan NOT_CALCULATED)."""
        result = CalculationResult(
            component_type="nozzle",
            calculation_type="nozzle_reinforcement",
            code=self.code_name,
            edition=self.code_edition,
        )
        result.set_not_calculated(
            "Nozzle reinforcement calculation has not been implemented yet. "
            "This result must not be used for fabrication."
        )
        return result

    def validate_weld(self, input_data: dict) -> CalculationResult:
        """Kaynak doğrulama (opsiyonel — varsayılan NOT_CALCULATED)."""
        result = CalculationResult(
            component_type="weld",
            calculation_type="weld_validation",
            code=self.code_name,
            edition=self.code_edition,
        )
        result.set_not_calculated(
            "Weld validation has not been implemented yet."
        )
        return result

    def validate_welds(self, project: "VesselProject") -> List[CalculationResult]:
        """Projedeki tüm kaynakları doğrula (opsiyonel — varsayılan boş liste).

        Standart eklentisi bunu, kendi `welds` bağımlılığıyla uygular.
        calc-core burada nozzles/welds import etmez (döngü önleme).
        """
        return []

    def check_nozzle_clashes(self, project: "VesselProject") -> List[CalculationResult]:
        """Nozul çakışma/geometri kontrolleri (opsiyonel — varsayılan boş liste).

        Standart eklentisi bunu, kendi `nozzles` bağımlılığıyla uygular.
        """
        return []

    def check_external_pressure(self, project: "VesselProject") -> List[CalculationResult]:
        """Dış basınç/vakum stabilite kontrolü (opsiyonel — varsayılan boş liste).

        Standart eklentisi bunu, kendi `external-pressure` bağımlılığıyla uygular.
        """
        return []

    def check_mdmt(self, project: "VesselProject") -> List[CalculationResult]:
        """MDMT kontrolü (opsiyonel — varsayılan boş liste).

        Standart eklentisi bunu, kendi `mdmt` bağımlılığıyla uygular.
        MDMT eğri grubu standarda özgüdür (ASME'de UCS-66), bu yüzden
        orkestratör değil standart eklentisi sahiplenir.
        """
        return []

    def check_supports(self, project: "VesselProject") -> List[CalculationResult]:
        """Destek (saddle/skirt/leg) kontrolü (opsiyonel — varsayılan boş liste).

        Standart eklentisi bunu, kendi `supports` bağımlılığıyla uygular.
        """
        return []

    def calculate_pneumatic_test_pressure(self, input_data: dict) -> CalculationResult:
        """Pnömatik test basıncı hesabı (opsiyonel — varsayılan NOT_CALCULATED)."""
        result = CalculationResult(
            component_type="system",
            calculation_type="pneumatic_test",
            code=self.code_name,
            edition=self.code_edition,
        )
        result.set_not_calculated(
            "Pneumatic test calculation has not been implemented yet."
        )
        return result


__all__ = ["DesignCode"]

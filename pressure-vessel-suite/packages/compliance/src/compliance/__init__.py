"""Compliance modülü — PED uygunluk dokümantasyonu.

ESR matrisi, risk/tehlike analizi, EU DoC taslağı, isim plakası bilgileri,
kullanım/güvenlik talimatı şablonu, teknik dosya indeksi.

Referans: PED 2014/68/EU, Annex I (ESR), Article 14 (DoC), Article 16 (Nameplate)
"""

from compliance.esr_matrix import ESRMatrix, ESRItem
from compliance.declaration import DeclarationOfConformity, NameplateInfo
from compliance.technical_file import TechnicalFileIndex, TechnicalFileItem
from compliance.risk_analysis import RiskAnalysis, RiskItem

__all__ = [
    "ESRMatrix",
    "ESRItem",
    "DeclarationOfConformity",
    "NameplateInfo",
    "TechnicalFileIndex",
    "TechnicalFileItem",
    "RiskAnalysis",
    "RiskItem",
]

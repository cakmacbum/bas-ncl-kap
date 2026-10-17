from tools.campaign.aggregate import LABELS, normalize_verdict


def test_verdict_normalization_handles_spaces_and_mojibake():
    assert normalize_verdict("KAPSAM_DI\x9eI") == "KAPSAM_DIŞI"
    assert normalize_verdict("KAPSAM DIŞI") == "KAPSAM_DIŞI"
    assert normalize_verdict("FORMÜLASYON FARKI") == "FORMÜLASYON_FARKI"
    assert normalize_verdict("DOĞRULANDI") == "DOĞRULANDI"
    assert set(LABELS) == {"DOĞRULANDI", "FORMÜLASYON_FARKI", "SAPMA", "TEK_KAYNAK", "KAYNAK_BEKLİYOR", "KAPSAM_DIŞI"}

"""Hayalet özellik testleri — "yazıldı ama çalışmıyor" sınıfını yakalar.

Neden var: dört doğrulama turunda bulunan yedi sapmanın tamamı, formülde değil
formülün **çevresinde**ydi. Sonuncusu (V-19) hiç çağrılmayan bir fonksiyondu.
Ardından yapılan envanterde üç paket daha (mdmt, flanges, supports) hesap
hattına hiç bağlı olmadığı hâlde kasada ✅ işaretli çıktı.

Bu dosya o sınıfın bir daha sessizce girmesini engeller. Sayısal doğruluk
sınamaz — **iddia ile gerçek arasındaki farkı** sınar.

Üç kural:
  1. Arayüzün beklediği her sonuç tipini bir yerin üretebiliyor olması gerekir.
  2. Üretilen her sonuç tipinin ya arayüzde gösteriliyor ya da bilinçli
     gösterilmediğinin kayıtlı olması gerekir.
  3. Her hesap paketi ya hesap hattına bağlı, ya da `limitations.md`'de
     "bağlı değil" olarak açıkça listeli olmalıdır.
"""

import re
from pathlib import Path

import pytest

SUITE_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES = SUITE_ROOT / "packages"
PAGES_TSX = SUITE_ROOT / "apps" / "web-ui" / "src" / "pages.tsx"
LIMITATIONS = SUITE_ROOT / "docs" / "limitations.md"


def _produced_types() -> set[str]:
    """Kod tabanının üretebildiği tüm `calculation_type` değerleri."""
    found: set[str] = set()
    for py in PACKAGES.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        found.update(re.findall(r'calculation_type=["\']([a-z_]+)["\']', text))
    return found


def _ui_expected_types() -> set[str]:
    """Arayüzün `byType("...")` ile beklediği sonuç tipleri."""
    text = PAGES_TSX.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r'byType\(["\']([a-z_]+)["\']\)', text))


# Bilinçli olarak arayüzde gösterilmeyen tipler ve sebepleri.
# Buraya bir tip eklemek bir KARARDIR — gerekçesiz eklenmemeli.
UI_DE_GOSTERILMEYENLER = {
    "material_check": "ön kontrol; hata varsa zaten diğer sonuçlar bloke olur",
    "pressure_consistency": "ön kontrol; aynı gerekçe",
    "fea_analysis": "FEA laboratuvarı offline araçtır, arayüzde gösterilmez (Faz 2 kararı)",
    "fea_material_data_check": "aynı gerekçe",
    "flange_stress": "flanş modülü hesap hattına bağlı değil — limitations.md B-11",
}


def test_ui_beklenen_her_tip_uretilebiliyor():
    """Arayüzde gösterilen ama hiçbir yerin üretmediği bölüm olmamalı.

    Böyle bir bölüm kullanıcıya "bu kontrol yapıldı ve sorun yok" izlenimi verir;
    gerçekte hiç yapılmamıştır. Yanlış ✅, olmayan özellikten zararlıdır.
    """
    produced = _produced_types()
    expected = _ui_expected_types()
    ghosts = expected - produced
    assert not ghosts, (
        f"Arayüz şu sonuç tiplerini bekliyor ama hiçbir paket üretmiyor: {sorted(ghosts)}. "
        f"Ya üretimi bağla ya da bölümü kaldır/not göster."
    )


def test_uretilen_her_tip_ya_gosteriliyor_ya_kayitli():
    """Üretilip de arayüzde hiç görünmeyen sonuç tipi olmamalı.

    Bu, ters yöndeki hayalet: hesap yapılıyor, sonuç üretiliyor, kullanıcı
    hiç görmüyor. Gösterilmeyecekse sebebi `UI_DE_GOSTERILMEYENLER`'de yazılı olmalı.
    """
    produced = _produced_types()
    shown = _ui_expected_types()
    invisible = produced - shown - set(UI_DE_GOSTERILMEYENLER)
    assert not invisible, (
        f"Şu sonuç tipleri üretiliyor ama arayüzde hiç gösterilmiyor: {sorted(invisible)}. "
        f"Ya arayüze ekle ya da UI_DE_GOSTERILMEYENLER'e gerekçesiyle yaz."
    )


# Hesap yapan paketler. Her biri ya hesap hattından çağrılmalı, ya da
# limitations.md'de "bağlı değil" diye geçmeli.
HESAP_PAKETLERI = [
    "external_pressure",
    "flanges",
    "mdmt",
    "nozzles",
    "supports",
    "welds",
]

# Hesap hattı: orkestratör + standart eklentileri.
HESAP_HATTI = [
    PACKAGES / "calc-core" / "src" / "calc_core",
    PACKAGES / "code-asme-viii-1" / "src" / "code_asme_viii_1",
    PACKAGES / "code-en-13445" / "src" / "code_en_13445",
]


def _hesap_hattinda_cagriliyor_mu(paket: str) -> bool:
    pattern = re.compile(rf"\b(?:from|import)\s+{re.escape(paket)}\b")
    for root in HESAP_HATTI:
        for py in root.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            if pattern.search(py.read_text(encoding="utf-8", errors="replace")):
                return True
    return False


@pytest.mark.parametrize("paket", HESAP_PAKETLERI)
def test_her_hesap_paketi_ya_bagli_ya_kayitli(paket):
    """Ölü paket testi.

    `supports` ve `mdmt` tam olarak böyle kaçmıştı: yazılmış, testleri geçiyor,
    kasada ✅ — ama hiçbir yerden çağrılmıyor. Bir paket bağlı değilse bu bir
    tercih olabilir; ama **yazılı** bir tercih olmalı (K4).
    """
    if _hesap_hattinda_cagriliyor_mu(paket):
        return

    # Yalnızca paket adının dosyada geçmesi YETMEZ — bu testi ilk yazdığımda
    # `flanges` "✅ Faz 5" satırı sayesinde geçiyordu, yani yakalamak istediğim
    # yanlış iddianın kendisi testi geçiriyordu. Bu yüzden açık, makine-okunur
    # bir işaret aranıyor.
    limitations = LIMITATIONS.read_text(encoding="utf-8", errors="replace")
    marker = f"BAGLI DEGIL: {paket}"
    assert marker in limitations, (
        f"`{paket}` paketi hesap hattından çağrılmıyor ve docs/limitations.md'de "
        f"`{marker}` işareti yok. Ya bağla ya da bu işaretle gerekçesini kaydet."
    )

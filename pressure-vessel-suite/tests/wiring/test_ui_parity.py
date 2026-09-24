"""Arayüz eşdeğerliği testleri — "kullanıcı tetikleyebiliyor mu?" sınıfını yakalar.

Neden var: `test_no_ghost_features.py` şu soruyu sorar — "orkestratörden çağrılıyor
mu?" `external_pressure` ve `supports` paketleri o testi geçiyordu (ikisi de
`design_code.py`'den import ediliyordu) ama kullanıcının onları tetikleyecek bir
form alanı yoktu: `strain_factor_A`/`allowable_stress_B` kodda `0.0` sabitti,
`supports` listesi arayüzde hep boştu. Faz 4 bu ikisini açtı; bu dosya aynı
sınıfın bir daha sessizce girmesini engeller.

Üç kural:
  1. `ResultGroup`'un her çağrısında `emptyNote` bulunur (boş grup asla `null`
     dönmemeli — K4: eksiklik gizlenmez).
  2. Domain'in hesabı etkileyen her alanı arayüzde ya vardır, ya da gerekçesiyle
     `ARAYUZDE_YOK` sözlüğünde kayıtlıdır.
  3. `CalcPayload`'ın ürettiği her alan arayüzde ya render edilir, ya da
     gerekçesiyle kayıtlıdır.
"""

import re
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES = SUITE_ROOT / "packages"
WEB_UI_SRC = SUITE_ROOT / "apps" / "web-ui" / "src"
PAGES_TSX = WEB_UI_SRC / "pages.tsx"
COMPONENTS_TSX = WEB_UI_SRC / "components.tsx"
TYPES_TS = WEB_UI_SRC / "types.ts"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_her_resultgroup_emptynote_tasiyor():
    """Boş bir `ResultGroup` sessizce kaybolamaz.

    `pages.tsx:596-598`'deki yorum bunun neden gerekli olduğunu zaten yazıyor:
    kullanıcı "kontrol yapıldı ve geçti" ile "kontrol hiç yapılmadı"yı ayırt
    edebilmeli. `emptyNote` olmayan bir çağrı, boş grubu `null` döndürür ve
    kullanıcı o bölümün var olduğunu bile bilmez.
    """
    text = _read(PAGES_TSX)
    # Her <ResultGroup ...> ... /> bloğunu (tek satır veya çok satır) yakala.
    calls = re.findall(r"<ResultGroup\b.*?/>", text, flags=re.DOTALL)
    assert calls, "pages.tsx içinde hiç ResultGroup çağrısı bulunamadı — dosya taşındı mı?"
    missing = [c for c in calls if "emptyNote=" not in c]
    assert not missing, (
        f"{len(missing)} ResultGroup çağrısında emptyNote yok. Her çağrı, grup "
        f"boşken kullanıcıya neden boş olduğunu söylemeli:\n"
        + "\n---\n".join(missing)
    )


def test_calculation_code_dropdown_exposes_asme_and_en():
    """Kullanıcı desteklenen iki hesap motorunu UI'dan seçebilir."""
    text = _read(PAGES_TSX)
    assert '{ value: "ASME VIII-1", label: "ASME VIII Division 1" }' in text
    assert '{ value: "EN 13445", label: "EN 13445" }' in text


# Domain alanları arayüzde bilinçli olarak yok. Buraya bir alan eklemek bir
# KARARDIR — gerekçesiz eklenmemeli. (Aynı desen: test_no_ghost_features.py
# içindeki UI_DE_GOSTERILMEYENLER.)
ARAYUZDE_YOK = {
    "Flange.flange_id": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.rating_standard": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.thickness": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.hub_length": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.hub_small_thickness": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.bolt_count": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.bolt_area": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.bolt_allowable_stress": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.gasket_m": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Flange.gasket_y": "Flange domain UI deferred until complete Appendix 2 wiring",
    "Head.crown_depth": "Head geometry UI field deferred to B-06 geometry completion",
    "Head.flat_z_factor": "Head geometry UI field deferred to B-06 geometry completion",
    "Support.anchor_bolt_count": "Phase C anchor input UI deferred",
    "Support.anchor_bolt_diameter_mm": "Phase C anchor input UI deferred",
    "Support.anchor_shear_allowable_N": "Phase C anchor input UI deferred",
    "Support.anchor_tension_allowable_N": "Phase C anchor input UI deferred",
    "Support.lateral_load_N": "Phase C anchor input UI deferred",
    # Koni: domain + hesap var (orchestrator.py kalınlık ve MAWP hesaplıyor),
    # arayüzde form yok. Kapsam genişletmesi — Faz 4'ün "kapsam dışı" listesi.
    "Cone.cone_id": "koni formu yok — Faz 4 kapsamı dışında, docs/limitations.md",
    "Cone.large_diameter": "aynı gerekçe",
    "Cone.small_diameter": "aynı gerekçe",
    "Cone.half_apex_angle": "aynı gerekçe",
    "Cone.length": "aynı gerekçe",
    "Cone.nominal_thickness": "aynı gerekçe",
    "Cone.material_id": "aynı gerekçe",
    "Cone.weld_joint_id": "aynı gerekçe",
    "Cone.internal_corrosion_allowance": "aynı gerekçe",
    "Cone.mill_tolerance": "aynı gerekçe",
    # Head.external_corrosion_allowance: ShellSection'da karşılığı forma
    # bağlıyken Head'de unutulmuş — bu test bunu ilk kez ortaya çıkardı.
    # Küçük ama bilinçli bir dışta bırakma; forma eklenmedi.
    "Head.external_corrosion_allowance": "forma eklenmedi — bombe dış korozyonu V1'de 0 varsayılır",
    # Çoklu gövde kesiti / yük durumları: Faz 4 kapsamı dışı (bkz. plan).
    "VesselProject.load_cases": "15 zorunlu şablon, arayüz yok — Faz 4 kapsamı dışında",
    "VesselProject.load_combinations": "aynı gerekçe",
    "VesselProject.cones": "koni formu yok (yukarı bakınız)",
}


def _domain_fields(py_file: Path) -> dict[str, set[str]]:
    """Bir domain dosyasındaki her Pydantic sınıfının alan adlarını çıkar.

    Basit satır-tabanlı ayrıştırma: `class X(BaseModel):` başlığından bir
    sonraki `class` veya dosya sonuna kadar, girinti 4 olan `ad: Tip = Field(`
    veya `ad: Tip` satırlarını alan sayar. `model_config`, `@` dekoratörleri,
    method tanımları (`def `) ve docstring içi satırlar ("Tip: ..." gibi
    dokstring metni yanlışlıkla alan sanılmasın diye) hariç tutulur.
    """
    text = _read(py_file)
    fields: dict[str, set[str]] = {}
    current_class = None
    in_docstring = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('"""'):
            # Tek satırda açılıp kapanan docstring hariç, aç/kapa durumunu çevir.
            if stripped.count('"""') == 1:
                in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        cls_match = re.match(r"class (\w+)\(", line)
        if cls_match:
            current_class = cls_match.group(1)
            fields[current_class] = set()
            continue
        if current_class is None:
            continue
        field_match = re.match(r"    (\w+): ", line)
        if field_match and not line.strip().startswith("def "):
            name = field_match.group(1)
            if name != "model_config":
                fields[current_class].add(name)
    return fields


def test_domain_alanlari_arayuzde_ya_var_ya_kayitli():
    """Hesabı etkileyen her domain alanı, kullanıcı tarafından ya girilebilir
    ya da bilinçli olarak dışta bırakıldığı kayıtlıdır.

    `external_pressure`/`vacuum_condition` (form yoktu) ve `strain_factor_A`/
    `allowable_stress_B` (kodda 0.0 sabitti) tam olarak bu testin yakalamak
    istediği sınıftandı — hesap var, kapı yoktu.
    """
    types_text = _read(TYPES_TS)

    all_fields = {}
    for py_file in [
        PACKAGES / "domain" / "src" / "domain" / "conditions.py",
        PACKAGES / "domain" / "src" / "domain" / "geometry.py",
    ]:
        for cls, names in _domain_fields(py_file).items():
            for name in names:
                all_fields[f"{cls}.{name}"] = name

    missing = []
    for qualified, name in sorted(all_fields.items()):
        if qualified in ARAYUZDE_YOK:
            continue
        # Alan adı types.ts'te bir yerde (herhangi bir interface'te) geçmeli.
        if not re.search(rf"\b{re.escape(name)}\b", types_text):
            missing.append(qualified)

    assert not missing, (
        f"Şu domain alanları types.ts'te hiç geçmiyor ve ARAYUZDE_YOK'ta kayıtlı "
        f"değil: {missing}. Ya arayüze bir form alanı ekle, ya da gerekçesiyle "
        f"ARAYUZDE_YOK'a yaz."
    )


# CalcPayload alanları arayüzde bilinçli olarak render edilmiyor.
CALCPAYLOAD_GOSTERILMEYEN = {
    "project_number": "proje meta bilgisi — Yeni Proje adımında zaten girildi/gösterildi, hesap sonucu değil",
    "code": "statik olarak ResultsPage başlığında gösteriliyor, calc.code olarak değil",
    "edition": "aynı gerekçe",
}


def test_calcpayload_alanlari_render_ediliyor():
    """`CalcPayload`'ın her alanı arayüzde bir yere düşmeli.

    `errors` tam olarak bu kuralı ihlal ediyordu: tipte tanımlıydı, hiçbir
    yerde okunmuyordu. Bir orkestratör istisnası ekranda hiç görünmezdi.
    """
    types_text = _read(TYPES_TS)
    m = re.search(r"export interface CalcPayload \{(.*?)\n\}", types_text, re.DOTALL)
    assert m, "types.ts içinde CalcPayload arayüzü bulunamadı."
    # Yalnız üst seviye alanlar (2 boşluk girinti) — `volume_mass: { ... }` gibi
    # iç içe obje tanımlarının kendi alanları (4 boşluk girinti) burada
    # sayılmaz; onlar `calc.volume_mass.<alan>` olarak zaten erişiliyor ve
    # üst seviye `volume_mass` kontrolü bunu kapsar.
    field_names = re.findall(r"^  (\w+)[?:]", m.group(1), re.MULTILINE)

    pages_text = _read(PAGES_TSX)
    components_text = _read(COMPONENTS_TSX)
    haystack = pages_text + components_text

    missing = []
    for name in field_names:
        if name in CALCPAYLOAD_GOSTERILMEYEN:
            continue
        # `calc.<alan>` veya opsiyonel zincirleme `calc?.<alan>` — ikisi de geçerli.
        if not re.search(rf"\bcalc\??\.{re.escape(name)}\b", haystack):
            missing.append(name)

    assert not missing, (
        f"CalcPayload alanları {missing} pages.tsx/components.tsx içinde "
        f"`calc.<alan>` olarak hiç kullanılmıyor. Ya render et, ya da "
        f"gerekçesiyle CALCPAYLOAD_GOSTERILMEYEN'e yaz."
    )

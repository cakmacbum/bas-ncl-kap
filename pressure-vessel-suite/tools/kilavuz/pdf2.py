"""docs/kilavuz/kilavuz2.html -> Vessela-Baslangic-Kilavuzu.pdf (Edge/Chromium, A4)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

kok = Path(__file__).resolve().parents[2] / "docs" / "kilavuz2"
html, pdf = kok / "kilavuz2.html", kok / "Vessela-Baslangic-Kilavuzu.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    s = b.new_page()
    s.goto(html.as_uri(), wait_until="networkidle")
    s.pdf(path=str(pdf), format="A4", print_background=True,
          margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
          display_header_footer=True, header_template="<span></span>",
          footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#888">'
                          'Vessela — Başlangıç Kılavuzu · <span class="pageNumber"></span>/<span class="totalPages"></span></div>')
    b.close()
print(pdf)
try:
    from pypdf import PdfReader
    print("sayfa:", len(PdfReader(str(pdf)).pages))
except Exception as e:
    print("sayfa sayisi okunamadi", e)

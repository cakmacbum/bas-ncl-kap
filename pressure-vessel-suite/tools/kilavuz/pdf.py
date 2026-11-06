"""docs/kilavuz/kilavuz.html -> Vessela-Kullanim-ve-Hesap-Kilavuzu.pdf (Edge/Chromium, A4)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

kok = Path(__file__).resolve().parents[2] / "docs" / "kilavuz"
html, pdf = kok / "kilavuz.html", kok / "Vessela-Kullanim-ve-Hesap-Kilavuzu.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    s = b.new_page()
    s.goto(html.as_uri(), wait_until="networkidle")
    s.pdf(path=str(pdf), format="A4", print_background=True,
          margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
          display_header_footer=True, header_template="<span></span>",
          footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#888">'
                          'Vessela — Kullanım ve Hesap Kılavuzu · <span class="pageNumber"></span>/<span class="totalPages"></span></div>')
    b.close()
print(pdf)

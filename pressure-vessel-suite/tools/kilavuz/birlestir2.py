"""parca-D2/G1/G2/G3 -> kilavuz2.html (h2'lerden otomatik icindekiler)."""
import re
from pathlib import Path
k = Path(__file__).resolve().parents[2] / "docs" / "kilavuz2"
CSS = """
@page{size:A4;margin:16mm 14mm}
*{box-sizing:border-box}
body{font-family:'Segoe UI',Calibri,Arial,sans-serif;font-size:10.5pt;line-height:1.5;color:#222;max-width:182mm;margin:0 auto;padding:0 4mm}
h1,h2,h3,h4{color:#12304d;line-height:1.25}
h1{font-size:26pt}
h2{font-size:17pt;border-bottom:2px solid #12304d;padding-bottom:3px;margin-top:1.4em;break-after:avoid}
h3{font-size:13pt;margin-top:1.1em;break-after:avoid}h4{font-size:11pt;break-after:avoid}
p{margin:.5em 0;orphans:3;widows:3}
img{max-width:100%;height:auto;display:block;margin:.6em auto;break-inside:avoid;max-height:230mm;object-fit:contain;border:1px solid #cfd6de}
figure.uzun img{max-height:230mm;width:auto;max-width:100%}
figure{margin:.6em 0;break-inside:avoid}figcaption{font-size:9pt;color:#555;text-align:center}
table{border-collapse:collapse;width:100%;margin:.6em 0;font-size:9.5pt}
th,td{border:1px solid #b9c2cc;padding:4px 6px;vertical-align:top;text-align:left}
th{background:#e8eef4;color:#12304d}tr{break-inside:avoid}thead{display:table-header-group}
code,pre{font-family:Consolas,monospace;font-size:9.5pt;background:#f2f4f6}
.ipucu,.uyari{margin:.8em 0;padding:8px 12px;border-left:5px solid;border-radius:3px;break-inside:avoid}
.ipucu{background:#eaf6ee;border-color:#2e8b57}
.uyari{background:#fdf1e3;border-color:#d9822b}
.kapak{min-height:240mm;display:flex;flex-direction:column;justify-content:center;break-after:page}
.kapak .alt{font-size:15pt;color:#456}.kapak .tarih{color:#666;margin:1em 0 2em}
.nasil{border:2px solid #12304d;border-radius:6px;padding:10px 16px;background:#f4f7fa}
.ic{break-after:page}.ic ol{line-height:1.9;list-style:none;padding-left:0}.ic a{color:#12304d;text-decoration:none}
section.parca{break-before:page}
.son{break-before:page;text-align:center;padding-top:60mm}
"""
def idle(html, pre):
    n=[0]
    def f(m):
        n[0]+=1; return f'<h2 id="{pre}-{n[0]}">'
    return re.sub(r'<h2>', f, html)
parts=[]; toc=[]
for p in ["D2","G1","G2","G3"]:
    h=idle((k/f"parca-{p}.html").read_text(encoding="utf-8"),p.lower())
    for i,t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',h,re.S):
        toc.append((i,re.sub(r'<[^>]+>','',t)))
    parts.append(f'<div class="parca">{h}</div>')
tochtml="".join(f'<li><a href="#{i}">{t}</a></li>' for i,t in toc)
doc=f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>Vessela — Başlangıç Kılavuzu</title>
<style>{CSS}</style></head><body>
<div class="kapak"><h1>Vessela — Başlangıç Kılavuzu: Basınçlı Kap Hesabını Sıfırdan Öğrenin</h1>
<div class="alt">zeyslabs-vessela</div><div class="tarih">2026-11-18</div>
<div class="nasil"><h3 style="margin-top:0">Nasıl okunur?</h3>
<p>Önce <strong>Bölüm 1–7</strong> ile basınçlı kap hesabının mantığını öğrenin; sonra uygulamayı açıp adım adım (Adım 1&ndash;6) alan alan ilerleyin. Yeşil kutular ipucu, turuncu kutular uyarıdır. Terimlerde takılırsanız Bölüm 7 (Sözlük) yardımcı olur.</p></div></div>
<div class="ic"><h2 style="border:0">İçindekiler</h2><ol>{tochtml}<li>Sorumluluk reddi</li></ol></div>
{"".join(parts)}
<div class="son"><h2 style="border:0">Sonuç</h2>
<p><strong>Sorumluluk reddi:</strong> Hesap sonuçları bir mühendis tarafından doğrulanmalıdır.</p></div>
</body></html>"""
(k/"kilavuz2.html").write_text(doc,encoding="utf-8")
print(len(toc),"h2")

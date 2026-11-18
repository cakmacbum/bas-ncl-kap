import json,re
from pathlib import Path
from html.parser import HTMLParser
k=Path(__file__).resolve().parents[2]/"docs"/"kilavuz2"
html=(k/"kilavuz2.html").read_text(encoding="utf-8")
norm=lambda s:re.sub(r'\s+',' ',s.casefold().replace('İ','i').replace('I','ı')).strip()
class T(HTMLParser):
    def __init__(s):super().__init__();s.t=[]
    def handle_data(s,d):s.t.append(d)
t=T();t.feed(html);text=norm(" ".join(t.t))
srcs=re.findall(r'<img[^>]+src="([^"]+)"',html)
imgs={p.name for p in (k/"img").glob("*.png")}
kirik=[s for s in srcs if not (k/s).exists()]
print("img src:",len(srcs),"kirik:",kirik)
inv=json.loads((k/"alan-envanteri.json").read_text(encoding="utf-8"))
eksik=[r for r in inv if norm(r["etiket"]) not in text]
with open(k/"eksik-etiketler.md","w",encoding="utf-8") as f:
    f.write(f"# Eksik etiketler ({len(eksik)}/{len(inv)})\n\n")
    for r in eksik:f.write(f"- {r['adim']} / {r['alt_adim']} / {r['etiket']}\n")
print("eksik etiket:",len(eksik))
for r in eksik[:10]:print("  ",r['adim'],'/',r['alt_adim'],'/',r['etiket'])
kul={Path(s).name for s in srcs}
print("kullanilmayan gorsel:",sorted(imgs-kul))
bad=[]
for p in sorted(k.glob("parca-*.html")):
    for m in re.finditer(r'<\s*(script|style|iframe)\b|\bonclick\s*=',p.read_text(encoding="utf-8"),re.I):bad.append((p.name,m.group(0)))
print("izinsiz etiket:",bad)

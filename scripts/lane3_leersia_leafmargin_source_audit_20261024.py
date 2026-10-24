#!/usr/bin/env python3
"""Scan exact species Commons series for specifically labelled blade-margin macro.
Metadata-only; never promote image just from a filename.
"""
import json, pathlib, re, urllib.parse, urllib.request, urllib.error, time, html
numbers=[24,25,27,28,29,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]
report={"species":"leersia-oryzoides","scope":"Stefan.lefnaer exact-taxon Commons source descriptions; photo bytes NOT imported in this audit","files":[],"holds":[]}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (credit Wikimedia photographers; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req, timeout=35) as response:return response.read(2000000)
for start in (0,8,16):
 block=numbers[start:start+8]
 titles="|".join(f"File:Leersia oryzoides sl{n}.jpg" for n in block)
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"size|extmetadata","titles":titles})
 try:
  payload=json.loads(fetch(api));pages=payload["query"]["pages"].values()
  for page in pages:
   title=page.get("title","")
   if "imageinfo" not in page:
    report["holds"].append({"title":title,"reason":"missing media"});continue
   info=page["imageinfo"][0];meta=info.get("extmetadata",{})
   def v(key):return html.unescape(re.sub("<[^>]*>"," ",meta.get(key,{}).get("value",""))).strip()
   desc=" ".join(v("ImageDescription").split())
   text=" ".join(desc.split())
   category=("POSSIBLE_BLADE_MARGIN" if re.search(r"blattrand|blatt.?rand|leaf.?margin|blade.?margin|saw.?tooth|retrors|s[aä]gez[aä]hn",text,re.I)
      else "SPECIES_MACRO_OTHER_OR_UNKNOWN")
   report["files"].append({"name":title,"license":v("LicenseShortName"),"artist":v("Artist")[:180],"description":desc[:600],"width":info.get("width"),"height":info.get("height"),"category":category})
 except Exception as e:report["holds"].append({"titles":block,"reason":str(e)[:240]})
 time.sleep(2)
pathlib.Path("reports/lane3-leersia-leafmargin-source-audit-20261024.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"checked":len(report["files"]),"candidates":[f for f in report["files"] if f["category"]=="POSSIBLE_BLADE_MARGIN"],"holds":report["holds"]},ensure_ascii=False))

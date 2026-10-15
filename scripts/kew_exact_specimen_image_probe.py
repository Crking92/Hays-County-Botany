#!/usr/bin/env python3
"""Source-only Kew POWO specimen image media discovery for Physaria sessilis and
Symphyotrichum lanceolatum subsp. lanceolatum. No canonical gallery write.
Does not assume all page images have same rights; record metadata first.
"""
import json,datetime,pathlib,re,html,urllib.request,urllib.parse
from html.parser import HTMLParser
SITES={
 "physaria-sessilis":"https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:1150625-2/images",
 "symphyotrichum-lanceolatum-subsp-lanceolatum":"https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:77180710-1/images"
}
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.urls=[];self.props=[];self.scripts=[]
 def handle_starttag(self,tag,attrs):
  vals=dict(attrs)
  if tag=="img":self.images.append(vals)
  if tag=="a" and vals.get("href"):self.urls.append(vals.get("href"))
  if tag=="meta":self.props.append(vals)
  if tag=="script":self.scripts.append({"src":vals.get("src"),"type":vals.get("type")})
results={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sources":{},"photos_installed":0}
for sid,url in SITES.items():
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (HaysBotany Kew licensed photo research)","Accept":"text/html"})
  with urllib.request.urlopen(req,timeout=35) as r:body=r.read(3000000).decode("utf-8","replace")
  p=Parser();p.feed(body)
  literal_pat=re.compile(r'.{0,180}(?:herbcat|plant-images|image_url|imageUrl|imageId|(?:data-|src=).*?image|cdn\.|iiif|thumbnail|digitized|specimen).{0,220}',re.I)
  excerpts=[html.unescape(m.group())[:340] for m in literal_pat.finditer(body)][:35]
  photos=[x for x in p.images if any(w in str(x).lower() for w in ("herb","powo","kew","plant","cdn","iiif","specimen"))]
  results["sources"][sid]={"page":url,"html_size":len(body),
    "candidate_image_tags":photos[:25],"other_images_count":len(p.images),
    "possible_links":[x for x in p.urls if any(q in x.lower() for q in ("specim","image","herb","kew","download"))][:30],
    "meta_image_props":[x for x in p.props if "image" in str(x).lower()][:15],
    "script_sources":p.scripts[:18],
    "image_markup_excerpts":excerpts}
 except Exception as exc:results["sources"][sid]={"error":str(exc)[:200],"page":url}
pathlib.Path("reports/kew-herbarium-photo-leads.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:{"images":len(v.get("candidate_image_tags",[])),"examples":v.get("candidate_image_tags",[])[:5],"error":v.get("error"),"possible_links":v.get("possible_links",[])[:4]} for k,v in results["sources"].items()},indent=2))

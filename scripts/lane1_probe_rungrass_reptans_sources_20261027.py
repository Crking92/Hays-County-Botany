#!/usr/bin/env python3
"""Nonmutating Lane 1 audit of six original CC BY-NC Urochloa reptans RUNGRASS images."""
import requests,re,json,html
from bs4 import BeautifulSoup
u="https://rungrass.org/"
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotany/1.0 educational site photo rights audit"})
x=s.get(u,timeout=40);print("HTTP",x.status_code,"bytes",len(x.content));x.raise_for_status()
raw=x.text
for match in re.finditer("Urochloa reptans",raw,re.I):
  st=max(0,match.start()-400);en=min(len(raw),match.start()+24000)
  chunk=raw[st:en]
  print("MATCH_POS",match.start(),"HTML_NEAR",re.sub(r"\\s+"," ",chunk[:5000])[:5000])
  ids=list(dict.fromkeys(re.findall(r"(?:/photos/|photos/|photo_id=|photo-id=)([0-9]{6,12})",chunk)))
  href=list(dict.fromkeys(re.findall(r"https?[^\\s'\\\"]{1,200}",chunk)))
  print("NEARBY_PHOTO_IDS",ids[:25])
  print("NEARBY_HREF",json.dumps(href[:30],ensure_ascii=False))
  print("TEXT_SNIPPET",BeautifulSoup(chunk[:12000],"html.parser").get_text(" ",strip=True)[:1200])
  break

#!/usr/bin/env python3
"""Candidate-only anatomical scout: inspect Commons Paspalum setaceum photo series.

Never install a source by genus/category membership alone. Each image remains a
REVIEW candidate until exact species, photo license, and diagnostic pixels agree.
Generated contact sheet is an attributed archival review collage, not a learner photo.
"""
from __future__ import annotations
import html, io, json, pathlib, re, urllib.parse, urllib.request, urllib.error, time
from PIL import Image, ImageDraw, ImageFont, ImageOps
OUT=pathlib.Path("reports/lane4-setaceum-photo-scout-20261027")
OUT.mkdir(parents=True,exist_ok=True)
TITLES=[f"File:PaspalumS{i}.jpg" for i in range(1,10)]+[
 "File:Paspalum setaceum 49099717.jpg",
 "File:Starr 080601-5225 Paspalum setaceum.jpg",
 "File:Starr 080604-5943a Paspalum setaceum.jpg",
 "File:Starr 080607-7291 Paspalum setaceum.jpg",
 "File:Starr 990514-0712 Paspalum setaceum.jpg"]
def read(url,limit=12_000_000):
    error=None
    for attempt in range(4):
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyFieldID/1.0 (strictly licensed image audit; github.com/Crking92/Hays-County-Botany)"})
            with urllib.request.urlopen(request,timeout=55) as response:data=response.read(limit+1)
            if len(data)>limit:raise ValueError("Oversized source")
            return data
        except (urllib.error.URLError,TimeoutError) as exc:
            error=exc
            if isinstance(exc,urllib.error.HTTPError) and exc.code not in (429,500,502,503,504):raise
            time.sleep(2*(attempt+1))
    raise RuntimeError(repr(error))
def normalize(v):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",v or ""))).strip()
url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
 "action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata|size|sha1",
 "iiurlwidth":660,"titles":"|".join(TITLES)
})
data=json.loads(read(url,5_000_000))
items=[]
for page in data.get("query",{}).get("pages",{}).values():
    title=page.get("title","")
    o={"title":title,"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":/()"),
       "source_taxon_status":"Commons category only; requires visual taxon QC","rights_verified":False}
    try:
        info=page["imageinfo"][0];metadata=info.get("extmetadata",{})
        o.update({
            "description":normalize(metadata.get("ImageDescription",{}).get("value",""))[:1800],
            "artist":normalize(metadata.get("Artist",{}).get("value",""))[:300],
            "license":normalize(metadata.get("LicenseShortName",{}).get("value","")),
            "license_url":normalize(metadata.get("LicenseUrl",{}).get("value","")),
            "size_original":[info.get("width"),info.get("height")],
            "original_sha1":info.get("sha1"),
            "source_url":info.get("descriptionurl")})
        rights=o["license"].lower().replace(" ","").replace("-","")
        if any(x in rights for x in ["ccbyncnd","ccbync","ccbynd"]): raise ValueError("Rights restricted: "+rights)
        if not any(x in rights for x in ["cc0","ccby","publicdomain"]):raise ValueError("No individually verified public CC")
        o["rights_verified"]=True
        thumb=info.get("thumburl") or info.get("url")
        if not thumb or not urllib.parse.urlparse(thumb).hostname.endswith("wikimedia.org"):raise ValueError("Unexpected image host")
        raw=read(thumb)
        src=Image.open(io.BytesIO(raw));src.verify()
        src=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
        if min(src.size)<320:raise ValueError("Candidate thumbnail too small")
        # Source originals NOT installed. Only the attributed review contact sheet uses an optimized thumbnail.
        src.thumbnail((224,230),Image.Resampling.LANCZOS)
        o["preview_size"]=list(src.size)
        o["status"]="candidate only (neither species panel nor score)"
        items.append((o,src))
    except Exception as exc:
        o["reason"]=str(exc)[:350]
        items.append((o,None))
font=ImageFont.load_default()
columns=4;cellw=280;cellh=320;rows=(len(items)+columns-1)//columns
sheet=Image.new("RGB",(columns*cellw,rows*cellh),(250,250,246))
draw=ImageDraw.Draw(sheet)
for i,(record,pic) in enumerate(items):
    x=(i%columns)*cellw;y=(i//columns)*cellh
    draw.rectangle((x+3,y+3,x+cellw-3,y+cellh-3),outline=(160,160,160),width=1)
    draw.text((x+12,y+10),record["title"].replace("File:","")[:39],fill=(10,10,10),font=font)
    if pic:
        sheet.paste(pic,(x+12+(224-pic.width)//2,y+36+(230-pic.height)//2))
    who=(record.get("artist") or "unconfirmed author")[:37]
    draw.text((x+11,y+270),"Credit: "+who,fill=(20,20,20),font=font)
    draw.text((x+11,y+286),"License: "+record.get("license","not verified")[:30],fill=(20,20,20),font=font)
report={"target":"Paspalum setaceum","date":"2026-10-27",
"purpose":"Find real exact-species true inner ligule, scaled glume/lemma or rooted crown; no score claims from candidates",
"source_category":"https://commons.wikimedia.org/wiki/Category:Paspalum_setaceum",
"evidence_warning":"Commons category grouping cannot alone certify photographed identity or organ; review pixels before promoting any candidate, and original photographer/source rights individually.",
"license_caveat":"Contact sheet is a study review collage assembled from original Commons image thumbs; any adapted CC BY-SA thumbnails require preserving ShareAlike and attribution in reuse. No data-free claims.",
"images":[x for x,_ in items]}
(OUT/"metadata.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
sheet.save(OUT/"licensed-photo-contact-sheet.jpg","JPEG",quality=88,optimize=True)
print(json.dumps({"count":len(items),"rights_checked":sum(bool(x.get("rights_verified")) for x,_ in items),
 "descriptions":[{k:x.get(k) for k in ("title","artist","license","description","reason")} for x,_ in items]},ensure_ascii=False,indent=2),flush=True)

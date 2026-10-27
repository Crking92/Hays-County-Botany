#!/usr/bin/env python3
"""Browse exact identified CC-licensed P. caroliniana photos, never install automatically.

Creates visual contact sheets plus individual photo source and license ledger.
Selection of root/ligule/dissection remains pending human pixel-level inspection.
"""
import io, json, math, pathlib, time, urllib.parse, urllib.request, re, hashlib
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT = pathlib.Path("reports/lane5-phalaris-photo-scout-20261027")
ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED = {"cc0", "cc-by", "cc-by-sa"}
NAME = "Phalaris caroliniana"
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Hays-County-Botany-Photo-Scout/1.0 (noncommercial educational botany)"})
    with urllib.request.urlopen(req,timeout=40) as reply: return reply.read()
entries=[]; seen=set(); counts={"observations":0,"exact_research":0,"allowed":0}
# TEXAS observation ids first, then broaden to central/southwestern U.S.
queries = [
    {"taxon_name": NAME, "place_id":"18", "quality_grade":"research","order_by":"observed_on", "order":"desc"},
    {"taxon_name": NAME, "place_id":"18", "quality_grade":"research","order_by":"observed_on", "order":"asc"},
    {"taxon_name": NAME, "quality_grade":"research","order_by":"observed_on","order":"desc"},
]
for spec in queries:
  for page in [1,2,3]:
    if len(entries)>=80:break
    params={**spec,"per_page":180,"page":page}
    api="https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode(params)
    try:payload=json.loads(fetch(api))
    except Exception as exc:
      print("API hold",type(exc).__name__,str(exc)[:100]);continue
    obs=payload.get("results",[])
    if not obs:break
    counts["observations"]+=len(obs)
    for o in obs:
      tax=o.get("taxon") or {}
      if tax.get("name")!=NAME or o.get("quality_grade")!="research":continue
      counts["exact_research"]+=1
      for ph in o.get("photos") or []:
        code=(ph.get("license_code") or "").lower().replace("_","-")
        pid=ph.get("id")
        if code not in ALLOWED or not pid or pid in seen:continue
        url=ph.get("url") or ""
        if "/square." not in url and "/small." not in url and "/medium." not in url and "/large." not in url:continue
        seen.add(pid)
        region=o.get("place_guess") or ""
        creator=ph.get("attribution") or ""
        entries.append({"id":str(pid),"obs":str(o.get("id")),"creator":creator,
         "license":code,"site":"iNaturalist","place":region,
         "source_page":f"https://www.inaturalist.org/photos/{pid}",
         "observation_page":f"https://www.inaturalist.org/observations/{o.get('id')}",
         "thumb":re.sub(r"/(?:square|small|medium|large)\.", "/medium.",url),
         "photo_direct":re.sub(r"/(?:square|small|medium|large)\.","/original.",url),
         "research_grade_exact_taxon":True})
        counts["allowed"]+=1
        if len(entries)>=80:break
      if len(entries)>=80:break
    if len(entries)>=80:break
  if len(entries)>=80:break
# Limit image network overhead and image output size; no rights-unclear source photos.
usable=[]
for item in entries:
    if len(usable)>=60:break
    try:
      im=Image.open(io.BytesIO(fetch(item["thumb"])))
      im=ImageOps.exif_transpose(im).convert("RGB")
      if min(im.size)<180:continue
      im.thumbnail((220,160))
      item["small_dimensions"]=list(im.size)
      usable.append((item,im.copy()))
    except Exception:continue
cols=4;rows=5;tiles=20
for sheet_no in range(math.ceil(len(usable)/tiles)):
    subset=usable[sheet_no*tiles:(sheet_no+1)*tiles]
    board=Image.new("RGB",(4*242,5*218),(251,251,248))
    draw=ImageDraw.Draw(board)
    for offset,(it,im) in enumerate(subset):
      idx=sheet_no*tiles+offset
      col=offset%cols;row=offset//cols
      x=col*242+10;y=row*218+8
      board.paste(im,(x,y))
      draw.text((x,y+165),f"{idx+1:02d} | {it['license']} | {it['id']}",fill=(0,0,0))
      draw.text((x,y+184),it["place"][:32],fill=(35,35,35))
      it["sheet"]=sheet_no+1;it["sheet_number"]=idx+1
    outfile=ROOT/f"sheet-{sheet_no+1:02d}.jpg"
    board.save(outfile,"JPEG",quality=79,optimize=True)
report={"date":"2026-10-27","species":NAME,"purpose":"PHOTO_SCOUT_ONLY; no anatomical role certified or photo installed",
"source":"iNaturalist per-photo license; exact research-grade observation name",
"allowed_license_codes":sorted(ALLOWED),"counts":counts,"scouted_with_contact_sheets":len(usable),
"photos":[it for it,im in usable],
"holds":["Contact sheets are miniature previews, not anatomical evidence.","Research grade is source taxon determination, not guaranteed ID accuracy.","True isolated ligule or separated two sterile lemmas require macro and actual scale.","Credit creator/source/license and strip EXIF if photo is later installed."]}
(ROOT/"candidates.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"sheets":math.ceil(len(usable)/tiles),"photographs":len(usable),"counts":counts}))

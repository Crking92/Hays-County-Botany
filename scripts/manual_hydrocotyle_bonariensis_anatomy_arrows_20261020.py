#!/usr/bin/env python3
"""Targeted source-SHA-matched, original-licensed anatomical arrows for 3 bonariensis
photos. Annotate branchpoint/primary rays and underside attachment only, never
imply independent voucher verification or county-native approval.
"""
from pathlib import Path
import hashlib,io,json,math,csv
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
BASE=Path("content/taxa/Araliaceae/Hydrocotyle/hydrocotyle-bonariensis")
C=BASE/"species.json"
SCREEN=Path("workflow/photo-library/reviews/hydrocotyle-bonariensis-20261020/photo-screen.json")
j=json.loads(C.read_text())
assert j["id"]=="hydrocotyle-bonariensis" and len(j["images"])==6
m=json.loads(SCREEN.read_text())
candidates={str(x["photo_id"]):x for x in m["candidates"]}
SETS=[
 {"pid":"666145212","file":"williamkjones-666145212-primary-umbel-rays.jpg",
 "arrows":[("Umbel ray junction",(.497,.520),(.05,.16)),
           ("A primary ray",(.588,.480),(.62,.19))],
 "role":"Confirm the compound inflorescence clue: whole umbrella-like branching node (umbel-ray junction) and one of several primary rays labeled. Secondary whorls and accepted voucher ID are not established by this image alone."},
 {"pid":"590221868","file":"sam-590221868-compound-axis-hand-scale.jpg",
 "arrows":[("Main branch point",(.455,.745),(.055,.57)),
           ("Primary ray",(.551,.644),(.64,.46))],
 "role":"Look closer: hand-held flowering/fruiting head with primary rays converging at main node and a ray labeled. The groups at ray tips show additional flowers; do not claim full mature secondary whorl internode sequence from this photo."},
 {"pid":"479454106","file":"sandy-loam22-479454106-leaf-underside-petiole.jpg",
 "arrows":[("Petiole to underside",(.514,.394),(.035,.085))],
 "role":"Look closer: photo shows underside of round leaf with the petiole joining the lower surface INSIDE the visible leaf margin (peltate). Yellow arrow indicates the junction, not a stem node or leaf edge."}
]
S=requests.Session();S.headers.update({"User-Agent":"HaysCountyBotanyAnatomyPixelReview/1.0 (github.com/Crking92/Hays-County-Botany)"})
def font(n):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",max(17,n))
def draw_arrows(im,details):
 w,h=im.size
 canvas=ImageDraw.Draw(im)
 f=font(round(min(w,1300)*.025))
 for word,point,textpos in details:
  tx,ty=round(w*point[0]),round(h*point[1])
  x,y=round(w*textpos[0]),round(h*textpos[1])
  b=canvas.textbbox((x,y),word,font=f)
  box=(x-6,y-6,b[2]+6,b[3]+6)
  canvas.rounded_rectangle(box,radius=7,fill="#132c27",outline="#fffce7",width=2)
  canvas.text((x,y),word,font=f,fill="#ffffff")
  sx=max(box[0],min(tx,box[2]));sy=box[3] if ty>box[3] else box[1]
  canvas.line(((sx,sy),(tx,ty)),fill="#182019",width=7)
  canvas.line(((sx,sy),(tx,ty)),fill="#ffdc45",width=3)
  angle=math.atan2(ty-sy,tx-sx);ln=max(12,round(min(w,h)*.018))
  canvas.polygon([(tx,ty),(tx-ln*math.cos(angle-.42),ty-ln*math.sin(angle-.42)),
                  (tx-ln*math.cos(angle+.42),ty-ln*math.sin(angle+.42))],fill="#ffdc45")
 return im
def obtain(p,sha):
 pid=p["photo_id"]
 urls=[p["photo_url"].replace("/large.","/original."),p["photo_url"],"https://inaturalist-open-data.s3.amazonaws.com/photos/"+str(pid)+"/original.jpg"]
 for url in dict.fromkeys(urls):
  try:
   r=S.get(url,timeout=42);r.raise_for_status()
   if hashlib.sha256(r.content).hexdigest()!=sha:continue
   with Image.open(io.BytesIO(r.content)) as source:
    source.load();im=ImageOps.exif_transpose(source).convert("RGB")
   im.thumbnail((1450,1450),Image.Resampling.LANCZOS)
   return im
  except Exception as e:print("Source retry",pid,str(e)[:150])
 raise RuntimeError("Cannot find identical SHA-matched media; refuse inaccurate annotations for "+str(pid))
done=[]
for t in SETS:
 entry=next(x for x in j["images"] if x["file"]=="images/"+t["file"])
 if entry.get("manual_arrow_review")=="2026-10-20-final-pixel-correction":
  done.append(t["file"]);continue
 assert entry["license"]=="CC BY" and entry["source_photo_id"]==t["pid"]
 im=obtain(candidates[t["pid"]],entry["source_sha256"])
 im=draw_arrows(im,t["arrows"])
 out=BASE/"images"/t["file"]
 assert out.exists()
 im.save(out,quality=90,optimize=True,progressive=True)
 with Image.open(out) as check:check.verify()
 entry["role"]=t["role"]
 entry["modifications"]="Original resized/reencoded, EXIF removed, then "+str(len(t["arrows"]))+" source-hash-verified yellow anatomical labels added; artist's arrows selected by manual source pixel review."
 entry["anatomy_arrows"]=[{"label":label,"target_fraction":list(point)} for label,point,_ in t["arrows"]]
 entry["manual_arrow_review"]="2026-10-20-final-pixel-correction"
 entry["photo_review"]+=" Exact media original SHA verified, anatomical coordinates selected by human full-size photo inspection; final installed derivative to be re-read before publishing."
 done.append(t["file"])
j["curation_status"]["anatomy_image_install"]="2026-10-20 full image QA flagged both original primary-ray arrows as off-target; corrected primary-ray coordinates on SHA-matched originals. Check latest committed pixels, branchpoint and underside petiole arrow previously passed."
j["curation_status"]["required_to_finish"]=[
 "Full size post-commit pixel check of three arrowed photo derivatives",
 "Taxonomic voucher review under bonariensis versus historical H. verticillata var. triradiata; preserve all valid competing concepts",
 "Mature fruit rib and mericarp pair with 1 mm scale; actual secondary whorl internode sequence beyond primary ray tips if photo becomes available",
 "BONAP/NAPA target county audit unresolved and native scores excluded"
]
j["learner_visual_status"]["note"]="6 physical credited CC BY sources; three anatomical overlays added for primary branching, ray, and peltate leaf underside insertion; full-size final arrows and modern species name still provisional until source-pixel review/voucher."
j["photo_note"]+=" Three arrowed source-SHA-matched photo derivatives added (2 floral branch examples and underside leaf insertion). They annotate only visible anatomical structures, not species-taxonomic certainty."
C.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
with (BASE/"image-sources.csv").open(newline="") as f:
 reader=csv.DictReader(f);rows=list(reader);head=reader.fieldnames
for row in rows:
 for x in SETS:
  if row["file_name"]==x["file"]:row["role"]=x["role"]
with (BASE/"image-sources.csv").open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=head,lineterminator="\n")
 writer.writeheader();writer.writerows(rows)
print(json.dumps({"modified":done,"card_photo_count":len(j["images"]),"accepted_species_voucher_claim":False,"county_native_claim":False},indent=2))

#!/usr/bin/env python3
"""Archive only the two specifically identified USDA-origin sandbur anatomy plates.
No republication of the separately credited ©2007 Regents of California bur plate.
"""
import base64,hashlib,io,json,os,pathlib,time,urllib.parse
import requests
from PIL import Image,ImageOps

repo=os.environ["GITHUB_REPOSITORY"]
token=os.environ["GITHUB_TOKEN"]
branch=os.getenv("GITHUB_REF_NAME","main")
slug=os.environ["PHOTO_SLUG"]
root="content/taxa/Poaceae/Cenchrus/cenchrus-spinifex/"
species=root+"species.json"
source_base="https://idtools.org/id/weed-tool/key/GrapeGrassKey/Media/Images/Entity_key_images/"
record={
 "cupule":(
  "Cen_inc3DissComp.jpg","usda-cenchrus-spinifex-labelled-cupule-and-spikelet.jpg",
  "USDA-labelled original: spikelet enclosed by cupule of fused bristles and base of disseminule",
  "SPINY BUR ANATOMY — original USDA arrow labels spikelet/cupule/base"),
 "sterile-lemma":(
  "Cen_inc3DissClose3Comp.jpg","usda-cenchrus-spinifex-cupule-sterile-lemma.jpg",
  "USDA original macro of partially opened spiny cupule, with labelled sterile lemma and lower glume",
  "OPEN CUPULE — original USDA sterile-lemma label")
}
if slug not in record:raise SystemExit("No approved source ID")
src_name,name,caption,label=record[slug]
url=source_base+src_name
s=requests.Session()
s.headers.update({"User-Agent":"HaysCountyBotany-USDA-Attribution-Review/1.0 (educational site)"})
response=s.get(url,timeout=85)
response.raise_for_status()
if urllib.parse.urlparse(response.url).hostname!="idtools.org":
 raise SystemExit("Unapproved redirected image host")
if not response.content.startswith(bytes.fromhex("ffd8")) or len(response.content)>10_000_000:
 raise SystemExit("Image missing JPEG magic or oversized")
img=Image.open(io.BytesIO(response.content))
img.verify()
img=Image.open(io.BytesIO(response.content))
img=ImageOps.exif_transpose(img).convert("RGB")
if img.width<400 or img.height<400:raise SystemExit("Image too small for labelled anatomy")
out=io.BytesIO();img.save(out,"JPEG",quality=92,optimize=True)
data=out.getvalue()
digest=hashlib.sha256(data).hexdigest()
s.headers.update({"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
                  "X-GitHub-Api-Version":"2022-11-28"})
api=f"https://api.github.com/repos/{repo}/contents/"
def get(path):
 r=s.get(api+urllib.parse.quote(path,safe="/"),params={"ref":branch},timeout=40)
 if r.status_code==404:return None
 r.raise_for_status()
 return r.json()
def put(path,data,sha,msg):
 b={"message":msg,"content":base64.b64encode(data).decode(),"branch":branch}
 if sha:b["sha"]=sha
 r=s.put(api+urllib.parse.quote(path,safe="/"),json=b,timeout=85)
 if r.status_code in (409,422):return False
 r.raise_for_status()
 return True
target=root+"images/"+name
existing=get(target)
if existing and existing.get("size")!=len(data):raise SystemExit("Existing binary differs: preserve")
if not existing and not put(target,data,None,"Archive federally produced sandbur spikelet/cupule anatomical plate"):
 existing=get(target)
 if not existing or existing.get("size")!=len(data):raise SystemExit("Conflicting concurrent photo upload")
attribution="Deena S. Walters and Christina Southwick, USDA APHIS PPQ CPHST"
source_page="https://idtools.org/id/weed-tool/key/GrapeGrassKey/Media/Html/fact_sheets/Cen-inc.html"
rights_page="https://idtools.org/id/weed-tool/key/Whole_key_html/About_tool.htm"
metadata={
 "file":"images/"+name,"role":caption,"creator":attribution,
 "license":"Public domain — U.S. federal photographic work (author source-specific)",
 "license_url":rights_page,"source_page":source_page,"source_image":url,
 "image_sha256":digest,"image_dimensions":[img.width,img.height],
 "source_taxon_name":"Cenchrus spinifex Cav.",
 "source_determination":"USDA scientific key labelled species; not a local Texas voucher",
 "source_locality":"USDA photographed diagnostic seed specimen; no specific Hays County origin indicated",
 "public_reuse":"US government work per authorship and stated rights. Source-specific copyright exception for J. O'Brien NOT included.",
 "modifications":"RGB JPEG re-encode, EXIF/GPS removed; original photographer's anatomical labels preserved",
 "photo_review":"Exact original USDA labeled organ plate; no new arrows or unverified species-ID claim"
}
panel={
 "label":label+" · USDA public domain",
 "scientific_name":"Cenchrus spinifex","image_url":target,"image_fit":"contain",
 "creator":attribution,"license":metadata["license"],"source_page":source_page,
 "image_role":caption,
 "caption":caption+". Original photographed labels point to actual organs, not new overlay arrows. This is USDA seed-reference material, not a Hays specimen.",
 "why_it_matters":"Teaches the distinction between a spiny bur (fused bristles) and enclosed true spikelets; existing green bur photos cannot expose these organs.",
 "markers":[],"photo_status":"USDA-source labeled anatomy physically archived; specimen-locality and new arrow claims deliberately withheld."
}
for attempt in range(6):
 original=get(species)
 if not original:raise SystemExit("Cenchrus canonical species missing")
 d=json.loads(base64.b64decode(original["content"]))
 images=d.setdefault("images",[])
 panels=d.setdefault("visual_comparison",{}).setdefault("items",[])
 prior=[x for x in images if x.get("file")=="images/"+name]
 priorpanels=[x for x in panels if x.get("image_url")==target]
 if len(prior)==1 and len(priorpanels)==1:
  print("ALREADY_ARCHIVED_AND_DISPLAYED",target,digest);break
 if len(prior)>1 or len(priorpanels)>1 or bool(prior)!=bool(priorpanels):
  raise SystemExit("Source photo partially/duplicately represented")
 images.append(metadata)
 first_comparison=next((i for i,p in enumerate(panels) if p.get("scientific_name")!="Cenchrus spinifex"),len(panels))
 panels.insert(first_comparison,panel)
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(images)
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in images)
 d["curation_status"]["lane1_usda_dissected_sandbur_20261024"]="PD_SOURCE_LABELED_ACTUAL_ANATOMY_NO_NEW_ARROWS"
 content=(json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode()
 if put(species,content,original["sha"],"Display USDA-labelled Cenchrus spinifex cupule and spikelet anatomy"):
  print("ARCHIVED_AND_DISPLAYED",target,"sha256",digest)
  break
 time.sleep(attempt+1)
else:raise SystemExit("Concurrent species updates exceeded guard")

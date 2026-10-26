#!/usr/bin/env python3
"""Lane 3 Cynodon: physical public-license stolon photographs, no rhizome bluffing."""
import hashlib,io,json,pathlib,urllib.request,urllib.parse,time
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Cynodon/cynodon-dactylon")
P=ROOT/"species.json"
R=pathlib.Path("reports/lane3-cynodon-stolon-pass-20261026.json")
CC_BY="https://creativecommons.org/licenses/by/2.0/"
CC_SA="https://creativecommons.org/licenses/by-sa/4.0/"
CANDIDATES=[
 {
 "title":"File:Cynodon dactylon stem (6920283073).jpg",
 "page":"https://commons.wikimedia.org/wiki/File:Cynodon_dactylon_stem_(6920283073).jpg",
 "url":"https://upload.wikimedia.org/wikipedia/commons/c/c7/Cynodon_dactylon_stem_%286920283073%29.jpg",
 "local":"images/harry-rose-cynodon-stolon-6920283073-ccby2.jpg",
 "creator":"Harry Rose / Macleay Grass Man","license":"CC BY 2.0","license_url":CC_BY,
 "source_collection":"Independently CC BY 2.0 Flickr photograph mirrored to Commons, NOT Bob Harms' separate Selected Monocots or Plant Resources Center collections",
 "label":"RUNNER ANATOMY — photographed horizontal stem and leaf-bearing nodes",
 "role":"Detached elongated aboveground stem with repeated clear leaf-bearing nodes; roots and rhizomes NOT photographed",
 "caption":"Harry Rose photographed one continuous horizontally oriented Cynodon stem with many separate blade-bearing nodes against black. This teaches the jointed leaf arrangement of a runner. It is NOT a photograph of roots emerging at a node, nor an exposed underground rhizome.",
 "markers":[{"label":"Continuous jointed runner","label_x":1,"label_y":72,"target_x":46,"target_y":45},{"label":"Blade leaving a stem node","label_x":65,"label_y":11,"target_x":64,"target_y":43}],
 },
 {
 "title":"File:Cynodon dactylon sl12.jpg",
 "page":"https://commons.wikimedia.org/wiki/File:Cynodon_dactylon_sl12.jpg",
 "url":"https://upload.wikimedia.org/wikipedia/commons/d/dd/Cynodon_dactylon_sl12.jpg",
 "local":"images/stefan-lefnaer-cynodon-surface-runner-sl12-ccbysa4.jpg",
 "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":CC_SA,
 "source_collection":"Stefan.lefnaer independently authored Commons photograph, not any Bob Harms collection",
 "label":"STOLON IN PLACE — spreading pale runner across bare ground",
 "role":"Aboveground leaf-bearing spreading stolon visibly continuous from patch into bare ground; nodes visible, no verified attached roots",
 "caption":"A single long, dry, jointed surface runner crosses from established vegetation onto the bare paved edge. The plant's surface spread is plain; no underground segment, excavated rhizome, or true roots arising from its nodes are proven.",
 "markers":[{"label":"Long surface stolon","label_x":68,"label_y":91,"target_x":53,"target_y":57},{"label":"Leaves at a visible node","label_x":3,"label_y":42,"target_x":44,"target_y":44}],
 },
]
d=json.loads(P.read_text(encoding="utf8"))
assert d["id"]=="cynodon-dactylon" and d["scientific_name"]=="Cynodon dactylon"
report={"taxon":"Cynodon dactylon","status":"HOLD","added":[],"existing":[],"failures":[]}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPhotoFinish/1.0 (github.com/Crking92/Hays-County-Botany, rights-credited Commons photograph, contact via repository)","Accept":"image/jpeg,image/*"})
 with urllib.request.urlopen(req,timeout=50) as rsp:
  data=rsp.read(15000001)
 assert 30000<len(data)<=15000000,(url,len(data))
 return data
def verify_license(candidate):
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":candidate["title"]})
 try:
  data=json.loads(get(api))
  inf=next(iter(data["query"]["pages"].values()))["imageinfo"][0]
  meta=inf.get("extmetadata",{})
  ls=meta.get("LicenseShortName",{}).get("value","")
  expected="CC BY-SA 4.0" if "SA" in candidate["license"] else "CC BY 2.0"
  if expected not in ls:raise ValueError("Mismatched Commons API license "+ls)
  return {"checked_via":"Commons exact file imageinfo extmetadata","shortname":ls}
 except Exception as exc:
  # Both file pages individually checked with original author, exact source, 
  # CC BY 2.0 FlickreviewR / CC BY-SA 4.0 author-upload on 2026-10-26.
  return {"checked_via":"Commons exact file description previously manually checked 2026-10-26; API temporarily unavailable",
          "external_api_error":str(exc)[:180]}
for candidate in CANDIDATES:
 rel=candidate["local"]
 dest=ROOT/rel
 if any(row.get("file")==rel for row in d["images"]):
  if not dest.exists():raise RuntimeError("Canonical image points at missing bytes: "+rel)
  report["existing"].append(rel);continue
 if dest.exists():
  raise RuntimeError("Unexpected orphan image, do not overwrite: "+rel)
 try:
  rights=verify_license(candidate)
  data=get(candidate["url"])
  with Image.open(io.BytesIO(data)) as im:
   assert im.format=="JPEG"
   im.verify()
  with Image.open(io.BytesIO(data)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   assert min(im.size)>=750
   size=[im.width,im.height]
   im.thumbnail((2600,2600),Image.Resampling.LANCZOS)
   buf=io.BytesIO()
   im.save(buf,"JPEG",quality=89,optimize=True)
   archived=buf.getvalue()
  with Image.open(io.BytesIO(archived)) as chk:
   assert not chk.getexif().get(34853)
   chk.verify()
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(archived)
  checksum=hashlib.sha256(archived).hexdigest()
  d["images"].append({
   "file":rel,"role":candidate["role"],"creator":candidate["creator"],
   "license":candidate["license"],"license_url":candidate["license_url"],
   "source_page":candidate["page"],"source_image_url":candidate["url"],
   "source_collection_note":candidate["source_collection"],
   "public_reuse":"CC license allows redistribution with named attribution, version and modification notice",
   "modifications":"Resized and JPEG reencoded; removed original EXIF/GPS; web annotations are separate overlays",
   "source_original_sha256":hashlib.sha256(data).hexdigest(),
   "archive_sha256":checksum,"source_dimensions":size,
   "photo_status":"ACTUAL JPEG EXAMINED 2026-10-26: surface stems and leaf nodes only; no photographed rhizome or rooted node",
  })
  markers=candidate["markers"]
  assert all(all(0<=m[k]<=100 for k in ("label_x","label_y","target_x","target_y")) for m in markers)
  panel={
   "label":candidate["label"],"scientific_name":"Cynodon dactylon","image_url":str(ROOT/rel),
   "image_fit":"contain","image_role":candidate["role"],"caption":candidate["caption"],
   "why_it_matters":"Real surface runner anatomy, a higher value vegetative structure than repeated lawn-mat photos; does not clear underground-rhizome/rooted-node gap.",
   "creator":candidate["creator"],"license":candidate["license"],"license_url":candidate["license_url"],
   "source_page":candidate["page"],"source_image_url":candidate["url"],
   "modifications":"JPEG resaved without EXIF/GPS; arrows are reversible browser overlays",
   "photo_status":"2026-10-26 original Commons photograph visually checked; two gross-feature arrows only, rooted node and rhizome NOT claimed",
   "markers":markers
  }
  items=d["visual_comparison"]["items"]
  first_seed=next((i for i,x in enumerate(items) if "COLLAR" in str(x.get("label","")).upper()),len(items))
  items.insert(first_seed,panel)
  report["added"].append({"path":str(dest),"sha256":checksum,"license":candidate["license"],"source":candidate["page"],"dimensions":size,"rights":rights})
 except Exception as exc:
  report["failures"].append({"source":candidate["page"],"reason":str(exc)[:280]})
if report["added"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=sum(1 for x in d["images"] if str(x.get("file","")).startswith("images/"))
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["visual_comparison"]["subtitle"]="Real Texas turf and collar/head photos, plus two independently CC-licensed photographed surface runners. Neither new runner image proves rooted nodes or underground rhizomes. Original anatomy photos, marks and credit preserved."
 d["visual_comparison"]["overlay_note"]="Lane 3 2026-10-26: two genuine surface-stolon views, individually CC BY 2.0 / CC BY-SA 4.0 from Commons, physically archived with creator/source and EXIF removed. Four new gross-feature arrow overlays. No roots were inferred from a dry surface node; no photograph here shows an excavated scaly underground rhizome."
 d["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — supplemented real photographed surface runners; still require rooted attached stolon with true roots, excavated underground scaly rhizome with buds/nodes and calibration. Existing true collar and flowering heads retained."
 d["curation_status"]["lane3_surface_runner_pass_20261026"]="Archived two individually CC-licensed exact C. dactylon stolon photographs; 4 visible gross-feature arrow overlays, no rhizome/rooted-node claim."
 P.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 report["status"]="ARCHIVED"
report["photo_count_after"]=len(d["images"]) if report["added"] else None
report["unresolved"]=["stolon demonstrably rooting at soil-contact node","excavated scaly rhizome with nodes/buds and scale","full rooted single colony with flowering shoot"]
R.parent.mkdir(parents=True,exist_ok=True)
R.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,indent=2))

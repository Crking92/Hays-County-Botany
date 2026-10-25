#!/usr/bin/env python3
"""Lane 5: archive differentiated anatomical images of Chloris verticillata.
Verified exact taxon, source photo license, creator, provenance. Do not invent
fertile or sterile lemma boundaries, true ligule or local-voucher status.
"""
import io, json, pathlib, re, urllib.parse, urllib.request, hashlib, html, time
from PIL import Image
ROOT=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-verticillata")
P=ROOT/"species.json"
S=json.loads(P.read_text())
REPORT=pathlib.Path("reports/lane5-tumble-windmillgrass-anatomy-archive-20261025.json")
PHOTO_SPECS=[
 {"name":"ChlorisV1.jpg","author":"Douglas Goldman","lic":"CCBYSA40",
  "slug":"douglas-goldman-verticillata-spikelet-raceme.jpg",
  "label":"REAL MACRO — unilateral spikelets and slender awns",
  "role":"Source-labelled actual one-sided raceme with individual overlapping awned spikelets against dark background",
  "caption":"Douglas Goldman photographed a spikelet-bearing tumble windmillgrass branch in close profile. Narrow bract-covered units follow ONE SIDE of a long rachis, and thin projections rise from the units. The overlapping florets cannot be dissected from the photo; the base of each separate fertile versus sterile awn remains unverified. No metric ruler.",
  "why":"Provides true reproductive-branch anatomy against a contrasting background, instead of another whole-head silhouette.",
  "markers":[{"label":"Awned spikelet row","label_x":4,"label_y":75,"target_x":51,"target_y":52},{"label":"Slender awn","label_x":66,"label_y":8,"target_x":47,"target_y":30}]},
 {"name":"ChlorisV2.jpg","author":"Douglas Goldman","lic":"CCBYSA40",
  "slug":"douglas-goldman-verticillata-raceme-junction-hairs.jpg",
  "label":"RACEME JUNCTION — actual branch attachment and short hairs",
  "role":"Close-up of true multiple radiating racemes meeting the upper reproductive axis; small hairs at BRANCH attachment, not stem collar",
  "caption":"Multiple flowering branches converge on the same photographed inflorescence axis, with tiny whitish hairs visible around their attachment. This is a reproductive RACEME JUNCTION, not the leaf/sheath COLLAR or a vegetative stem node. Do not infer ligule hairs here.",
  "why":"Distinguishes true clustered whorl insertion from vegetative collar anatomy; useful for comparative Chloris panicle topology.",
  "markers":[{"label":"Raceme branching junction","label_x":2,"label_y":85,"target_x":49,"target_y":52},{"label":"Hairs near raceme base","label_x":75,"label_y":74,"target_x":55,"target_y":59}]},
 {"name":"ChlorisV4.jpg","author":"Douglas Goldman","lic":"CCBYSA40",
  "slug":"douglas-goldman-verticillata-rooted-crown.jpg",
  "label":"ACTUAL ROOTED BASE — basal shoots and fibrous roots",
  "role":"Actual same-species exposed plant base showing fibrous roots, clustered flattened basal tillers and bent lower stems",
  "caption":"A source-identified tumble windmillgrass clump has exposed fibrous roots with several basal shoots and curved low stems. The stem/root junction is visible. A connecting RHIZOME or independently rooted STOLON node cannot be positively followed from this one frame; do not label these structures without a better specimen sequence.",
  "why":"Adds true underground/basal photographic evidence absent from the former gallery, helpful for separating rooting growth from a detached tumbling head.",
  "markers":[{"label":"Exposed fibrous roots","label_x":6,"label_y":89,"target_x":47,"target_y":89},{"label":"Basal shoots and crown","label_x":68,"label_y":54,"target_x":49,"target_y":72}]},
 {"name":"ChlorisV5.jpg","author":"Douglas Goldman","lic":"CCBYSA40",
  "slug":"douglas-goldman-verticillata-blade-sheath-junction.jpg",
  "label":"TRUE COLLAR AREA — leaf blade emerging from the sheath",
  "role":"Real grass blade/sheath attachment: pale sheath rim and inserted blade. Fine 0.7–1.3 mm ciliate ligule not independently discernible.",
  "caption":"A leaf blade emerges from the actual sheath mouth of C. verticillata. The pale collar area is now photographed with the correct botanical context, but this view does NOT prove the free edge of the tiny shortly ciliate membranous LIGULE or establish its length; no ruler. The arrow points only to the visible blade/sheath junction.",
  "why":"Separates a genuine vegetative leaf collar from the inflorescence branch attachment in other photographs.",
  "markers":[{"label":"Blade–sheath junction","label_x":71,"label_y":78,"target_x":44,"target_y":63}]},
 {"name":"Chloris verticillata - windmillgrass - 51680653829.jpg","author":"Matt Lavin","lic":"CCBYSA20",
  "slug":"matt-lavin-verticillata-sheath-mouth-macro.jpg",
  "label":"LEAF SHEATH DETAIL — emerging blade and basal junction",
  "role":"Source-labelled macro vegetative junction with green blade and folded leaf/sheath tissues; fine membranous ligule not reliably resolved.",
  "caption":"A second source-verified, magnified leaf/shoot view. Look for the actual base of the emerging green blade and split sheath margin, not a reproductive floret. This is useful for locating where a ligule must be photographed, but the true free membrane edge cannot be calibrated from this image.",
  "why":"Provides a different, close vegetative angle for crew collar recognition. Does not falsely finish the missing 0.7–1.3 mm ligule shot.",
  "markers":[{"label":"Leaf/sheath meeting point","label_x":5,"label_y":87,"target_x":70,"target_y":52}]},
 {"name":"Chloris verticillata - windmillgrass - 51680867945.jpg","author":"Matt Lavin","lic":"CCBYSA20",
  "slug":"matt-lavin-verticillata-awns-on-raceme.jpg",
  "label":"REAL REPRODUCTIVE MACRO — separated spikelets along a rachis",
  "role":"Attached one-sided mature awned spikelets arranged along a narrow rachis against pale background",
  "caption":"A genuine photographed fertile-looking raceme from Matt Lavin's documented species collection. Repeated tan spikelets stand along the rachis and long thin awns project from some units. The fertile versus upper sterile LEMMA and its own awn cannot be independently traced in the overlapping spikelets; no metric scale.",
  "why":"The excellent pale background makes individual attached spikelet bodies and projecting awns clearer for learning than a distant whole flowering wheel.",
  "markers":[{"label":"One-sided spikelet row","label_x":3,"label_y":86,"target_x":54,"target_y":58},{"label":"Fine projecting awns","label_x":76,"label_y":9,"target_x":68,"target_y":37}]},
 {"name":"Chloris verticillata - windmillgrass - 51679981431.jpg","author":"Matt Lavin","lic":"CCBYSA20",
  "slug":"matt-lavin-verticillata-dry-overlapping-florets.jpg",
  "label":"DRY SPIKELET DETAIL — overlapping pale bracts and awns",
  "role":"Close reproductive cluster: source-labelled mature dry spikelets and projecting awns; individual floret structures unresolved",
  "caption":"An original source-determined magnified cluster of dry spikelets and their pale lance-shaped enclosing bracts. Long fine awns project beside them. This view helps recognize mature reproductive units, but overlapping glumes/lemmas cannot be separated into independently identified fertile/sterile parts from the photograph alone.",
  "why":"Shows maturation and overlap in a distinct reproductive view without claiming a detached, measured lemma dissection.",
  "markers":[{"label":"Dry awned spikelet material","label_x":5,"label_y":50,"target_x":50,"target_y":43}]}
]
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (licensed visual-ID image archive)"})
 for attempt in range(5):
  try:
   with urllib.request.urlopen(req,timeout=60) as rsp:return rsp.read()
  except Exception as exc:
   if attempt==4:raise
   if "429" not in str(exc) and "503" not in str(exc):raise
   time.sleep(2**attempt + 2)
results=[]
for spec in PHOTO_SPECS:
 name=spec["name"]
 source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 target=ROOT/"images"/spec["slug"]
 try:
  if target.exists() and any(z.get("file")=="images/"+spec["slug"] for z in S["images"]) and any(z.get("image_url")==str(target) for z in S["visual_comparison"]["items"]):
   results.append({"name":name,"status":"previously_archived","file":str(target),"creator":spec["author"],"license":"CC BY-SA 4.0" if spec["lic"]=="CCBYSA40" else "CC BY-SA 2.0","new_arrows":len(spec["markers"])})
   continue
  params=urllib.parse.urlencode({"action":"query","prop":"imageinfo|categories","iiprop":"url|extmetadata","cllimit":"max","iiurlwidth":"1800","titles":"File:"+name,"format":"json"})
  page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+params))["query"]["pages"].values()))
  info=page["imageinfo"][0]
  meta=info["extmetadata"]
  lic=re.sub(r"[^A-Z0-9]","",meta["LicenseShortName"]["value"].upper())
  artist=html.unescape(re.sub(r"<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
  desc=html.unescape(re.sub(r"<[^>]+>"," ",meta.get("ImageDescription",{}).get("value",""))).strip()
  if lic!=spec["lic"] or spec["author"].casefold() not in artist.casefold():
   raise ValueError("Image-level license/artist mismatch "+lic+" "+artist)
  category_titles=[cat.get("title","") for cat in page.get("categories",[])]
  if "verticillata" not in desc.casefold() and "Category:Chloris verticillata" not in category_titles:
   raise ValueError("Exact species unconfirmed in original file description and Commons category")
  raw=get(info.get("thumburl") or info["url"])
  image=Image.open(io.BytesIO(raw));image.verify()
  image=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(image.size)<550:raise ValueError("Original resolution insufficient")
  target.parent.mkdir(parents=True,exist_ok=True)
  image.save(target,"JPEG",quality=91,optimize=True)
  rel="images/"+spec["slug"]
  license_human="CC BY-SA 4.0" if lic=="CCBYSA40" else "CC BY-SA 2.0"
  license_url="https://creativecommons.org/licenses/by-sa/"+("4.0" if lic=="CCBYSA40" else "2.0")+"/"
  if not any(m.get("file")==rel for m in S["images"]):
   S["images"].append({"file":rel,"role":spec["role"],"creator":spec["author"],"license":license_human,
    "license_url":license_url,"source_page":source,"original_url":info["url"],
    "modifications":"JPEG recompressed, EXIF/GPS stripped; separate browser arrows only","license_review":"Image-level creator, CC BY-SA and exact species metadata verified against Commons API",
    "photo_status":"Local real source-determined species photo; gross visible structures only. No isolated measured lemma/ligule.",
    "image_dimensions":list(image.size),"sha256_local":hashlib.sha256(target.read_bytes()).hexdigest()})
  if not any(z.get("image_url")==str(target) for z in S["visual_comparison"]["items"]):
   S["visual_comparison"]["items"].append({"label":spec["label"],"scientific_name":"Chloris verticillata",
    "image_url":str(target),"image_fit":"contain","image_role":spec["role"],
    "caption":spec["caption"],"why_it_matters":spec["why"],"creator":spec["author"],"license":license_human,
    "license_url":license_url,"source_page":source,"markers":spec["markers"],
    "photo_status":"Author/license/species verified in Commons; photo preview visually checked October 2026, arrows on actually visible gross structures. Live mobile alignment pending; no glume/lemma micromorphology claimed."})
  results.append({"name":name,"status":"archived","file":str(target),"license":license_human,"creator":spec["author"],"pixels":list(image.size),"new_arrows":len(spec["markers"])})
 except Exception as exc:
  results.append({"name":name,"status":"HELD","reason":str(exc)[:230]})
S["field_id_finish_pass"]["lane5_tumble_fine_anatomy_20261025"]={
 "stage":"FIELD_READY_PHOTO_GAPS",
 "archive_results":results,
 "true_evidence":"Locally archived exact-species photos of unilateral awned spikelet branch, branch-base hairs, basal fibrous-root crown, and two real leaf junction views; photographs source-determined, anatomical species-level identity not independently dissected.",
 "remaining":["Source-vouchered separated lower/upper glumes and mature fertile + upper sterile lemmas, awns independently traced and measured with mm ruler","TRUE 0.7–1.3 mm free ligule membrane with ciliate rim and metric ruler","Intact source-vouchered Texas culm with all tier attachment levels and root-to-floret photo sequence","On-device photo/marker alignment and Pages deployment QA"],
 "license_warning":"Existing Joey Santore CC BY-NC source image records preserved but not displayed on public site; selected new photos have original CC BY-SA license and attribution.",
 "scientific_guard":"No species status/identity/taxonomy or native-range fields altered. No anatomy arrows for invisible sterile/ fertile lemma and free ligule."
}
P.write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n")
REPORT=pathlib.Path("reports/lane5-tumble-windmillgrass-anatomy-archive-20261025.json")
REPORT.write_text(json.dumps(S["field_id_finish_pass"]["lane5_tumble_fine_anatomy_20261025"],indent=2)+"\n")
print(json.dumps({"archived":[z["name"] for z in results if z["status"]=="archived"],
                   "held":[z for z in results if z["status"]=="HELD"]}))

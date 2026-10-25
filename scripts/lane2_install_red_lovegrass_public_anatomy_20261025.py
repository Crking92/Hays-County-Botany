#!/usr/bin/env python3
"""Public-safe exact-source red lovegrass anatomical photo install.

Images licensed individually (Patrick Alexander CC0, Douglas Goldman CC BY-SA 4.0).
oxylepis images depict that form; they do not prove all Eragrostis secundiflora concepts.
"""
import hashlib,io,json,pathlib,urllib.error,urllib.parse,urllib.request,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-secundiflora")
p=base/"species.json"
specs=[
 {"title":"File:Eragrostis secundiflora - Flickr - aspidoscelis.jpg",
  "file":"patrick-alexander-red-lovegrass-ripe-spikelets.jpg","creator":"Patrick Alexander",
  "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
  "role":"SOURCE-LABELLED ERAGROSTIS SECUNDIFLORA — pink-red, mature imbricate spikelets on flowering branches; no millimeter scale",
  "label":"MATURE SPIKELETS · CC0 original close photograph",
  "caption":"Patrick Alexander's real Eragrostis secundiflora spikelet photograph. Pinkish paired clustered spikes visibly contain rows of overlapping florets. This photo is CC0, source credited voluntarily. No claim about true ligule dimensions or invisible glumes."},
 {"title":"File:Eragrostis secundiflora oxylepis2.jpg",
  "file":"douglas-goldman-oxylepis-mature-spikelets.jpg","creator":"Douglas Goldman",
  "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
  "role":"SOURCE-LABELLED E. secundiflora subsp. oxylepis — actual pale pink-green ripe spikelet cluster on flowering branch, on black background; not a measured lemma dissection",
  "label":"OXylepis form · large flowering spikelet cluster detail",
  "caption":"Douglas Goldman original source-named Eragrostis secundiflora subsp. oxylepis. Clear close view of overlapping laterally flattened spikelets. CC BY-SA 4.0. This is a subspecies/form-specific photograph; it is not a measurement of all forms."},
 {"title":"File:Eragrostis secundiflora oxylepis3.jpg",
  "file":"douglas-goldman-oxylepis-leaf-collar-3.jpg","creator":"Douglas Goldman",
  "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
  "role":"SOURCE-LABELLED E. secundiflora subsp. oxylepis — leaf blade joins longitudinally ribbed sheath on green culm, visible collar; microscopic ligule-tip itself NOT unambiguously opened",
  "label":"OXYLEPIS COLLAR · leaf blade / sheath union, photographed",
  "caption":"Original photographed blade–sheath junction in source-identified red lovegrass subsp. oxylepis. See the actual leaf blade entering its sheath, but do not place a microscopic ligule label or measure hairs on these pixels. Douglas Goldman, CC BY-SA 4.0."},
 {"title":"File:Eragrostis secundiflora oxylepis4.jpg",
  "file":"douglas-goldman-oxylepis-leaf-collar-4.jpg","creator":"Douglas Goldman",
  "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
  "role":"SOURCE-LABELLED E. secundiflora subsp. oxylepis — alternate high-contrast sheath and blade junction close, collar region visible but no reliable standalone ligule fringe measurement",
  "label":"OXYLEPIS COLLAR · second true junction view, photographed",
  "caption":"Close photograph of a second blade/sheath junction of Eragrostis secundiflora subsp. oxylepis. The photographed collar is authentic; the free ligule is not separately calibrated. Do not invent a ligule fringe marker. Douglas Goldman, CC BY-SA 4.0."}
]
def read(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"HaysBotanyVisualLearner/1.1 (source-credited public photo reuse)","Accept":"image/jpeg,application/json;q=0.9,*/*;q=0.5"}),timeout=75) as f:return f.read()
report={"species":"Eragrostis secundiflora","public_licenses":["CC0 1.0","CC BY-SA 4.0"],"images":[]}
j=json.loads(p.read_text());assert j["id"]=="eragrostis-secundiflora"
for s in specs:
 title=s["title"]
 src="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace("File:","").replace(" ","_"),safe="_()-.")
 result={"source_page":src,"status":"HOLD"}
 try:
  params={"action":"query","format":"json","prop":"imageinfo","titles":title,"iiprop":"url|extmetadata","iiurlwidth":"1280"}
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
  record=next(iter(json.loads(read(api))["query"]["pages"].values()))["imageinfo"][0]
  actual=record["extmetadata"]["LicenseShortName"]["value"].upper()
  if s["license"].startswith("CC0"):assert "CC0" in actual,actual
  else:assert "BY-SA 4.0" in actual,actual
  artist=record["extmetadata"].get("Artist",{}).get("value","")
  assert s["creator"].split()[-1].lower() in artist.lower(),artist[:250]
  variants=[record.get("thumburl"),record.get("url")]
  original=None;chosen=None
  for url in variants:
   if not url:continue
   for attempt in range(3):
    try:
     b=read(url)
     if not b.startswith(b"\xff\xd8"):raise ValueError("not JPEG")
     original=b;chosen=url;break
    except Exception as ex:
     if attempt<2:time.sleep((2,5,11)[attempt])
   if original is not None:break
  assert original is not None,"Rights verified but both image byte URLs failed"
  assert 18000<len(original)<12000000
  trial=Image.open(io.BytesIO(original));trial.verify()
  im=Image.open(io.BytesIO(original)).convert("RGB");assert min(im.size)>500,im.size
  output=base/"images"/s["file"];output.parent.mkdir(parents=True,exist_ok=True)
  im.save(output,"JPEG",quality=92,optimize=True)
  if not any(x.get("source_page")==src for x in j["images"]):
   j["images"].append({"file":"images/"+s["file"],"role":s["role"],"creator":s["creator"],"license":s["license"],
     "license_url":s["license_url"],"source_page":src,
     "public_reuse":"YES public web and repository: exact-source "+s["license"]+" with creator/source credit and ShareAlike where required",
     "modifications":"Re-encoded RGB JPEG without EXIF/GPS or cropping, original features preserved",
     "scientific_hold":"oxylepis morphology should not be generalized to all E. secundiflora subspecies" if "oxylepis" in title.lower() else "No confirmed Hays voucher; photographer source-identification",
     "photo_status":"Photo reviewed visually in 7-photo source contact sheet, source rights checked independently; no speculative microscopic arrows"})
  if not any(x.get("source_page")==src for x in j["visual_comparison"]["items"]):
   j["visual_comparison"]["items"].append({"label":s["label"],"scientific_name":"Eragrostis secundiflora",
    "image_url":str(output),"image_fit":"contain","image_role":s["role"],"caption":s["caption"],
    "why_it_matters":"Actual publicly reusable diagnostic close-up, locally served without external host availability.",
    "creator":s["creator"],"license":s["license"],"license_url":s["license_url"],"source_page":src,
    "markers":[],"photo_status":"Photo copyright and content inspected; real JPEG stored and gallery-linked. No new precise anatomy markers."})
  result.update(status="ARCHIVED_AND_GALLERY_LINKED",file=str(output),pixels=list(im.size),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),download_url=chosen,license=s["license"])
 except Exception as exc:result["error"]=str(exc)
 report["images"].append(result)
installed=sum(x["status"]=="ARCHIVED_AND_GALLERY_LINKED" for x in report["images"])
if installed:
 j["field_id_finish_pass"]["lane2_public_closeup_20261025"]={"stage":"FIELD_READY_PHOTO_GAPS","new_published_eligible_macro_photos":installed,"source":"individual Wikimedia Commons original media verification","allowed_licenses":["CC0","CC BY-SA 4.0"],"variety_warning":"Three Goldman photos specifically oxylepis; do not assume they illustrate all varieties","new_speculative_arrows":0,"not_yet_proven":["fully unfolded 1-mm-scale true ligule","vouchered mature spikelet glumes/lemmas with physical scale","Hays County same-plant specimen and live mobile gallery QA"]}
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=sum(x["file"].startswith("images/") for x in j["images"])
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
audit=pathlib.Path("reports/lane2-red-lovegrass-public-closer-macros-20261025.json")
audit.parent.mkdir(parents=True,exist_ok=True)
audit.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))

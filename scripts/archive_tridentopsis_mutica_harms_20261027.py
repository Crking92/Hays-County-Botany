#!/usr/bin/env python3
"""Source exact Bob Harms Tridens muticus (= Tridentopsis mutica) anatomy photos.
Only credited educational/scientific display; copyright retained, not CC.
"""
import hashlib,io,json,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image,ImageOps
BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
ALT="https://www.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
LICENSE="© Bob Harms — scientific/educational use with attribution (NOT Creative Commons)"
PERMISSION="BOB_HARMS_SELECTED_MONOCOTS_EDU_WITH_CREDIT_20261022"
D=Path("content/taxa/Poaceae/Tridentopsis")
SP=D/"tridentopsis-mutica/species.json"
GP=D/"genus.json"
REP=Path("reports/tridentopsis-mutica-harms-original-anatomy-20261027.json")
MARK=Path("workflow/field-id-publication/2026-10-27-tridentopsis-mutica-harms-anatomy-release.json")
PHOTOS=[
 ("TRMU-L","TRUE COLLLAR — blade/sheath junction and ligule-region image",
  "Actual thin green blades entering narrow sheaths with pale free collar tissue; source has millimeter ticks. Free fringe and tip do not resolve enough to measure a hair length.",
  "See the blade–sheath junction. The photo is not proof of an exact free ciliate ligule tip."),
 ("TRMU-j1","ATTACHED PANICLE — flowering branches with multi-flowered spikelets",
  "Several vertically held narrow flowering branches with attached pale spikelets and a metric scale. Long compact panicle branches are clearly distinguishable, not loose purpletop."),
 ("TRMU-9","DETACHED SPIKELETS — real hairy lemma parts and scale",
  "Source-identified detached spikelets and florets show conspicuous pale hairs and other flowering parts aligned by a metric bar. This is actual reproductive morphology, but individual three-nerved lemma-vein labels require better microscopic proof.")
]
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def download(pid):
    errors=[]
    for base in (BASE,ALT):
        for attempt in range(2):
            try:
                r=requests.get(base+"images/"+pid+".jpg",timeout=35,
                    headers={"Accept":"image/jpeg,image/*","User-Agent":"HaysBotanyBotanicalOriginals/1.0 (educational source attribution)"})
                r.raise_for_status()
                if urlparse(r.url).hostname not in ("w3.biosci.utexas.edu","www.biosci.utexas.edu"):
                    raise ValueError("Untrusted image redirect")
                raw=r.content
                if len(raw)<3000 or len(raw)>4_000_000 or raw[:3]!=b"\xff\xd8\xff":
                    raise ValueError("Invalid source JPEG")
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    if im.format!="JPEG" or min(im.size)<145 or max(im.size)>5000:
                        raise ValueError("Unexpected original image dimensions")
                    source_dims=list(im.size)
                    clean=ImageOps.exif_transpose(im).convert("RGB")
                buf=io.BytesIO();clean.save(buf,"JPEG",quality=94,optimize=True)
                img=buf.getvalue()
                with Image.open(io.BytesIO(img)) as test:
                    assert test.format=="JPEG" and not test.getexif().get(34853)
                    test.verify()
                return dict(img=img,original_sha256=hashlib.sha256(raw).hexdigest(),
                    archived_sha256=hashlib.sha256(img).hexdigest(),
                    source_dimensions=source_dims,archive_dimensions=list(clean.size),
                    downloaded_from=r.url)
            except Exception as e:
                errors.append(type(e).__name__+": "+str(e)[:120])
                time.sleep(1+attempt)
    return {"error":" / ".join(errors[-4:])}
def main():
    sp=json.loads(SP.read_text());gen=json.loads(GP.read_text())
    if sp.get("id")!="tridentopsis-mutica" or gen.get("name")!="Tridentopsis" or "Tridens muticus" not in sp.get("synonyms",[]):
        raise RuntimeError("Exact accepted name and original published synonym guard failed")
    existing={x.get("source_photo_id") for x in sp.get("images",[])}
    archival=[];blocked=[]
    for pid,label,caption,*_ in PHOTOS:
        if pid in existing:
            print("EXISTING",pid);continue
        fetched=download(pid)
        if "error" in fetched:
            blocked.append({"photo_id":pid,"error":fetched["error"]});continue
        path=SP.parent/"images"/("bob-harms-"+pid.lower()+".jpg")
        if path.exists():raise RuntimeError("Existing file without corresponding metadata "+str(path))
        source=BASE+"pages/"+pid+".html"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(fetched["img"])
        metadata={"file":"images/"+path.name,"role":label,
          "creator":"Bob Harms","license":LICENSE,
          "license_url":"https://w3.biosci.utexas.edu/prc/Monocots/",
          "source_page":source,"source_image":BASE+"images/"+pid+".jpg",
          "source_photo_id":pid,"source_taxon_name":"Tridens muticus",
          "accepted_taxon_name":"Tridentopsis mutica",
          "site_specific_public_permission":PERMISSION,
          "public_reuse":"Bob Harms original Selected Monocots copyright retained; free only for scientific/educational use WITH author credit, NOT CC",
          "photo_status":"EXACT ORIGINAL TAXON SOURCE / PHYSICAL GITHUB JPEG / NO MICROSCOPIC ARROWS",
          "modifications":"Converted to RGB JPEG, no crop or arrows, EXIF/GPS removed",
          **{k:v for k,v in fetched.items() if k not in ("img",)}}
        sp["images"].append(metadata)
        panel={"label":label,"scientific_name":"Tridentopsis mutica",
          "image_url":str(path),"image_fit":"contain","image_role":label,
          "caption":caption,"why_it_matters":"Exact source-traced photographed diagnostic anatomy",
          "creator":"Bob Harms","license":LICENSE,"license_url":metadata["license_url"],
          "source_page":source,"source_image":metadata["source_image"],
          "source_taxon_name":"Tridens muticus","accepted_taxon_name":"Tridentopsis mutica",
          "source_photo_id":pid,"site_specific_public_permission":PERMISSION,
          "markers":[],"photo_status":"Real copyright-retained original locally stored with Bob Harms source/credit; source calls it Tridens muticus (accepted Tridentopsis mutica)."}
        for d in (sp,gen):
            if any(x.get("source_photo_id")==pid for x in d["visual_comparison"]["items"]):
                raise RuntimeError("Duplicate same source photo-ID needs review "+pid)
            d["visual_comparison"]["items"].append(dict(panel))
        archival.append({"photo_id":pid,"file":str(path),"sha256":fetched["archived_sha256"],
          "source_dimensions":fetched["source_dimensions"],"source":source})
        print("ARCHIVED",pid,fetched["source_dimensions"])
    if not archival:
        print("NO_PHOTOS_ARCHIVED",blocked);return
    sp["curation_status"]["photo_metadata_count"]=len(sp["images"])
    sp["curation_status"]["photo_files_present"]=sum(
      1 for x in sp["images"] if str(x.get("file","")).startswith("images/") and (SP.parent/x["file"]).is_file())
    sp["curation_status"]["tridentopsis_mutica_harms_anatomy_archive_20261027"]=(
       str(len(archival))+" exact actual Bob Harms Tridens muticus (= accepted Tridentopsis mutica) copyrighted anatomical JPEGs archived. Only visible whole structures highlighted; no invented tiny lemma hairs or ligule tip. Strict PHOTO GAPS remain.")
    dump(SP,sp);dump(GP,gen)
    dump(REP,{"created_utc":datetime.now(timezone.utc).isoformat(),
       "result":"EXACT_COPYRIGHTED_SOURCE_JPEGS_ARCHIVED_FOR_EDUCATION",
       "taxon":"Tridentopsis mutica","source_name":"Tridens muticus",
       "images_added":len(archival),"photos":archival,"blocks":blocked,
       "photo_files_present":sp["curation_status"]["photo_files_present"],
       "teaching_panels":len(sp["visual_comparison"]["items"]),
       "copyright":"Bob Harms; scientific/educational reuse with credit, not CC",
       "remaining":"Living connected root crown, freely exposed ciliate true ligule and calibrated detailed lemma nerve hairs."})
    dump(MARK,{"date":"2026-10-27","target":"tridentopsis-mutica","report":str(REP),
        "noncommercial":True,"status":"Physical archive committed; Pages success still requires live check"})
    print("COMPLETE",len(archival))
if __name__=="__main__":main()

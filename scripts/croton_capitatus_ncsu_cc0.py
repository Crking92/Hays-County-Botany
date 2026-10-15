#!/usr/bin/env python3
"""Install explicitly labeled NC State CC0 Croton capitatus photographs, if live validated.
Exact photo rights must be inspected from fresh plant toolbox HTML. Never save ephemeral
signed URLs or change taxonomy/hold. Strict modern taxon ID and anatomy remain provisional.
"""
import copy,csv,datetime,hashlib,io,json,pathlib,re,sys,urllib.parse
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
ROOT=pathlib.Path(".");sys.path.insert(0,str(ROOT.resolve()))
SID="croton-capitatus"
FOLDER=ROOT/"content/taxa/Euphorbiaceae/Croton/croton-capitatus"
FILE=FOLDER/"species.json"
PAGE="https://plants.ces.ncsu.edu/plants/croton-capitatus/"
LICENSE="https://creativecommons.org/publicdomain/zero/1.0/"
TARGETS=[("Croton_capitatus_flo_KqnJuIIplXth.jpeg","male and female flowers"),
         ("Croton_capitatus_lea_Ha3oJnm0caWg.jpeg","leaves")]
def science(x):
    obj=copy.deepcopy(x)
    for field in ("images","photo_note","learner_visual_status"):obj.pop(field,None)
    if isinstance(obj.get("curation_status"),dict):
        for k in ("photo_metadata_count","photo_files_present","ncsu_cc0_first_photo_install"):
            obj["curation_status"].pop(k,None)
        if not obj["curation_status"]:obj.pop("curation_status",None)
    return obj
def write_csv(path,new):
    t=path.read_text(encoding="utf-8-sig") if path.exists() else ""
    reader=csv.DictReader(io.StringIO(t));cols=list(reader.fieldnames or []);old=list(reader)
    for k in new:
        if k not in cols:cols.append(k)
    old.append(new)
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=cols,lineterminator="\n")
    w.writeheader();w.writerows(old);path.write_text(b.getvalue(),encoding="utf-8")
def fetch_source():
    r=requests.get(PAGE,headers={"User-Agent":"Mozilla/5.0 (compatible; HaysBotany-LicensedPhoto/1.0; research)"},timeout=35)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    if "Croton capitatus" not in soup.get_text(" ",strip=True):raise ValueError("Species source title missing")
    links=[]
    for filename,role in TARGETS:
        anchor=next((a for a in soup.find_all("a",href=True) if filename in a["href"]),None)
        if not anchor:raise ValueError("Missing original NC State image link "+filename)
        # Verify the page actually labels both specific images CC0 and MCD Staff.
        # Search a local ancestor of the individual image, not whole page's unrelated CC0 images.
        node=anchor
        nearby=""
        for _ in range(6):
            node=node.parent
            if node is None:break
            value=node.get_text(" ",strip=True)
            if "MCD Staff" in value and ("CC0 1.0" in value or "CC0" in value):
                nearby=value[:1300]
                break
        if not nearby:raise ValueError("Cannot individually verify CC0 MCD Staff near "+filename)
        raw_url=urllib.parse.urljoin(PAGE,anchor["href"])
        u=urllib.parse.urlparse(raw_url)
        if u.scheme!="https" or u.hostname!="eit-planttoolbox-prod.s3.amazonaws.com":
            raise ValueError("Unexpected NC State media host")
        if not u.path.endswith(filename):raise ValueError("Wrong image filename")
        links.append((filename,role,raw_url,raw_url.split("?")[0]))
    results=[]
    for filename,role,url,redacted_url in links:
        req=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=35)
        req.raise_for_status()
        if len(req.content)>13000000:raise ValueError("Too large")
        with Image.open(io.BytesIO(req.content)) as im:
            im.load()
            rgb=ImageOps.exif_transpose(im).convert("RGB")
        if min(rgb.size)<300 or max(rgb.size)<600:raise ValueError("Photo size too low "+filename)
        rgb.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        out=io.BytesIO();rgb.save(out,format="JPEG",quality=90,optimize=True)
        if len(out.getvalue())<14000:raise ValueError("Small result")
        results.append((filename,role,out.getvalue(),redacted_url,list(rgb.size)))
    return results
def main():
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text())
    for claim in claims.get("claims",[]):
        if SID in claim.get("taxa",[]) and claim.get("status") in ("active","queued","blocked"):
            raise ValueError("Croton capitatus is owned by an active project claim")
    man=json.loads((ROOT/"data/manifest.json").read_text())
    if {v["id"]:v["path"] for v in man["species"]}.get(SID)!=str(FILE):
        raise ValueError("Canonical manifest path mismatch")
    s=json.loads(FILE.read_text(encoding="utf-8"))
    if s.get("id")!=SID or (s.get("images") or []):raise ValueError("Not zero-image anymore")
    image_dir=FOLDER/"images"
    if image_dir.exists() and any(image_dir.iterdir()):raise ValueError("Physical images found")
    validated=fetch_source()
    before=science(s);images=[]
    for filename,role,data,clean_url,dimensions in validated:
        key="flowers" if "flo_" in filename else "leaves"
        dest=image_dir/("ncsu-croton-capitatus-cc0-"+key+".jpg")
        if dest.exists():raise ValueError("Refuse overwrite")
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        row={"file":"images/"+dest.name,"role":role+" as labeled by NC State; photo-specific diagnostic confirmation pending",
             "creator":"MCD Staff","license":"CC0 1.0","license_url":LICENSE,"source_platform":"NC State Extension Plant Toolbox",
             "source_page":PAGE,"downloaded_from":clean_url,
             "source_filename":filename,"image_dimensions":dimensions,
             "study_use":"yes","public_reuse":"yes, CC0",
             "modifications":"resized JPEG; EXIF and metadata removed; no anatomical overlays",
             "photo_review":"Plant toolbox source labels Croton capitatus and individual photo CC0; strict C. capitatus vs. C. lindheimeri visual split not yet independently confirmed"}
        images.append(row)
        write_csv(FOLDER/"image-sources.csv",{
            "file_name":dest.name,"role":row["role"],"creator":row["creator"],"license":"CC0 1.0",
            "license_url":LICENSE,"source_page":PAGE,"direct_url":clean_url,"study_use":"yes",
            "public_reuse":"yes, CC0","modifications":row["modifications"]})
    s["images"]=images
    s.setdefault("curation_status",{})["photo_metadata_count"]=len(images)
    s["curation_status"]["photo_files_present"]=len(images)
    s["curation_status"]["ncsu_cc0_first_photo_install"]=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    s["learner_visual_status"]={"status":"provisional_learner_ready","mode":"learner_fast_fill","image_count":len(images),
                                "note":"Exact-name NC State CC0 source photos installed; species-concept distinction from Croton lindheimeri requires a separate expert visual check.",
                                "missing_diagnostic_views":["verified pistillate sepal posture close-up","confirmed strict taxon-concept comparison against Croton lindheimeri"]}
    s["photo_note"]=((s.get("photo_note") or "")+" NC State labeled Croton capitatus leaf and flower CC0 photos installed as provisional references; do NOT clear taxon-concept hold.").strip()
    if science(s)!=before:raise AssertionError("Scientific concept or taxonomy changed")
    with (FOLDER/"SOURCES.txt").open("a",encoding="utf-8") as f:
        f.write("\nNC STATE EXTENSION CC0 PHOTOS "+datetime.datetime.now(datetime.timezone.utc).isoformat()+"\n"+PAGE+"\n")
        for x in validated:f.write(x[0]+" — MCD Staff, CC0 1.0 "+LICENSE+"\n")
        f.write("Exact species name as NC State labels it. Images need independent strict Croton capitatus vs C. lindheimeri verification. Do not infer target range or clear HOLD. Photo URLs stripped of expiring signatures.\n")
    FILE.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report={"species":SID,"status":"installed_provisional","count":len(images),
            "source_page":PAGE,"images":[{"filename":r[0],"role":r[1],"bytes":len(r[2]),"sha256":hashlib.sha256(r[2]).hexdigest()} for r in validated],
            "science_preserved":True,"taxon_concept_hold_preserved":True}
    pathlib.Path("reports/croton-capitatus-ncsu-cc0-batch.json").write_text(json.dumps(report,indent=2)+"\n")
    from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
    rebuild_photo_fast_fill_queue()
    print(json.dumps(report,indent=2),flush=True)
if __name__=="__main__":main()

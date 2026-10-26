#!/usr/bin/env python3
"""Archive verified federal-public-domain photo evidence without disturbing endangered Z. texana."""
import io, json, pathlib, hashlib, urllib.parse, urllib.request, urllib.error, time
from PIL import Image, ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Zizania/zizania-texana")
CARD=BASE/"species.json"
API="https://commons.wikimedia.org/w/api.php"
USER_AGENT={"User-Agent":"Hays-County-Botany/1.0 (educational local plant learner)"}
ROWS=[
 dict(n="20534",out="usfws-hagerty-20534-flowering-architecture.jpg",
      label="USFWS Texas wild-rice flowering shoots — entire branching architecture",
      role="Ryan Hagerty exact Zizania texana public domain flowering shoot photo: several visible branched inflorescences with dangling yellow male anthers and upright narrow spikelets. Not a same-plant calibrated sex-position map.",
      caption="Public-domain U.S. Fish and Wildlife Service 20534 (Ryan Hagerty, 2016) photographed Texas wild-rice flowering culms with multi-branch panicles. Multiple drooping anthers and slender upright-looking units are visible. The complete entire panicle and exact sex of each branch cannot be assigned with confidence from this overlapped scene; no new sex-label arrows."),
 dict(n="20579",out="usfws-hagerty-20579-upper-awned-spikelets.jpg",
      label="USFWS Texas wild-rice: narrow awned-looking units and hanging anthers",
      role="Ryan Hagerty exact taxon public domain closeup, showing slender upright green spikelet-like units with long filiform tips and separate drooping pale male flower parts. NO exact female lemma/awn origin certified.",
      caption="Public-domain U.S. Fish and Wildlife Service 20579 (Ryan Hagerty, 2016): close view of narrow green flowering units with elongate awn-like projections and pendant pale reproductive organs. Compatible with expected female/male branch differences, but pixels do not establish the precise terminal female lemma-awn insertion or whole-panicle upper/lower orientation. Do not add microscopic or sex-position arrows.")
]
def pull(url):
    err=None
    for i in range(5):
        try:
            req=urllib.request.Request(url,headers=USER_AGENT)
            with urllib.request.urlopen(req,timeout=60) as response:
                b=response.read(10_000_001)
            if len(b)>10_000_000:raise ValueError("too many bytes")
            return b
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            err=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
            time.sleep(3*(i+1))
    raise RuntimeError(repr(err))
def get(n):
    title=f"File:Zizania texana (Texas wild rice) FWS {n}.jpg"
    url=API+"?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata|sha1|size","iiurlwidth":"1600","titles":title,"format":"json"})
    d=json.loads(pull(url));p=next(iter(d["query"]["pages"].values()))
    assert "missing" not in p,repr(p)
    info=p["imageinfo"][0]
    meta=info.get("extmetadata",{})
    licence=meta.get("LicenseShortName",{}).get("value","").lower()
    artist=meta.get("Artist",{}).get("value","").lower()
    combined=" ".join(meta.get(k,{}).get("value","").lower() for k in ("Credit","Artist","UsageTerms","LicenseShortName","License"))
    assert ("public domain" in licence or "pd-usgov" in licence or "pd-usgov" in combined or "public domain" in combined),(n,licence,combined[:160])
    assert ("hagerty" in artist or "hagerty" in combined),(n,artist[:140])
    assert "Zizania texana" in p.get("title",""),p.get("title")
    thumb=info.get("thumburl")
    assert thumb and "wikimedia.org" in thumb,repr(info)
    return info,thumb
def main():
    j=json.loads(CARD.read_text())
    assert j["id"]=="zizania-texana"
    assert len(j["images"])>=8 and len(j["visual_comparison"]["items"])>=8
    installed=[]
    for row in ROWS:
        n=row["n"]
        page=f"https://commons.wikimedia.org/wiki/File:Zizania_texana_(Texas_wild_rice)_FWS_{n}.jpg"
        try:
            info,thumb=get(n)
            raw=pull(thumb)
            assert raw[:2]==b"\xff\xd8",(n,"non-JPEG")
            im=Image.open(io.BytesIO(raw))
            im.verify()
            im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
            assert im.width>=1000 and im.height>=700,(n,im.size)
            dest=BASE/"images"/row["out"]
            dest.parent.mkdir(parents=True,exist_ok=True)
            im.save(dest,"JPEG",quality=91,optimize=True)
            written=dest.read_bytes()
            assert written[:2]==b"\xff\xd8" and written[-2:]==b"\xff\xd9"
            reread=Image.open(dest)
            assert not reread.getexif() and "exif" not in reread.info
            file="images/"+row["out"]
            sha=hashlib.sha256(written).hexdigest()
            metadata=dict(file=file,role=row["role"],creator="Ryan Hagerty / U.S. Fish and Wildlife Service",
                    license="Public domain — official U.S. federal government employee work",
                    license_url="https://commons.wikimedia.org/wiki/Template:PD-USGov-FWS",
                    source_page=page,source_photo_id=n,public_reuse="Public domain; federal author/source credit preserved",
                    source_original_sha1=info.get("sha1"),image_dimensions=list(im.size),archived_sha256=sha,
                    modifications="Resized complete Wikimedia 1600px derivative, stripped EXIF/GPS and re-encoded RGB JPEG; no crop, no source-image arrows",
                    photo_status="USFWS exact species federal public domain photo, original source taxon credited; anther/awn-looking gross organs visible, but detailed sex branch placement, 5–15mm ligule, underwater rooting crown NOT independently proven. Noncontact conservation-only lesson.")
            match=next((x for x in j["images"] if x.get("file")==file or x.get("source_page")==page),None)
            if match is None:j["images"].append(metadata)
            else:match.update(metadata)
            gal=j["visual_comparison"]["items"]
            if not any(x.get("source_page")==page for x in gal):
                gal.append(dict(label=row["label"],scientific_name="Zizania texana",
                     image_url=(BASE/file).as_posix(),image_fit="contain",image_role=row["role"],
                     caption=row["caption"],why_it_matters="No-contact, exact-source public-domain conservation photo showing branching reproductive structures, not a measured dissected female awn or root/collar",
                     creator="Ryan Hagerty / U.S. Fish and Wildlife Service",license="Public domain — US federal government work",
                     license_url="https://commons.wikimedia.org/wiki/Template:PD-USGov-FWS",source_page=page,
                     markers=[],photo_status="EXACT USFWS photograph public domain; genuine pixels gross verified from Commons 960px preview; no new anatomy/sex arrows; no protected plant manipulation."))
            installed.append(dict(source_id=n,file=file,archived_sha256=sha,pixels=list(im.size),original_sha1=info.get("sha1")))
            print("INSTALLED",n,file,sha,flush=True)
        except Exception as e:
            print("HELD",n,repr(e),flush=True)
    if not installed:raise RuntimeError("No new rights-validated photographs installed; do not alter species")
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in j["images"])
    j["learner_visual_status"]["image_count"]=j["curation_status"]["photo_files_present"]
    j["field_id_finish_pass"]["lane4_fws_flower_archive_20261026"]=dict(
      stage="FIELD_READY_PHOTO_GAPS",archived_photos=installed,
      photo_rights="Two separately verified public domain photos by Ryan Hagerty / USFWS. No changes to three original Joey Santore CC BY-NC credits or licenses.",
      gain="Actual broader flowering head morphology and narrower awned-looking reproductive branch close view, but sex branch origin and exact female awn morphology remain uncertain.",
      still_missing=["Ex-situ approved photo of attached true underwater root/stolon/crown","Unmanipulated source-authorized 5–15mm inner membranous ligule macro","One intact panicle with scientifically certified upper female and lower male branches","Female single awn terminal lemma origin at recognizable scale","Rights-filtered live Pages and mobile arrow QA"],
      conservation_rule="FEDERAL/STATE ENDANGERED; do not contact wild stands, reveal sensitive precise coordinates or recommend entering protected aquatic habitat.",
      new_arrows=0,pages_qa="NOT VERIFIED")
    CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
    print("DONE",len(installed),"new USFWS photos,",len(j["visual_comparison"]["items"]),"gallery panels")
if __name__=="__main__":
    main()

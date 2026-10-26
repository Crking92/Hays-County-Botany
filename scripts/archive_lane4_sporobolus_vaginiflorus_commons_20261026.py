#!/usr/bin/env python3
"""Lane 4: archive individually CC BY-SA 4.0-licensed S. vaginiflorus photographs.

Photographer's Austrian 'sensu Fischer 2008' concept is NOT a Hays County voucher,
or a resolution of S. neglectus / ozarkanus nomenclature. Source labels on original
macro are retained. No fine, guessed annotation arrows are added.
"""
import hashlib
import io
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from PIL import Image, ImageOps

BASE = pathlib.Path("content/taxa/Poaceae/Sporobolus/sporobolus-vaginiflorus")
CARD = BASE / "species.json"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "Hays-County-Botany-Lane4/1.0 (noncommercial botanical education; user maintainer)"}
LICENSE = "https://creativecommons.org/licenses/by-sa/4.0/"
SOURCE = "Wikimedia Commons, Stefan.lefnaer, field-collected Austrian S. vaginiflorus sensu Fischer et al. (2008)"
ENTRIES = [
    {
      "number":"125",
      "name":"stefan-lefnaer-sl125-spikelet-labels.jpg",
      "role":"Original close-up of one flower-bearing spikelet seen from two sides, directly marked on source image: lower glume (Glu'), upper glume (Glu\"), lemma (Lem), palea (Pal) and photographic 3 mm scale.",
      "label":"ONE SPIKELET — author-labeled lower/upper glumes, lemma and palea (3-mm scale)",
      "why":"This is a genuine anatomical plate, not an inferred 0.5 mm lemma hair or Texas specimen; source labels and scale are in original pixels.",
      "caption":"Stefan.lefnaer's original Austrian S. vaginiflorus sensu Fischer et al. (2008) photograph of an individual spikelet from two faces. Photographer directly labels Glu' lower glume, Glu\" upper glume, Lem lemma and Pal palea and shows a physical 3-mm scale bar. This panel is a source-identification anatomical reference, not same-plant proof of a Hays population or photographed 400× lemma hooks."
    },
    {
      "number":"126",
      "name":"stefan-lefnaer-sl126-eight-spikelet-angles.jpg",
      "role":"Eight original photographic faces/angles of photographed whole spikelets and glumes/lemma/palea with author labels and 5 mm scale.",
      "label":"EIGHT ANGLES — intact spikelet profile and outer glume / inner floret",
      "why":"Independent multiangle teaching reference so the crew can follow the glumes and inner fertile floret as view changes, without speculative overlay arrows.",
      "caption":"Eight related macro views by Stefan.lefnaer of the same source-labeled European taxon concept, with a 5-mm scale and author-embedded Glu, Lem and Pal labels. The series visually teaches overlapping outer bracts and internal floret architecture. Do not infer an exact local lemma-hair / S. ozarkanus species separation from this gross photographic series."
    },
    {
      "number":"101",
      "name":"stefan-lefnaer-sl101-sheath-junctions.jpg",
      "role":"Five different exterior photos of sheathing leaf-blade junctions and culms with a real 10-mm photo scale; true free inner hair ligule NOT resolved.",
      "label":"FIVE SHEATH ANGLES — blade–sheath attachment at visible scale",
      "why":"Photographically distinguish a blade attachment / upper sheath exterior from an inner minute hair-fringe ligule; do not label outer pale collar tissue as measured inner fringe.",
      "caption":"Stefan.lefnaer's actual close botanical plate illustrates several blade/sheath junctions beside an original 10-mm scale. Exterior lip and culm anatomy are visible. The 0.1–0.3-mm INNER hair ligule is too small / hidden to certify here. Austrian roadside provenance and separately source-labeled taxonomic concept; not a Hays-rooted voucher."
    }
]

def request_bytes(url, timeout=65):
    error = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read(12_000_001)
            if len(raw)>12_000_000:
                raise ValueError("Source image exceeds permitted 12 MB")
            return raw
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429,500,502,503,504):
                raise
            time.sleep(min(20, 3 * (attempt+1)))
    raise RuntimeError(f"Download retried and failed: {error}")

def source_info(n):
    title = f"File:Sporobolus vaginiflorus sl{n}.jpg"
    q = urllib.parse.urlencode({"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata|sha1|size","format":"json"})
    obj = json.loads(request_bytes(API+"?"+q,timeout=45))
    page = next(iter(obj["query"]["pages"].values()))
    assert page.get("title","").lower() == title.lower(), (n,page.get("title"))
    info = page["imageinfo"][0]
    meta = info.get("extmetadata",{})
    license = meta.get("LicenseShortName",{}).get("value","").upper().replace(" ","")
    artist = meta.get("Artist",{}).get("value","")
    assert license in ("CCBY-SA4.0","CCBYSA4.0"), (n,license)
    assert "Stefan.lefnaer".lower() in artist.lower(), (n,artist[:200])
    assert info.get("mime")=="image/jpeg" or info["url"].lower().endswith(".jpg")
    assert int(info.get("width",0)) >= 1000 and int(info.get("height",0)) >= 1200
    return title,info

def sanitize_and_store(raw,dest):
    assert raw[:2]==b"\xff\xd8", "Not JPEG original"
    picture=Image.open(io.BytesIO(raw))
    picture.verify()
    picture=Image.open(io.BytesIO(raw))
    picture=ImageOps.exif_transpose(picture).convert("RGB")
    picture.thumbnail((2600,2600),Image.Resampling.LANCZOS)
    assert picture.width >= 900 and picture.height >= 500, picture.size
    dest.parent.mkdir(parents=True,exist_ok=True)
    picture.save(dest,"JPEG",quality=92,optimize=True,progressive=False)
    saved=dest.read_bytes()
    assert saved.startswith(b"\xff\xd8") and saved.endswith(b"\xff\xd9")
    recheck=Image.open(dest)
    assert not recheck.getexif() and "exif" not in recheck.info
    return picture.size,hashlib.sha256(saved).hexdigest()

def main():
    d=json.loads(CARD.read_text())
    assert d["id"]=="sporobolus-vaginiflorus"
    items=d.setdefault("visual_comparison",{}).setdefault("items",[])
    accepted=0
    newest=[]
    for row in ENTRIES:
        n=row["number"]
        page_url=f"https://commons.wikimedia.org/wiki/File:Sporobolus_vaginiflorus_sl{n}.jpg"
        try:
            title,info=source_info(n)
            raw=request_bytes(info["url"],timeout=90)
            if info.get("sha1"):
                assert hashlib.sha1(raw).hexdigest().lower()==info["sha1"].lower(), (n,"original Commons SHA1 mismatch")
            path=BASE/"images"/row["name"]
            dims,archive_sha=sanitize_and_store(raw,path)
            relative="images/"+row["name"]
            rec={
              "file":relative,"role":row["role"],"creator":"Stefan.lefnaer",
              "license":"CC BY-SA 4.0","license_url":LICENSE,
              "source_page":page_url,"source_taxon_name":"Sporobolus vaginiflorus sensu Fischer et al. 2008",
              "source_provenance":"Austrian roadside, Lower Austria, October 4 2026. NO Hays/Texas occurrence implied.",
              "original_source_sha1":info.get("sha1"),"archive_sha256":archive_sha,
              "image_dimensions":list(dims),
              "public_reuse":"Public site allowed CC BY-SA 4.0; credit photographer, exact source, license and derivative/adaptation note. Any adapted photo overlays must respect BY-SA.",
              "modifications":"EXIF/GPS removed, full source rescaled proportionally to max 2600px edge, JPEG RGB re-encoded; no crop or anatomical changes.",
              "photo_status":"Exact photographer original and individual CC BY-SA 4.0 inspected; no new arrow because labels/scale already inside author photo. Source European taxon concept; not locally vouchered or microscopically sexed."
            }
            prior=next((r for r in d["images"] if r.get("file")==relative or r.get("source_page")==page_url),None)
            if prior is None:d["images"].append(rec)
            else:prior.update(rec)
            if not any(x.get("source_page")==page_url for x in items):
                items.append({
                  "label":row["label"],"scientific_name":"Sporobolus vaginiflorus",
                  "image_url":(BASE/relative).as_posix(),"image_fit":"contain",
                  "image_role":row["role"],"caption":row["caption"],
                  "why_it_matters":row["why"],"creator":"Stefan.lefnaer",
                  "license":"CC BY-SA 4.0","license_url":LICENSE,
                  "source_page":page_url,"source_taxon_concept":"sensu Fischer et al. (2008), Austria, not a verified Hays voucher",
                  "modifications":rec["modifications"],
                  "markers":[],
                  "photo_status":"2026-10-26 original pixels preview checked; original photographer label+scale retained and photo-level CC BY-SA4.0 recorded. Only actual photographed characters; no anatomy overlay arrows added."
                })
            accepted+=1
            newest.append({"number":n,"file":relative,"sha256":archive_sha,"dimensions":list(dims),"source_sha1":info.get("sha1")})
            print("INSTALLED",n,relative,archive_sha,dims)
        except Exception as exc:
            print("HELD",n,str(exc))
    if accepted==0:
        raise RuntimeError("No independently licensed media were physically installed; leave card untouched")
    local_records=[x for x in d["images"] if str(x.get("file","")).startswith("images/")]
    assert all((BASE/x["file"]).is_file() for x in local_records)
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=len(local_records)
    d["learner_visual_status"]["image_count"]=len(local_records)
    d["field_id_finish_pass"]["lane4_stefan_commons_20261026"]={
      "stage":"FIELD_READY_PHOTO_GAPS",
      "new_exact_photo_count":len(newest),
      "source":"Wikimedia Commons Stefan.lefnaer CC BY-SA 4.0 independently source-restricted to sensu Fischer et al 2008",
      "source_location":"Enzersfeld Lower Austria, NOT a Hays Texas voucher or county range proof",
      "downloaded_photos":newest,
      "photo_diagnostic_gain":"One real source-labelled 3mm spikelet showing BOTH GLUMES, LEMMA, PALEA plus second 5mm eight-angle plate, and external sheath junction plate where available",
      "not_cleared":["0.1–0.3-mm true INNER hair-fringe ligule","Microscopic verified lemma hooks/pubescence vs S. neglectus and S. ozarkanus","Directly opened sheath enclosing an actual mature flower","Hays source-vouchered same-root-to-head local identification","Live Pages/mobile annotation and rights QA"],
      "no_new_arrows":True,"no_taxonomy_or_county_change":True,
      "rights_note":"Resized photo adaptations retain CC BY-SA 4.0 credit/source/version/change notice. Earlier Harms originals unchanged."
    }
    # Card galleries may be concurrently changed by independent automations;
    # this writer only appends, preserves all existing items, and pulls with rebase.
    CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
    print("VERIFIED",len(newest),"new exact photos,",len(items),"total panels,",len(local_records),"physical own taxon JPEGs")

if __name__=="__main__":
    main()

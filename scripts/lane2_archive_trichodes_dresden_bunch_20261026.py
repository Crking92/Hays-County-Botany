#!/usr/bin/env python3
"""Lane 2: exact-file verified CC0 in-ground E. trichodes photo, no speculative ligule arrows."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image, ImageOps
from hashlib import sha256
import io,json,html,re

CARD=Path("content/taxa/Poaceae/Eragrostis/eragrostis-trichodes/species.json")
DEST=CARD.parent/"images"/"daderot-dresden-inground-bunch-2013.jpg"
REPORT=Path("reports/lane2-trichodes-in-ground-bunch-20261026.json")
NAME="Eragrostis trichodes - Botanischer Garten, Dresden, Germany - DSC08739.JPG"
SOURCE="https://commons.wikimedia.org/wiki/File:Eragrostis_trichodes_-_Botanischer_Garten,_Dresden,_Germany_-_DSC08739.JPG"
LICENSE="https://creativecommons.org/publicdomain/zero/1.0/"
UA={"User-Agent":"HaysCountyBotanyLearner/1.0 (photo-level rights and species evidence review)"}
def fetch(url, maxbytes):
    with urlopen(Request(url,headers=UA),timeout=50) as stream:
        final=stream.url
        data=stream.read(maxbytes+1)
        if len(data)>maxbytes:raise RuntimeError("Photo exceeds safe byte bound")
        return final,data

def main():
    doc=json.loads(CARD.read_text(encoding="utf-8"))
    assert doc["id"]=="eragrostis-trichodes"
    orig=next(x for x in doc["images"] if x.get("source_page")==SOURCE)
    assert orig["file"].startswith("https://commons.wikimedia.org/wiki/Special:Redirect"),"Photo already localized or changed; stop"
    api="https://commons.wikimedia.org/w/api.php?"+urlencode({"action":"query","titles":"File:"+NAME,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":"2000","format":"json"})
    _,raw=fetch(api,2_000_000)
    response=json.loads(raw)
    page=next(iter(response["query"]["pages"].values()))
    assert page.get("title")=="File:"+NAME and "imageinfo" in page,"Commons exact file not resolved"
    detail=page["imageinfo"][0]
    short=html.unescape(detail["extmetadata"]["LicenseShortName"]["value"]).lower()
    artist=html.unescape(detail["extmetadata"]["Artist"]["value"])
    artist_clean=re.sub("<[^>]*>","",artist)
    assert "cc0" in short or "public domain" in short,(short,artist_clean)
    assert "Daderot" in artist_clean,(short,artist_clean)
    assert detail["width"]==5472 and detail["height"]==3648,(detail["width"],detail["height"])
    links=[detail.get("thumburl"),detail.get("url")]
    photo=None
    errors=[]
    chosen=None
    for url in links:
      if not url:continue
      try:
        end,data=fetch(url,12_000_000)
        assert end.startswith(("https://thumb.wikimedia.org/","https://upload.wikimedia.org/")),end
        with Image.open(io.BytesIO(data)) as src:
            assert src.format=="JPEG" and min(src.size)>900
            photo=ImageOps.exif_transpose(src).convert("RGB")
        chosen=end
        break
      except Exception as e:
        errors.append(str(e)[:250])
    if photo is None:raise RuntimeError("No verified Commons image bytes; "+str(errors))
    photo.thumbnail((2200,2200))
    bio=io.BytesIO()
    photo.save(bio,format="JPEG",quality=88,optimize=True)
    clean=bio.getvalue()
    with Image.open(io.BytesIO(clean)) as chk:
        assert chk.format=="JPEG" and not chk.getexif()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    if DEST.exists():
        assert DEST.read_bytes()==clean,"Concurrent existing photo differs; do not overwrite"
    else: DEST.write_bytes(clean)
    old_url=orig["file"]
    orig["historical_external_file"]=old_url
    orig["file"]="images/"+DEST.name
    orig["role"]="WHOLE LIVE GROUNDED BUNCHGRASS CROWN: long slender green/straw arching blades radiating from ground-level tuft among several nursery specimens; individual roots and real 0.4-mm ligule NOT visible"
    orig["creator"]="Daderot"
    orig["license"]="CC0 1.0"
    orig["license_url"]=LICENSE
    orig["public_reuse"]="CC0 individually checked at source Commons file, public website permitted; credit voluntarily retained"
    orig["photo_status"]="Physically archived from original authenticated Wikimedia photo/thumbnail 2026-10-26, actual pixels reviewed for broad growth habit, specimen botanically source-labelled. Cultivated Dresden specimen; not Hays Texas voucher."
    orig["modifications"]="Original pixels downscaled to no more than 2200px long side, RGB JPEG re-encoded EXIF/GPS-free; non-destructive separate browser arrow"
    rel="content/taxa/Poaceae/Eragrostis/eragrostis-trichodes/images/"+DEST.name
    items=doc["visual_comparison"]["items"]
    assert not any(x.get("image_url")==rel for x in items),"Gallery already includes original"
    panel={
      "label":"GROWING IN SOIL · actual broad bunchgrass crown and long arching blades",
      "scientific_name":"Eragrostis trichodes","image_url":rel,"image_fit":"contain",
      "image_role":"Real Daderot photograph of a cultivated exact-source-labelled sand lovegrass bunch growing in garden soil. Multiple tillers/basal blades converge into apparent crown; no excavated roots.",
      "caption":"Daderot's 2013 Dresden botanical garden photograph visibly shows a live planted bunch of sand lovegrass with many narrow arching leaves. The arrow points to the central ABOVEGROUND leafy tuft at soil level — NOT to an exposed rooted crown or rhizome. Adjacent labelled grasses are different specimens; do not confuse their blades with this plant. The true short fringe ligule (about 0.4 mm) and longer sheath-throat hairs (up to 4–5 mm) are NOT resolved.",
      "why_it_matters":"Adds a genuine planted bunchgrass growth-form photo, not just another distant reproductive cloud; practice identifying the base before following attached culms upward.",
      "creator":"Daderot","license":"CC0 1.0","license_url":LICENSE,"source_page":SOURCE,
      "modifications":"Rights-verified photo scaled and EXIF/GPS stripped; 1 SVG learning pointer, underlying source JPEG not marked",
      "photo_status":"Photo-level Commons original CC0 verified, exact titled Eragrostis trichodes at Dresden garden, roots and collar hairs unresolved. One coarse anatomical arrow on obviously visible central leafy crown.",
      "markers":[{"label":"Central leafy bunch at soil surface (roots NOT visible)","label_x":3,"label_y":80,"target_x":46,"target_y":62}]
    }
    # Only same-taxon panels before look-alikes; preserves existing ordering and arrows.
    at=next((i for i,x in enumerate(items) if x.get("scientific_name")!="Eragrostis trichodes"),len(items))
    items.insert(at,panel)
    qc=doc["field_photo_quickcheck"]
    qc["steps"][0]="Start at the actual basal growing bunch in the new CC0 Dresden garden photograph: narrow arching leaf blades converge toward a soil-level tuft. This is NOT an excavated root crown. Then use the original Texas and Sam Kieschnick images to find the fine complete panicle and real spikelets."
    qc["featured_photo_indices"]=list(range(at+1))
    qc["warning"]+=" On 2026-10-26 verified original CC0 Daderot Dresden image archived and shown as in-ground bunch reference; one clearly visible aboveground crown arrow. TRUE 0.4-mm ligule, separate long throat/collar hair tuft, and exposed connected rootstock are NOT visible and remain photo gaps."
    doc["field_id_finish_pass"]["photo_gaps"]=[
       "Excavated rooted bunch connected to attached complete panicle on one authenticated individual (the new image only shows ground-level crown)",
       "TRUE 0.4-mm hair-fringe ligule photographed INSIDE peeled-open blade–sheath junction with millimeter scale, distinct from long 4–5-mm throat/collar hairs",
       "Mature spikelet with 1-mm scale and verified glumes/lemma as needed to separate open-panicle lovegrass look-alikes"
    ]
    doc["field_id_finish_pass"]["lane2_20261026_inground_bunch"]={
        "status":"FIELD_READY_PHOTO_GAPS","new_photos":0,"new_locally_archived_prior_external_photos":1,
        "annotation_count":1,"role":"soil-level growing leafy bunch only","true_ligule_completed":False,
        "rootstock_and_rhizomes_exposed":False,"source_locality":"Dresden botanical garden, Germany, not a Hays County specimen"
    }
    cs=doc["curation_status"]
    cs["photo_metadata_count"]=len(doc["images"])
    cs["photo_files_present"]=sum(str(z.get("file","")).startswith("images/") for z in doc["images"])
    cs["lane2_dresden_bunch_20261026"]="Previously external CC0 in-ground bunch now archived locally and connected to actual gallery; 1 gross organ arrow"
    doc["photo_note"]=doc.get("photo_note","")+"\n2026-10-26 Lane 2: migrated existing source-selected Daderot CC0 Dresden living in-ground clump into source-cleaned local gallery, one clearly visible gross arrow on central leafy bunch; rootstock and true 0.4-mm ligule remain missing; all existing original reproductive photos, look-alikes, NC license and annotations preserved."
    if isinstance(doc.get("learner_visual_status"),dict):doc["learner_visual_status"]["image_count"]=len(doc["images"])
    CARD.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
       "species":"Eragrostis trichodes","photo_source":SOURCE,
       "source_creator":"Daderot","license":"CC0 1.0","source_original_pixels":[5472,3648],
       "stored_clean_pixels":list(photo.size),"stored_bytes":len(clean),"sha256":sha256(clean).hexdigest(),
       "original_commons_download_url":chosen,"archived_path":str(DEST),
       "was_preexisting_remote_metadata_photo":True,"new_local_photo_count":cs["photo_files_present"],
       "new_gross_organ_arrows":1,"anatomical_photo_role":"in-ground leafy growing bunch and radiating blades",
       "absent":"excavated true root crown, membrane/hair ligule inside collar, mature scale-authenticated spikelet",
       "license_preservation":"Joey Santore CC BY-NC Eragrostis intermedia comparison not removed, pending photo-level NC policy audit",
       "stage":"FIELD_READY_PHOTO_GAPS","public_site_verified":False
    },indent=2)+"\n",encoding="utf-8")
    print("ARCHIVE_SUCCESS",len(clean),photo.size,str(DEST))
if __name__=="__main__": main()

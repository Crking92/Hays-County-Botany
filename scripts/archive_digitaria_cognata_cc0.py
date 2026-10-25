#!/usr/bin/env python3
"""One-taxon's exact-source CC0 archive, idempotent; run in GitHub Actions."""
import io, json, pathlib, urllib.request, hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Digitaria/digitaria-cognata")
p=base/"species.json"
d=json.loads(p.read_text())
assert d["id"] == "digitaria-cognata"
photos=[
("99737795","4/49","shaun-pogacnik-99737795.jpg","Close flowering panicle; reddish fine branching axes and individual spikelets"),
("99737817","1/13","shaun-pogacnik-99737817.jpg","Basal leafy tuft with slender reddish mature panicles"),
("99737830","e/e6","shaun-pogacnik-99737830.jpg","Terminal narrow oval spikelets on threadlike reddish stalks; NOT glume or ligule micro-dissection")]
for photo_id,folder,name,role in photos:
    url=f"https://upload.wikimedia.org/wikipedia/commons/{folder}/Digitaria_cognata_iNat-{photo_id}.jpg"
    dest=base/"images"/name
    if not dest.exists():
        req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (educational photo archive)"})
        with urllib.request.urlopen(req,timeout=45) as response:
            b=response.read()
        assert len(b)>15000 and len(b)<12000000, "unexpected image size"
        if photo_id=="99737830":
            # Wikimedia Commons exact public-domain file (Shaun Pogacnik),
            # checked at https://commons.wikimedia.org/wiki/File:Digitaria_cognata_iNat-99737830.jpg
            # This fingerprint pins the actual original; hold if source changes.
            assert hashlib.sha1(b).hexdigest()=="543e42b5463e997a40ef78b418b83acf3a890a8a", "Original CC0 image fingerprint mismatch"
        im=Image.open(io.BytesIO(b)); im.verify()
        im=Image.open(io.BytesIO(b)).convert("RGB")
        assert im.width>=800 and im.height>=600
        dest.parent.mkdir(parents=True,exist_ok=True)
        im.save(dest,format="JPEG",quality=91,optimize=True) # no EXIF/GPS transferred
    assert dest.stat().st_size>15000
    record={"file":"images/"+name,"role":role,"creator":"Shaun Pogacnik","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":f"https://commons.wikimedia.org/wiki/File:Digitaria_cognata_iNat-{photo_id}.jpg","original_source_page":f"https://www.inaturalist.org/photos/{photo_id}","public_reuse":"Public domain CC0; credited for educational provenance","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; exact taxon tagged at source, diagnostic anatomy unverified"}
    if not any(x.get("file")==record["file"] for x in d["images"]):d["images"].append(record)
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(1 for x in d["images"] if (base/x.get("file","")).is_file())
# Relink ONLY the already visually checked exact-source terminal spikelet panel.
# No new anatomy annotations are invented by this physical archival.
local_url="content/taxa/Poaceae/Digitaria/digitaria-cognata/images/shaun-pogacnik-99737830.jpg"
if (base/"images/shaun-pogacnik-99737830.jpg").is_file():
    matched=[x for x in d["visual_comparison"]["items"] if x.get("source_page")=="https://commons.wikimedia.org/wiki/File:Digitaria_cognata_iNat-99737830.jpg"]
    assert len(matched)==1,"Expected exactly one existing macro gallery panel"
    panel=matched[0]
    panel["image_url"]=local_url
    panel["image_role"]="PHYSICALLY ARCHIVED CC0 exact-source photo of several separate terminal oval spikelets on hair-thin purple pedicels; no measured glume/ligule/hairy axil."
    panel["photo_status"]="2026-10-25: Commons CC0 source/license verified; exact original SHA-1 matched and re-encoded locally without EXIF/GPS. Existing 3 visible-only gross markers kept; no micromorphology certified."
    panel["modifications"]="Original JPEG re-encoded as RGB JPEG; EXIF/GPS removed; existing 3 on-page arrows retained."
    for record in d["images"]:
        if record.get("file")=="images/shaun-pogacnik-99737830.jpg":
            record["photo_status"]="LOCAL BYTES VERIFIED SHA-1 AT SOURCE; gross terminal spikelet photo only, no glume/lemma measurement"
            record["source_original_sha1"]="543e42b5463e997a40ef78b418b83acf3a890a8a"
            record["modifications"]="Re-encoded RGB JPEG, EXIF/GPS stripped"
    d.setdefault("field_id_finish_pass",{})["lane4_terminal_spikelet_archival_20261025"]={
        "status":"FIELD_READY_PHOTO_GAPS",
        "physically_archived_own_species_photos":d["curation_status"]["photo_files_present"],
        "new_archived_role":"Existing external terminal-spikelet photo now physically archived; original identified CC0 image, source SHA-1 verified",
        "existing_gross_markers_preserved":3,
        "new_organ_level_markers":0,
        "remaining":["Real swollen hairy branch axil at sufficient resolution","True membranous 0.5-mm ligule against scale","Crispate leaf margin compared with opposite edge","Mature dissected glumes and lemmas at 1-mm scale","Confirmed connected rooted perennial crown","Live Pages gallery check"],
        "photo_rights_hold":"Copyrighted Minnesota Wildflowers node/glume macro photographs found, not licensed for republication: DO NOT COPY."
    }
    note=" Lane 4 2026-10-25: existing CC0 terminal-spikelet external gallery photo physically archived via source SHA-1 check; kept 3 verified gross markers; diagnostic collar, hairs and dissection still absent."
    if note not in d.get("photo_note",""): d["photo_note"]=str(d.get("photo_note",""))+note
    d["visual_comparison"]["subtitle"]="Four exact-species panels now use physically archived credited JPEGs, followed by three comparisons. Genuine terminal spikelet macro is source-verified CC0; ligule, swollen pubescent nodes, leaf margin and dissection remain photo gaps."
    d["visual_comparison"]["overlay_note"]="Four own-species CC BY/CC0 photographic panels use local JPEGs; three D. ciliaris comparisons remain. No measured ligule, swollen axil hairs, or glume dissection is claimed."
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
print("archived",len(d["images"]),"exact species photos")

#!/usr/bin/env python3
"""Archive Alex Abair's exact-species, entire attached Tobosa flowering head.

Anatomy: visually complete terminal head with separated successive open
papery fascicles. No individual sexed spikelet/glume/lemma claims; ligule absent.
"""
import io,json,hashlib,pathlib,time,urllib.request
from PIL import Image
BASE=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-mutica")
CARD=BASE/"species.json"
FILENAME="alex-abair-tobosa-full-open-mature-head-ccby4.jpg"
DEST=BASE/"images"/FILENAME
PAGE="https://commons.wikimedia.org/wiki/File:Hilaria_mutica_25040738.jpg"
URL="https://upload.wikimedia.org/wikipedia/commons/5/55/Hilaria_mutica_25040738.jpg"
sp=json.loads(CARD.read_text(encoding="utf-8"))
assert sp["id"]=="hilaria-mutica"
if DEST.exists() and any(x.get("file")=="images/"+FILENAME for x in sp.get("images",[])):
    print("Already installed");raise SystemExit(0)
assert not DEST.exists()
assert not any(x.get("source_page")==PAGE for x in sp.get("images",[]))
raw=None
for k in range(4):
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"HaysBotanyCrewFieldLearner/1.0 source attribution and CC BY photo archive"})
        with urllib.request.urlopen(req,timeout=55) as r: raw=r.read()
        break
    except Exception as e:
        print(k+1,str(e),flush=True)
        if k==3:raise
        time.sleep((k+1)*7)
assert raw and 100000<len(raw)<4000000
im=Image.open(io.BytesIO(raw));im.load()
assert im.format=="JPEG" and im.size==(1536,2048),f"Image version unexpected {im.size}"
DEST.parent.mkdir(parents=True,exist_ok=True)
im.convert("RGB").save(DEST,"JPEG",quality=92,optimize=True)
photo={
 "file":"images/"+FILENAME,
 "role":"A fully attached mature tobosa narrow flowering head, showing the series of spaced pale fan-shaped bract clusters along the upright stalk, source-confirmed by Alex Abair; NOT a dissected triad or true collar.",
 "creator":"Alex Abair",
 "license":"CC BY 4.0",
 "license_url":"https://creativecommons.org/licenses/by/4.0/",
 "source_page":PAGE,
 "source_original":URL,
 "source_photo_page":"https://www.inaturalist.org/photos/25040738",
 "source_observation":"https://www.inaturalist.org/observations/16617969",
 "source_taxon_name":"Hilaria mutica",
 "source_region":"Doña Ana County, New Mexico; 2018-09-16, not Hays County.",
 "license_evidence":"Wikimedia Commons image-specific original by Alex Abair reviewed by iNaturalistReviewBot CC BY 4.0 and exact source-identified Tobosa.",
 "public_reuse":"CC BY 4.0 with photographer credit, source, license and changes notice.",
 "image_dimensions":[1536,2048],
 "image_sha256":hashlib.sha256(DEST.read_bytes()).hexdigest(),
 "photo_review":"Actual source image visually checked: whole narrow erect terminal head from attenuate apex to stalk junction with multiple pale bract clusters spread around a central flowering axis. No true ligule, 1-mm ruler, sexed triad dissection or underground organs.",
 "modifications":"RGB JPEG recompressed without crop, GPS/EXIF removed."
}
sp["images"].append(photo)
panel={
 "label":"ENTIRE OPEN MATURE HEAD — genuine tobosa flowering-axis sequence (Alex Abair)",
 "scientific_name":"Hilaria mutica",
 "image_url":"content/taxa/Poaceae/Hilaria/hilaria-mutica/images/"+FILENAME,
 "image_fit":"contain",
 "creator":"Alex Abair","license":"CC BY 4.0",
 "license_url":"https://creativecommons.org/licenses/by/4.0/",
 "source_page":PAGE,
 "image_role":"Real unbroken mature terminal flowering spike with multiple spaced paperlike opened clusters on its upright axis; not detached heads or falsely dissected sexed spikelets.",
 "caption":"Follow this genuine tobosa head from its tip toward the stem: pale papery units are repeated up a slender upright axis. For detail, see the separately photographed detached fans, but do not name individual fertile and staminate spikelets here—those require a 1-mm-scale dissection.",
 "why_it_matters":"Bridges photographed plant habit with a complete attached mature flowering head, showing where the zoomed veined papery clusters sit on the actual grass.",
 "markers":[
   {"label":"Consecutive attached papery flowering groups","label_x":1,"label_y":22,"target_x":49,"target_y":38},
   {"label":"Single flowering axis carrying the groups","label_x":63,"label_y":85,"target_x":50,"target_y":72}
 ],
 "photo_status":"Original visually confirmed for clear gross structures only, not exact sexed triad anatomy. Mobile arrow QA and GitHub Pages deployment unverified."
}
p=sp["visual_comparison"]["items"]
idx=next((i for i,x in enumerate(p) if x.get("scientific_name")!="Hilaria mutica"),len(p))
p.insert(idx,panel)
sp.setdefault("curation_status",{})["lane1_abair_tobosa_whole_head_20261027"]="VERIFIED_CC_BY4_COMPLETE_ATTACHED_MATURE_HEAD_ADDED_LIGULE_TRIAD_RHIZOME_UNRESOLVED"
sp["curation_status"]["photo_files_present"]=len(sp["images"])
sp.setdefault("learner_visual_status",{})["image_count"]=len(sp["images"])
sp["photo_note"]=(sp.get("photo_note") or "")+" 2026-10-27: authentic high-resolution CC BY 4.0 Alex Abair entire open mature tobosa head archived with two gross axis/group arrows; distinct from earlier close-up papery fan photos. No true 0.5–2 mm ligule nor sexed triad resolved."
CARD.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"archived", "path":str(DEST),"photos":len(sp["images"]),"panels":len(p),"bytes":DEST.stat().st_size}))

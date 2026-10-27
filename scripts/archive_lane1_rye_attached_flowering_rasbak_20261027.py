#!/usr/bin/env python3
"""Install ONE genuinely attached flowering rye ear (Rasbak, CC BY-SA 3.0).
Also keep pre-existing noncommercial-only photograph in archive but off
unrestricted public learner, and correct old ligule teaching text.
"""
import io,json,time,hashlib,pathlib,urllib.request
from PIL import Image

base=pathlib.Path("content/taxa/Poaceae/Secale/secale-cereale")
card=base/"species.json"
name="rasbak-rye-attached-flowering-ear-anthers-awns-cc-by-sa3.jpg"
dest=base/"images"/name
page="https://commons.wikimedia.org/wiki/File:Secale_cereale_flowering,_rogge_bloeiend_(4).jpg"
original="https://upload.wikimedia.org/wikipedia/commons/4/41/Secale_cereale_flowering%2C_rogge_bloeiend_%284%29.jpg"
d=json.loads(card.read_text(encoding="utf-8"))
assert d["id"]=="secale-cereale"
existing=d.get("images",[])
assert len(existing)>=5,"Unexpected photo-card state, prevent clobber"
if not any(x.get("file")=="images/"+name for x in existing):
    assert not dest.exists() and not any(x.get("source_page")==page for x in existing),"Already archived under other name: do not duplicate"
    raw=None
    for k in range(4):
        try:
            req=urllib.request.Request(original,headers={"User-Agent":"HaysBotanyFieldLearner/1.0 (public CC BY-SA photo with author citation)"})
            with urllib.request.urlopen(req,timeout=50) as r:
                raw=r.read()
            break
        except Exception as exc:
            print("Source retry",k+1,str(exc),flush=True)
            if k==3:raise
            time.sleep(5*(k+1))
    assert raw and 400000<len(raw)<6500000,f"unexpected download {len(raw) if raw else 0}"
    img=Image.open(io.BytesIO(raw));img.load()
    assert img.format=="JPEG" and img.size==(3680,5520),f"original wrong resolution {img.size}"
    img=img.convert("RGB")
    img.thumbnail((2600,2600),Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True,exist_ok=True)
    img.save(dest,"JPEG",quality=91,optimize=True)
    info={
      "file":"images/"+name,
      "role":"REAL mature, ATTACHED actively flowering ear of actual Secale cereale with dozens of true awns and dangling yellow anthers on long filaments. Entire ear and connection to culm are visible, not an excised spikelet or false ligule.",
      "creator":"Rasbak",
      "license":"CC BY-SA 3.0",
      "license_url":"https://creativecommons.org/licenses/by-sa/3.0/",
      "source_page":page,
      "source_original":original,
      "source_taxon_name":"Secale cereale",
      "source_year":2013,
      "public_reuse":"Photographer Rasbak gives Creative Commons Attribution-ShareAlike 3.0 at individual Commons page, including commercial reuse with credit and adaptation notice.",
      "photo_review":"Pixel-reviewed full 960px preview and original 3680x5520: standing living reproductive stalk, slender green-blue ear and multiple straw-yellow dangling anthers with long slender awns. No measurable glume or leaf blade junction in this photo.",
      "image_dimensions_original":[3680,5520],
      "image_dimensions_archived":[img.width,img.height],
      "image_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
      "modifications":"Downscaled original preserving full subject; RGB JPEG re-encoded GPS/EXIF-free; arrows in web overlays only."
    }
    d.setdefault("images",[]).append(info)
else:
    assert dest.is_file(),"Card cites absent original"
    print("Previously archived rye actual flowering original; metadata already exists")
panels=d.setdefault("visual_comparison",{}).setdefault("items",[])
url="content/taxa/Poaceae/Secale/secale-cereale/images/"+name
if not any(p.get("image_url")==url for p in panels):
    panel={
      "label":"ACTUAL FLOWERING RYE EAR — long awns and dangling yellow pollen anthers (Rasbak)",
      "scientific_name":"Secale cereale",
      "image_url":url,
      "image_fit":"contain",
      "creator":"Rasbak",
      "license":"CC BY-SA 3.0",
      "license_url":"https://creativecommons.org/licenses/by-sa/3.0/",
      "source_page":page,
      "image_role":"One continuous living Secale cereale ear attached to a culm, multiple genuine awns extending up and outward, yellow pollen anthers on filaments. Not dissected individual glumes.",
      "caption":"Rasbak's photograph of genuinely flowering cereal rye: follow the densely arranged upright ear, pointed awns, and hanging yellow anthers. Compare the separate Matt Lavin detached spikelets and Stefan.lefnaer measured inner ligule views. These are DIFFERENT specimens—not same-plant dissections.",
      "why_it_matters":"Fills the missing clear entire-attached reproductive role, enabling field crew to link a living rye flower head to already archived microscopic spikelet and collar material.",
      "markers":[
        {"label":"Long upward-pointing awns","label_x":3,"label_y":13,"target_x":54,"target_y":23},
        {"label":"Dangling yellow pollen anthers","label_x":56,"label_y":80,"target_x":47,"target_y":49}
      ],
      "photo_status":"Genuine gross reproductive structures visibly inspected in original photo; no fabricated individual glume or anther-length claims. Final mobile arrow overlay QA remains."
    }
    panels.insert(0,panel)
nc=[i for i in d["images"] if "CC BY-NC" in (i.get("license") or "")]
for i in nc:
    i["public_gallery_eligibility"]="HOLD_CC_BY_NC"
    i["public_reuse"]="Original restricted to noncommercial study; kept as physical archive and provenance, excluded from unrestricted public lesson."
for p in panels:
    if "CC BY-NC" in (p.get("license") or ""):
        p["public_gallery_eligibility"]="HOLD_CC_BY_NC"
d["visual_comparison"]["title"]="Cereal rye — real flowering ear, actual membranous ligule, and detached paired florets"
d["visual_comparison"]["subtitle"]="First a real attached flowering ear with awns and yellow anthers. Then precise locally archived Stefan.lefnaer 3mm true ligule / 10mm collar images, followed by Matt Lavin actual detached mature spikelets. One CC BY-NC research image is withheld from the public learner."
q=d.setdefault("field_photo_quickcheck",{})
q["heading"]="Rye: flowering ear → measured true ligule/collar → individual mature spikelet"
q["featured_photo_indices"]=[len(d["images"])-1,3,4,1,2]
q["steps"]=[
 "FIRST see Rasbak's source-labelled photo of an attached flowering rye ear: narrow green-blue ear with upward-pointing awns and yellow hanging pollen anthers. This is authentic reproductive architecture, not an isolated spikelet.",
 "NEXT open the TRUE INNER BLADE–SHEATH JUNCTION: Stefan.lefnaer's verified original photo shows a short membranous rye ligule on the inner side with a photographed 3-mm reference; don't call the outer sheath margin the ligule.",
 "LOOK AT COLLAR AND AURICLES: another Stefan.lefnaer panel contains four real rye collar and sheath views with a 10-mm reference. Use them to learn ear-like clasping projections versus the little inner ligule.",
 "FINALLY inspect the two detached Matt Lavin rye spikelet photographs: two comparatively large florets and small paired glumes; their individual insertions are not safely arrow-labelled yet and no same-plant dissection has been recorded.",
 "NEXT PHOTOGRAPH NEEDED: a rooted entire rye plant showing fibrous crown and flowering culms in one view, beside photographed wheat, barley or wildrye ears at matched scale.",
 "PUBLIC PHOTO RIGHTS: one older CC BY-NC research photo stays archived but is excluded from the unrestricted public learner."
]
q["warning"]="Six physically archived rye photos, five public eligible and one CC BY-NC held. Real inner ligule and four collar views with rulers ARE installed; these were missing only in old lesson wording. Attached actual flowering ear now present, but rooted whole plant and matching wheat/barley comparisons absent. Same-specimen dissected glume/lemma/original scale still unverified; mobile photo-arrow and site QA outstanding."
q["field_rule"]="Pair a true attached rye ear with the measured true inner ligule and real detached large florets; compare entire mature rye spikelets to wheat, barley and wildrye before confirming from awns alone."
d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
d["curation_status"]["lane1_rye_attached_rasbak_20261027"]="REAL_CC_BY_SA_ATTACHED_YELLOW_ANTHERS_AND_AWNS_ARCHIVED_OLD_NC_PHOTO_HELD_OUT"
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Six rye photos archived (5 public-eligible, one old NC research hold); source-provenanced attached flowering ear, measured true inner membranous ligule/collar series, and detached actual mature spikelets documented. Rooted entire plant and same-scale lookalike photos remain open."
d["photo_note"]=(d.get("photo_note") or "")+" 2026-10-27: genuine attached rye ear with awns and yellow anthers from Rasbak CC BY-SA3 installed; 2 gross arrow markers, local GPS-clean JPEG. Changed old noncommercial one-photo learner hold and reconciled pre-existing scaled TRUE ligule photo teaching, no root/base/scaled mature glume dissection claims."
card.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"archived":str(dest),"photo_count":len(d["images"]),"panels":len(panels),"new_source":page,"public_eligible_count":len(d["images"])-len(nc),"bytes":dest.stat().st_size}))

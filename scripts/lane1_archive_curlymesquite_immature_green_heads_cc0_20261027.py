#!/usr/bin/env python3
"""Archive verified CC0 exact Hilaria belangeri earlier green/purple attached flowering heads.

Photo fills stage progression (earlier unopened heads), not true inner ligule,
dissected sexed central/lateral spikelets or rooted node. True visible arrows only.
"""
import io, json, pathlib, time, hashlib, urllib.request
from PIL import Image, ImageOps

base=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-belangeri")
card=base/"species.json"
filename="patrick-alexander-curlymesquite-young-green-purple-heads-cc0.jpg"
dst=base/"images"/filename
page="https://commons.wikimedia.org/wiki/File:Hilaria_belangeri_-_Flickr_-_aspidoscelis_(1).jpg"
original="https://upload.wikimedia.org/wikipedia/commons/4/49/Hilaria_belangeri_-_Flickr_-_aspidoscelis_%281%29.jpg"
data=json.loads(card.read_text(encoding="utf-8"))
assert data.get("id")=="hilaria-belangeri"
if any(p.get("file")=="images/"+filename for p in data.get("images",[])):
    assert dst.exists(), "Metadata cites absent photo"
    print("EXISTS_ALREADY")
    raise SystemExit(0)
assert not dst.exists() and not any(p.get("source_page")==page for p in data.get("images",[])), "Duplicate source"
raw=None
for attempt in range(4):
    try:
        req=urllib.request.Request(original,headers={"User-Agent":"HaysBotanyFieldLearner/1.0 (credit CC0 photographer source)"})
        with urllib.request.urlopen(req,timeout=50) as response:
            raw=response.read()
        break
    except Exception as exc:
        print("download retry",attempt+1,str(exc),flush=True)
        if attempt==3:raise
        time.sleep(4*(attempt+1))
assert raw and 200000<len(raw)<6000000, "Unexpected source bytes"
im=Image.open(io.BytesIO(raw));im.load()
assert im.format=="JPEG" and im.size==(3600,2400), f"Wrong source original {im.format} {im.size}"
im=ImageOps.exif_transpose(im).convert("RGB")
im.thumbnail((2400,2400),Image.Resampling.LANCZOS)
dst.parent.mkdir(parents=True,exist_ok=True)
im.save(dst,"JPEG",quality=91,optimize=True)
photo={
 "file":"images/"+filename,
 "role":"Exactly identified true attached Hilaria belangeri upright flowering spikes at earlier green/yellow to purple-brown stage; three flowering stalks show still relatively closed narrow repeated units. No actual leaf collar, measured glume, isolated sexed triad or rooted node.",
 "creator":"Patrick Alexander",
 "license":"CC0 1.0",
 "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
 "source_page":page,
 "source_original":original,
 "source_flickr_photo":"https://www.flickr.com/photos/aspidoscelis/24126379618/",
 "source_taxon_name":"Hilaria belangeri",
 "source_locality":"Thompson Canyon, Big Burro Mountains, Grant County, New Mexico, 13 Aug 2017 (NOT Texas)",
 "public_reuse":"CC0 1.0 Commons file-specific dedication independently checked; photographer voluntarily credited",
 "photo_review":"Original 3600x2400, three sharp upright attached H. belangeri seedheads on natural ocher background; plump closed green/purple groups. Arrows only to complete visually obvious heads, NOT central fertile/lateral male spikelet or glume/lemma sexing.",
 "image_dimensions_original":[3600,2400],
 "image_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
 "modifications":"Downscaled without crop, GPS/EXIF removed, only non-destructive web arrow overlays"
}
data.setdefault("images",[]).append(photo)
panel={
 "label":"IMMATURE CURLYMESQUITE HEADS — real green-purple attached flowering groups (CC0)",
 "scientific_name":"Hilaria belangeri",
 "image_url":"content/taxa/Poaceae/Hilaria/hilaria-belangeri/images/"+filename,
 "image_fit":"contain",
 "creator":"Patrick Alexander",
 "license":"CC0 1.0",
 "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
 "source_page":page,
 "image_role":"Actual three erect attached Hilaria belangeri heads with earlier purple-brown and yellow-green unopened reproductive groups; not dissected three sexed spikelets.",
 "caption":"Real curlymesquite in the Big Burro Mountains of New Mexico. Notice THREE slender upright heads: early green-to-purple closed flowering groups form tightly packed spikes. Compare with the separate later purple opened and pale papery mature heads. These are stage differences, not evidence for specific individual glume or central-versus-lateral spikelet sex.",
 "why_it_matters":"Helps beginner crews avoid ruling out curlymesquite just because the flowering clusters have not opened pale and papery yet.",
 "markers":[
  {"label":"Young green-purple attached flowering head","label_x":2,"label_y":16,"target_x":24,"target_y":28},
  {"label":"Separate young head on attached stem","label_x":67,"label_y":83,"target_x":49,"target_y":42}
 ],
 "photo_status":"Source original visually confirmed for whole heads and flowering groups only; mobile arrow alignment QA pending. Exact tiny sexed spikelets not arrow-labelled."
}
panels=data.setdefault("visual_comparison",{}).setdefault("items",[])
assert not any(x.get("image_url")==panel["image_url"] for x in panels)
index=next((i for i,p in enumerate(panels) if p.get("scientific_name")!="Hilaria belangeri"),len(panels))
panels.insert(index,panel)
data.setdefault("curation_status",{})["photo_files_present"]=len(data["images"])
data["curation_status"]["lane1_curlymesquite_young_heads_cc0_20261027"]="TRUE_EARLY_STAGE_EXACT_SPECIES_PUBLIC_CC0_IMAGE_TWO_GROSS_HEAD_ARROWS_NO_LIGULE_CLAIM"
data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
data["learner_visual_status"]["note"]="Curlymesquite actual attached earlier green/purple heads, developed purple and mature pale papery clusters photographed along with connected aboveground stolons. No free inner ligule, scale-matched sexed triad, visibly rooted stolon node or mobile arrow QA confirmed."
data["photo_note"]=(data.get("photo_note") or "")+" 2026-10-27: actual Patrick Alexander CC0 early green/purple stage heads installed, two arrows on complete heads only; all existing photographer attribution retained. Reproductive stage improved but six-role score unchanged."
card.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"installed":str(dst),"photos":len(data["images"]),"panels":len(panels),"bytes":dst.stat().st_size,"sha256":photo["image_sha256"]}))

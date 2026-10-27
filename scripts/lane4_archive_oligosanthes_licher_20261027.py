#!/usr/bin/env python3
"""Photo-level CC BY-SA candidate archiver: Max Licher exact D. oligosanthes photos.
No role-score increment until archived pixels independently reviewed. Preserve
CC BY-SA with unspecified license version; do not invent a Creative Commons version.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-oligosanthes")
CARD=ROOT/"species.json"
SOURCE=ROOT/"image-sources.csv"
PAGE="https://yavapaiplants.extension.arizona.edu/dichanthelium-oligosanthes"
BASE="https://yavapaiplants.extension.arizona.edu/sites/default/files/"
FILES=[
 ("1","max-licher-oligosanthes-leaf-plant.jpg","LIVE TUFT AND GREEN LEAVES — Arizona source exact species",
  "Actual living D. oligosanthes tuft with multiple narrow green basal and stem leaves, young flowering heads above rocky soil; roots and exposed free ligule NOT shown.",
  "Image credited Leaves at University of Arizona Yavapai Extension; many genuine green leafy culms at the soil surface, some flowering branches; NOT proof of buried roots, belowground caudex, true ligule or subspecies."),
 ("2","max-licher-oligosanthes-field-habit.jpg","ACTUAL LIVE PLANT GROWTH FORM — Arizona field view",
  "Actual D. oligosanthes growing in rocky habitat, with abundant low and erect green shoots from a dense grassy base; no dug crown or true collar.",
  "University of Arizona's Plant photograph by Max Licher; the interconnected green shoots and foliage give beginner field-scale context. No excavated roots, measured spikelet or inner ligule."),
 ("0","max-licher-oligosanthes-seedhead-close.jpg","SEEDHEAD REPRODUCTIVE CLOSE-UP — actual mature-looking oval spikelets",
  "Actual attached ovoid green spikelets and fine branching panicle; real organ contours and dark reproductive remnants, no 1mm ruler/glume dissection.",
  "Real Max Licher source-credited Seedhead picture shows the branching panicle with many green oval spikelets, some dark projecting parts; individual mature glume versus lemma faces are NOT isolated or measured.")
]
def grab(url,limit=16000000):
    err=None
    for n in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany-Lane4/1.0 (educational licensed photograph archive; github.com/Crking92/Hays-County-Botany)","Accept":"image/webp,image/jpeg,image/*;q=0.8,*/*;q=0.1"})
            with urllib.request.urlopen(req,timeout=50) as response:
                data=response.read(limit+1)
                if len(data)>limit:raise ValueError("oversize")
                return data
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            err=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
            time.sleep(2*(n+1))
    raise RuntimeError(repr(err))
def main():
    html=grab(PAGE,3000000).decode("utf-8","replace")
    assert "Dichanthelium oligosanthes" in html and "Max Licher" in html, "Source page no longer authenticates taxon/photographer"
    assert "Creative Commons Attribution-ShareAlike" in html, "Missing original photo-level license words"
    d=json.loads(CARD.read_text(encoding="utf-8"));assert d["id"]=="dichanthelium-oligosanthes"
    new=[];held=[];rows=[]
    for no,file,label,role,caption in FILES:
        filename="Dichanthelium_oligosanthe_"+no+"_ML.jpg"
        source=BASE+"Grasses/Images/"+filename
        public_preview=BASE+"styles/yp_card_image/public/Grasses/Images/"+filename+".webp"
        if filename not in html:
            held.append({"photo":filename,"reason":"Page did not confirm exact photo filename"});continue
        target="images/"+file
        if any(x.get("file")==target for x in d["images"]):continue
        try:
            raw=None;used=None;err=None
            for url in [source,public_preview]:
                try:
                    candidate=grab(url)
                    test=Image.open(io.BytesIO(candidate));test.verify()
                    raw=candidate;used=url;break
                except Exception as e:err=e
            if raw is None:raise RuntimeError("Could not retrieve either known matching photo "+str(err))
            pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
            assert pic.width>=550 and pic.height>=380, "Too small to teach visible growth form"
            dest=ROOT/target;dest.parent.mkdir(exist_ok=True,parents=True)
            pic.save(dest,"JPEG",quality=91,optimize=True)
            b=dest.read_bytes();proof=Image.open(io.BytesIO(b))
            assert b[:2]==bytes.fromhex("ffd8") and b[-2:]==bytes.fromhex("ffd9")
            assert not proof.getexif() and not proof.info.get("exif")
            digest=hashlib.sha256(b).hexdigest()
            metadata={"file":target,"role":role,"creator":"Max Licher","license":"CC BY-SA (version not specified by publisher)",
                "source_page":PAGE,"original_photo_url":source,"download_url":used,
                "source_taxon_name":"Dichanthelium oligosanthes",
                "source_locality":"Arizona (NOT authenticated Hays County voucher)",
                "public_reuse":"University of Arizona webpage explicitly credits photo to Max Licher and gives Creative Commons Attribution-ShareAlike (CC BY-SA); exact license version is not indicated, retain ShareAlike and link to source rather than guessing version.",
                "modifications":"Existing source JPEG or its scaled web preview re-encoded RGB JPEG, no crop, GPS/EXIF stripped; no image arrows painted.",
                "photo_status":"Original source photo authenticates exact species and credits. Archived real image with valid CC BY-SA notice; anatomy markers and new photographic-role score pending independent pixel review.",
                "archive_sha256":digest,"archived_dimensions":list(pic.size)}
            d["images"].append(metadata)
            d["visual_comparison"]["items"].append({
                "label":label,"scientific_name":"Dichanthelium oligosanthes","image_url":(ROOT/target).as_posix(),
                "image_fit":"contain","image_role":role,"caption":caption+" Photographer: Max Licher. Source: University of Arizona Yavapai County Extension, CC BY-SA version unspecified. PROVISIONAL — USER PHOTO REVIEW PENDING.",
                "why_it_matters":"One actual source-identifiable species photo, not a generic look-alike; learn verified photographed growth form only.",
                "creator":"Max Licher","license":"CC BY-SA (version unspecified)","source_page":PAGE,
                "modifications":"Uncropped source original or unaltered proportional institutional preview, saved JPEG RGB with EXIF/GPS stripped; browser labels separate from pixels.",
                "markers":[],"photo_status":"Actual source photograph archived for provisional learner review; gross visible anatomy should be inspected before adding arrows or score."})
            rows.append({"file_name":file,"role":role,"creator":"Max Licher","license":"CC BY-SA version unspecified","source_page":PAGE,"direct_url":used,
                         "study_use":"Public noncommercial field identification education","public_reuse":"Photo-specific CC BY-SA; attribution/source license credit and adaptation disclosures required, exact version unspecified",
                         "observation_id":"","photo_id":""})
            new.append({"file":target,"source":PAGE,"used_url":used,"license":"CC BY-SA version unspecified",
                        "sha256":digest,"dimensions":list(pic.size),"bytes":len(b)})
            print("ARCHIVED",file,used,flush=True)
        except Exception as e:
            held.append({"photo":filename,"reason":str(e)[:500]})
            print("HELD",filename,str(e)[:200],flush=True)
    if new:
        d["curation_status"]["photo_metadata_count"]=len(d["images"])
        d["curation_status"]["photo_files_present"]=len(d["images"])
        d["learner_visual_status"]["image_count"]=len(d["images"])
        d.setdefault("field_id_finish_pass",{})["lane4_max_licher_sources_20261027"]={
            "photos":len(new),"photo_names":[x["file"] for x in new],"new_arrows":0,
            "photo_role_gains":0,"photo_license":"Individual exact species photographs credited to Max Licher, CC BY-SA (license version not provided by page).",
            "remaining":"Inner hair-fringed ligule with mm bar, dissected mature spikelet/glume/lemma, actual excavated crown",
            "status":"Source-verified photos archived; photo pixel and live Pages QA pending"}
        d["visual_comparison"]["overlay_note"]+="\nMax Licher University of Arizona source licensed D. oligosanthes plant/leaf/seedhead real photos appended, without unverified anatomical arrows. Existing species-role photo score must be kept until source pixels reviewed and missing anatomy confirmed."
        CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        with SOURCE.open("r",encoding="utf-8",newline="") as f:
            reader=csv.DictReader(f);cols=list(reader.fieldnames);old=list(reader)
        with SOURCE.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(old+rows)
    report={"species":"Dichanthelium oligosanthes","photos_added":new,"held":held,
            "scoring":"NO new role scored pending independently inspected pixels. Historical illustration excluded from photo count. CC BY-SA license version unknown, do not write 4.0."}
    path=pathlib.Path("reports/lane4-oligosanthes-max-licher-photo-archive-20261027.json")
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()

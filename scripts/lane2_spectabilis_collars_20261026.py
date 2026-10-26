#!/usr/bin/env python3
"""Archive 2 individually licensed E. spectabilis collar/sheath photos; no invented true ligules."""
from pathlib import Path
from urllib.request import urlopen, Request
from hashlib import sha256
from PIL import Image, ImageOps
import io, json
BASE=Path("content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis")
CARD=BASE/"species.json"
REPORT=Path("reports/lane2-spectabilis-actual-collar-sheath-20261026.json")
UA={"User-Agent":"HaysBotanyLearner/1.0 (noncommercial grass education, source-attributed)"}
DATA=[
  {"photo":754582040,"obs":410304840,"file":"carrollk2015-collar-external-hairs-754582040.jpg",
   "role":"Actual live green outer leaf-blade/sheathed culm junction with visibly protruding WHITE HAIR TUFT at the junction; NOT a proven 0.2-0.4-mm inner ligule",
   "label":"COLLAR + SHEATH MOUTH: white hair tuft visible; TRUE ligule not resolved",
   "caption":"Research Grade iNaturalist source-labelled Eragrostis spectabilis from Oklahoma. Look at the small white hair tuft where the horizontal green blade meets a vertical sheathing culm. These are visible hairs near the collar, not a measured view of the extremely short INSIDE membranous/ciliate ligule. Don't confuse old dried stems with the live sheath.",
   "marks":[{"label":"White hairs at OUTER collar, not proven ligule","label_x":8,"label_y":78,"target_x":52,"target_y":61},{"label":"Blade emerging sideways from sheath","label_x":3,"label_y":34,"target_x":26,"target_y":57}]},
  {"photo":740532672,"obs":403335335,"file":"peter-quakenbush-blade-sheath-junction-740532672.jpg",
   "role":"Actual green external blade-sheath V-junction held beside fingertips, clear pointed narrow blade and upright green sheath; true inner ligule not opened",
   "label":"BLADE + SHEATH: real outside V-shaped attachment; no inner ligule exposed",
   "caption":"Research Grade iNaturalist source-labelled purple lovegrass photographed in Michigan. The outer blade separates at an angle from the sheath-wrapped upright green shoot; hairs on the surface are not a measured ligule. This view teaches where to peel open the leaf for a second true-ligule photograph.",
   "marks":[{"label":"Green outer sheath below blade insertion","label_x":7,"label_y":86,"target_x":47,"target_y":73},{"label":"Blade extending from sheath","label_x":66,"label_y":20,"target_x":66,"target_y":49}]}
]
def read(url,maxlen=11000000):
    with urlopen(Request(url,headers=UA),timeout=45) as h:
        data=h.read(maxlen+1)
        assert len(data)<=maxlen
        return data

def main():
    d=json.loads(CARD.read_text(encoding="utf-8"))
    assert d["id"]=="eragrostis-spectabilis"
    shots=[]
    for p in DATA:
        o=json.loads(read(f"https://api.inaturalist.org/v1/observations/{p['obs']}",2000000))["results"][0]
        assert o["taxon"]["name"]=="Eragrostis spectabilis" and o["quality_grade"]=="research"
        v=next(x for x in o["photos"] if x["id"]==p["photo"])
        license_code=v.get("license_code")
        assert license_code in ("cc-by","cc0","cc-by-sa","cc-by-nc","cc-by-nc-sa")
        original=v["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
        raw=read(original,11000000)
        with Image.open(io.BytesIO(raw)) as source:
            assert source.format=="JPEG"
            pic=ImageOps.exif_transpose(source).convert("RGB")
        pic.thumbnail((2200,2200))
        buf=io.BytesIO();pic.save(buf,format="JPEG",quality=89,optimize=True)
        content=buf.getvalue()
        with Image.open(io.BytesIO(content)) as check:
            assert check.format=="JPEG" and not check.getexif(),"EXIF retained"
        dest=BASE/"images"/p["file"]
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            assert dest.read_bytes()==content,"Changed previously archived photo; hold"
        else:
            dest.write_bytes(content)
        source=f"https://www.inaturalist.org/photos/{p['photo']}"
        rel="images/"+p["file"]
        lic=(v["license_code"]).upper().replace("CC-","CC ").replace("-","-")
        lurl="https://creativecommons.org/licenses/"+v["license_code"].replace("cc-","")+"/4.0/" if license_code!="cc0" else "https://creativecommons.org/publicdomain/zero/1.0/"
        if license_code=="cc-by":
            lic="CC BY 4.0 (iNaturalist photo-level code; version to reconfirm)"
        elif license_code=="cc-by-nc":
            lic="CC BY-NC 4.0 (iNaturalist photo-level code; only genuinely noncommercial website)"
        d["images"].append({
           "file":rel,"role":p["role"],"creator":v.get("attribution") or "iNaturalist photographer",
           "license":lic,"license_url":lurl,"source_page":source,"source_observation_url":f"https://www.inaturalist.org/observations/{p['obs']}",
           "license_evidence":"iNaturalist exact photo source API observation-photo license_code: "+license_code,
           "public_reuse":"Individually licensed; NC image is allowed ONLY on genuine noncommercial public educational Hays Botany learner; credit must remain visible" if "nc" in license_code else "Individually licensed CC BY public site with author and source attribution",
           "modifications":"Original JPEG converted RGB, compressed, EXIF/GPS removed, no cropping; browser SVG arrows separate",
           "photo_status":"Photo-level licensed, Research Grade exact-source ID, manually inspected 2026-10-26; exposed inner true ligule still MISSING; not a county voucher"
        })
        path="content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis/"+rel
        view={
          "label":p["label"],"scientific_name":"Eragrostis spectabilis","image_url":path,
          "image_fit":"contain","image_role":p["role"],"caption":p["caption"],
          "why_it_matters":"Practical close-up of sheath/collar anatomy as distinct from broad flowering-panicle photographs. A separate magnified peeled-open INNER ligule still required.",
          "creator":v.get("attribution") or "iNaturalist photographer",
          "license":lic,"license_url":lurl,"source_page":source,
          "photo_status":"Original source species and photo-level license verified, visible-only arrows; inner true ligule not resolved, no scale.",
          "markers":p["marks"],"modifications":"EXIF-stripped original, separate browser arrows; license/attribution retained"
        }
        if not any(x.get("image_url")==path for x in d["visual_comparison"]["items"]):
            index=next((i for i,x in enumerate(d["visual_comparison"]["items"]) if x.get("scientific_name")!="Eragrostis spectabilis"),len(d["visual_comparison"]["items"]))
            d["visual_comparison"]["items"].insert(index,view)
        shots.append({"photo_id":p["photo"],"observer":v.get("attribution"),"photo_license_code":license_code,"obs":p["obs"],"sha256":sha256(content).hexdigest(),"bytes":len(content),"image_dimensions":list(pic.size),"markers":len(p["marks"]),"image":rel})
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
    d["curation_status"]["lane2_true_sheath_collar_20261026"]="TWO REAL CC-LICENSED OUTER BLADE-SHEATH/COLLAR PHOTO PANELS ADDED, REAL TRUE LIGULE STILL MISSING"
    t=d["field_photo_quickcheck"]
    t["steps"].insert(1,"Inspect the actual close-ups now in this gallery: the Oklahoma photo shows a visible tuft of LONGER external collar hairs. The Michigan photo shows the green OUTSIDE blade/sheath V. Neither photograph reveals or measures the tiny INSIDE true membranous/ciliate ligule. The ligule must be revealed by peeling the blade away and photographing with a 1-mm scale.")
    t["warning"]+=" October 26: added TWO individually licensed Research Grade photographic collar/sheath panels with four gross arrows. One NC image is only conditionally usable on this genuinely noncommercial learner. Neither reveals true measured inner ligule; keep this photo hold."
    d["field_id_finish_pass"]["photo_evidence_limits"]+=" October 26 Research Grade original field photos added for sheath and OUTER collar hairs; short true inner ligule and scale remain unphotographed, no photo anatomy completion claim."
    d["photo_note"]=d.get("photo_note","")+"\n2026-10-26 Lane 2 added physical Research Grade exact-spp sheath/collar pair, with CC BY-NC/CC BY separate rights and visible-only arrow coordinates; no ligule completion."
    if isinstance(d.get("learner_visual_status"),dict):d["learner_visual_status"]["image_count"]=len(d["images"])
    CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"species":"Eragrostis spectabilis","photos":shots,"new_images":2,"actual_collars":1,"external_sheath_junctions":2,"new_markers":4,"true_inner_ligule":"MISSING, not shown","scientific_status":"FIELD_READY_PHOTO_GAPS","noncommercial_NC_condition":"Preserve attribution; re-check before any monetization."},indent=2)+"\n",encoding="utf-8")
    print("ARCHIVE_AND_CARD_OK",len(shots),"local",d["curation_status"]["photo_files_present"])
if __name__=="__main__":main()

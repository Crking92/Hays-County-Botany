#!/usr/bin/env python3
"""Archive exact Paspalum setaceum Goldman CC BY-SA anatomy images.

Five source-verified species-specific photographs inspected as Commons JPEG
previews on 2026-10-27. Preserve precise photo license and credit;
no claim of Hays native voucher or millimeter measurements. Ignore all OTHER taxa.
"""
import csv, hashlib, html, io, json, pathlib, re, time, urllib.parse, urllib.request, urllib.error
from PIL import Image, ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-setaceum")
CARD=BASE/"species.json";SOURCES=BASE/"image-sources.csv"
SCORE=pathlib.Path("reports/lane4-six-role-photographic-progress-20261027.json")
LICENSE_URL="https://creativecommons.org/licenses/by-sa/4.0/"
# Web source previews viewed independently; coordinate markers describe ONLY visible parts.
ITEMS=[
 ("S2","goldman-paspalums2-leaf-base-hairs.jpg",
  "Real leaf blade base, paired blade/sheath junction and hairs", "LEAF BASE — inner blade-sheath junction and visible long hairs",
  "Photographer's exact species P. setaceum. See two green leaf blades and fine pale hairs emerging by their bases. Do not call exterior hairs the free ligule or infer millimeter length.",
  [{"label":"Hairs near leaf base (not ligule)","label_x":5,"label_y":81,"target_x":38,"target_y":66},
   {"label":"Leaf bases at stem junction","label_x":66,"label_y":87,"target_x":49,"target_y":67}]),
 ("S3","goldman-paspalums3-true-stem-node.jpg",
  "Actually photographed ring-like stem node on culm", "STEM NODE — genuine ring across thin paspalum culm",
  "The paler swollen joint dividing the lower and upper green-brown culm segments is the actual NODE; not a leaf collar or underground rhizome.",
  [{"label":"Visible stem node","label_x":5,"label_y":62,"target_x":61,"target_y":55}]),
 ("S4","goldman-paspalums4-ligule.jpg",
  "Inner blade-sheath junction and photographed brown true ligule region; exact free flap length not scaled",
  "ACTUAL LIGULE — brown membranous margin at the opened leaf junction",
  "Goldman's P. setaceum photo is captioned Ligule at Wikimedia Commons. The frayed brown tissue along the inner sheath mouth is visible next to the green blade; neighboring white hairs are separate. Membrane height 0.2–1mm cannot be measured here. Species photographed in NC, not Hays.",
  [{"label":"Brown ligule at sheath rim","label_x":73,"label_y":18,"target_x":59,"target_y":46},
   {"label":"Inner sheath mouth","label_x":7,"label_y":77,"target_x":48,"target_y":50}]),
 ("S5","goldman-paspalums5-rachis-underside.jpg",
  "Real inflorescence rachis with paired green spikelets on alternating sides; unscaled",
  "FLOWERING RACHIS — paired spikelets attach along the wavy axis",
  "One side of the narrow branching spikelet-bearing axis; paired oval spikelets project along its edges. This is not the separated upper glume or lemma; no ruler in the image.",
  [{"label":"Green rachis axis","label_x":6,"label_y":18,"target_x":50,"target_y":54},
   {"label":"Attached pale spikelet","label_x":67,"label_y":83,"target_x":41,"target_y":55}]),
 ("S7","goldman-paspalums7-spikelet-faces.jpg",
  "Close reproductive anatomy: true attached P. setaceum oval spikelet faces in a row; no detached dissection or mm bar",
  "ACTUAL SPIKELET FACES — paired pale flattened spikelets along the rachis",
  "Clearly photographed oval pale spikelets attached to the one-sided green flowering axis; subtle bands and shape are visible. Without dissection and a 1-mm scale, this cannot identify individual hard fertile lemma, upper glume, or exact variety.",
  [{"label":"Flattened oval spikelet face","label_x":5,"label_y":15,"target_x":42,"target_y":54},
   {"label":"Green spikelet-bearing axis","label_x":72,"label_y":16,"target_x":66,"target_y":51}])
]
def get(url,limit=15000000):
    err=None
    for n in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (CC-by-SA diagnostic teaching; github.com/Crking92/Hays-County-Botany)"})
            with urllib.request.urlopen(req,timeout=55) as rsp:
                data=rsp.read(limit+1)
            if len(data)>limit:raise ValueError("Media too large")
            return data
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as ex:
            err=ex
            if isinstance(ex,urllib.error.HTTPError) and ex.code not in (429,500,502,503,504):raise
            time.sleep(2*(n+1))
    raise RuntimeError(str(err))
def trim(x):
    return html.unescape(re.sub(r"<[^>]+>"," ",x or "")).strip()
def main():
    card=json.loads(CARD.read_text(encoding="utf-8"));assert card["id"]=="paspalum-setaceum"
    audit=json.loads(SCORE.read_text(encoding="utf-8"))
    one=next(x for x in audit["species"] if x["id"]=="paspalum-setaceum")
    with SOURCES.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
    photo_list=[];added=[];held=[]
    for n,name,role,label,caption,arrows in ITEMS:
        title="File:Paspalum"+n+".jpg"
        srcpage="https://commons.wikimedia.org/wiki/"+title
        finalname="images/"+name
        if any(x.get("file")==finalname for x in card["images"]):
            print("Existing "+name,flush=True)
            continue
        try:
            args=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
                   "iiprop":"url|extmetadata|sha1|size","iiurlwidth":1600,"titles":title})
            result=json.loads(get("https://commons.wikimedia.org/w/api.php?"+args,5000000))
            entry=next(iter(result["query"]["pages"].values()))
            assert entry["title"].lower()==title.lower(),(entry["title"],title)
            info=entry["imageinfo"][0];meta=info.get("extmetadata",{})
            lic=re.sub("[^a-z0-9]","",trim(meta["LicenseShortName"]["value"]).lower())
            creator=trim(meta["Artist"]["value"])
            desc=trim(meta.get("ImageDescription",{}).get("value",""))
            assert lic=="ccbysa40",f"Wrong source license: {lic}"
            assert "Douglas Goldman" in creator,f"Wrong image creator: {creator}"
            assert "Paspalum setaceum" in desc or "paspalum setaceum" in desc.lower(),f"Wrong exact species description: {desc}"
            assert info["width"]>=1800 and info["height"]>=1200
            url=info.get("thumburl") or info["url"]
            domain=urllib.parse.urlparse(url).hostname or ""
            assert domain.endswith(".wikimedia.org"),f"Untrusted CDN: {domain}"
            raw=get(url)
            test=Image.open(io.BytesIO(raw));test.verify()
            pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
            assert min(pic.size)>=900
            destination=BASE/finalname;destination.parent.mkdir(parents=True,exist_ok=True)
            pic.save(destination,"JPEG",quality=91,optimize=True)
            saved=destination.read_bytes()
            assert saved[:2]==bytes.fromhex("ffd8") and saved[-2:]==bytes.fromhex("ffd9")
            local=Image.open(io.BytesIO(saved))
            assert local.size==pic.size and not local.getexif() and "exif" not in local.info
            sha256=hashlib.sha256(saved).hexdigest()
            card["images"].append({
              "file":finalname,"role":role,"creator":"Douglas Goldman","license":"CC BY-SA 4.0",
              "license_url":LICENSE_URL,"source_page":srcpage,"source_taxon_name":"Paspalum setaceum",
              "photo_date":"2011-08-17","photo_locality":"Davidson County, North Carolina, NOT a Texas voucher",
              "public_reuse":"Original photographer released this individual image CC BY-SA 4.0 on Wikimedia Commons, changes indicated. Photo remains CC BY-SA 4.0 when adapted.",
              "photo_status":"Correct exact-species source and licensed original seen as Commons photographic preview 2026-10-27. Genuine organ and gross markers visible; free membrane precise measurement and separated glume/lemma not proven.",
              "modifications":"Uncropped proportional thumbnail JPEG re-encoded RGB to remove EXIF/GPS; browser arrows separate from image pixels and credited adapted view licensed CC BY-SA 4.0.",
              "original_commons_sha1":info.get("sha1"),
              "archive_sha256":sha256,"archived_dimensions":list(pic.size)})
            card["visual_comparison"]["items"].append({
              "label":label,"scientific_name":"Paspalum setaceum",
              "image_url":(BASE/finalname).as_posix(),"image_fit":"contain",
              "image_role":role,"caption":caption,
              "why_it_matters":"Species-specific diagnostic actual photo, not a taxon-substitute illustration or general distant habit view. Compare seen structures only.",
              "creator":"Douglas Goldman","license":"CC BY-SA 4.0","license_url":LICENSE_URL,
              "source_page":srcpage,
              "modifications":"Image EXIF removed and JPEG proportionally resized; browser overlay labels added separately. Modified educational presentation follows CC BY-SA 4.0.",
              "photo_status":"EXACT SPECIES CC BY-SA licensed real JPG installed; source preview pixel inspected, provisional user review; anatomical arrow coordinates gross-only.",
              "markers":arrows})
            row={"file_name":name,"role":role,"creator":"Douglas Goldman","license":"CC BY-SA 4.0",
             "source_page":srcpage,"direct_url":info["url"],"study_use":"Public noncommercial botanical visual learner",
             "public_reuse":"Attribution and ShareAlike 4.0, modification disclosed, GPS stripped","observation_id":"","photo_id":""}
            photo_list.append(row)
            added.append({"file":finalname,"source":srcpage,"license":"CC BY-SA 4.0","sha256":sha256,"size":len(saved),"dimensions":list(pic.size)})
            print("ARCHIVED "+finalname+" "+sha256,flush=True)
        except Exception as e:
            held.append({"filename":title,"error":str(e)[:300]});print("HELD "+title+" "+str(e)[:300],flush=True)
    if not added:
        print("No licensed new originals installed: "+json.dumps(held),flush=True)
        return
    if isinstance(card.get("curation_status"),dict):
        card["curation_status"]["photo_metadata_count"]=len(card["images"])
        card["curation_status"]["photo_files_present"]=len(card["images"])
    card.setdefault("learner_visual_status",{})["image_count"]=len(card["images"])
    card.setdefault("field_id_finish_pass",{})["goldman_diagnostic_20261027"]={
      "installed_photo_count":len(added),"new_markers":sum(len(row[6]) for row in ITEMS if ("goldman-paspalum"+row[0].lower()+"-" in " ".join(z["file"] for z in added))),
      "photo_sources":[x["source"] for x in added],
      "quality_rule":"Ligule true brown rim visible but not 1mm measured; paired oval spikelets visible but no detached glume/lemma separate; no real rooted rhizome.",
      "licensing":"Photographer Douglas Goldman individual Wikimedia Commons CC BY-SA 4.0 with source links; EXIF stripped",
      "pages":"PENDING separate release"}
    present={x["file"] for x in added}
    if "images/goldman-paspalums4-ligule.jpg" in present and one["role_scores"][2]==0:
        one["role_scores"][2]=0.5
    if "images/goldman-paspalums7-spikelet-faces.jpg" in present and one["role_scores"][4]==0.5:
        one["role_scores"][4]=1
    before=one["total"];total=sum(one["role_scores"])
    one.update({"previous_total":before,"previous_pct":round(before/6*100),
       "total":total,"pct":round(total/6*100),
       "target_status":"at_70_80" if total>=4.5 else "below_70",
       "new_species_photos":one.get("new_species_photos",0)+len(added),
       "own_species_physically_archived":len(card["images"]),
       "gallery_panels":len(card["visual_comparison"]["items"]),
       "new_gross_arrows":sum(len(z["markers"]) for z in card["visual_comparison"]["items"] if z.get("source_page","").startswith("https://commons.wikimedia.org/wiki/File:PaspalumS")),
       "remaining":"actual scaled opened free ligule with 1mm reference, dissected ripe glume+lemma with 1mm reference, connected short rooted rhizome",
       "site_qa":"NOT YET VERIFIED"})
    audit["confirmed_at_or_above_70"]=sum((x.get("pct") or 0)>=75 for x in audit["species"])
    audit["photo_physical_progress_today"]["new_local_originals"]+=len(added)
    audit["photo_physical_progress_today"]["new_gross_arrows"]+=sum(len(z["markers"]) for z in card["visual_comparison"]["items"] if z.get("source_page","").startswith("https://commons.wikimedia.org/wiki/File:PaspalumS"))
    audit["progress_disclaimer"]="Photo-only Lane4 Goldman licensed and viewed exact Paspalum setaceum anatomical photos. Actual inner collar photo partial (no mm scale), reproductive paired faces full, rooted base still 0; current P. setaceum "+str(one["pct"])+"%, site/mobile QA pending."
    card.setdefault("photo_targets",[])
    card["field_id_finish_pass"]["goldman_diagnostic_20261027"]["six_roles"]=one["role_scores"]
    card["field_id_finish_pass"]["goldman_diagnostic_20261027"]["six_role_total"]=total
    card["photo_note"]+="\n2026-10-27: Added "+str(len(added))+" source-verified Douglas Goldman Commons CC BY-SA 4.0 real images: ligule/sheath, leaf base hairs, stem node, spikelet rachis and paired actual spikelet faces. Annotated ONLY clearly observed gross structures, non-Texas photo source noted. Rhizome and individually dissected/scale-verified upper glume + fertile lemma remain absent."
    with SOURCES.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=columns);w.writeheader();w.writerows(rows+photo_list)
    CARD.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    SCORE.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"added":added,"held":held,"score":one["total"],"pct":one["pct"],"roles":one["role_scores"],"gallery":len(card["visual_comparison"]["items"]),"images":len(card["images"])}),flush=True)
if __name__=="__main__":main()

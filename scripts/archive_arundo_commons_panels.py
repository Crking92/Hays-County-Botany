#!/usr/bin/env python3
"""Archive two existing Arundo Commons teaching panels only after Commons image-level rights checks."""
import io, json, pathlib, re, urllib.parse, urllib.request, hashlib, html
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Arundo/arundo-donax/species.json")
s=json.loads(p.read_text()); outcomes=[]
for item in s["visual_comparison"]["items"]:
    url=item.get("image_url","")
    if not (url.startswith("https://upload.wikimedia.org/") and ("Arundo_donax_ligule_" in url or "Arundo_donax_flowerhead1_" in url)): continue
    source=item.get("source_page") or ("https://commons.wikimedia.org/wiki/File:"+urllib.parse.unquote(url.split("/thumb/")[-1].split("/")[-2]))
    try:
        filename=urllib.parse.unquote(source.split("/wiki/File:",1)[1]).replace("_"," ")
        q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+filename,"format":"json"})
        def get(u):
            req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 (licensed plant media review)"})
            with urllib.request.urlopen(req,timeout=50) as response:return response.read()
        data=json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))
        info=next(iter(data["query"]["pages"].values()))["imageinfo"][0]
        md=info["extmetadata"]
        lic=re.sub(r"[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
        original=re.sub(r"[^A-Z0-9]","",item.get("license","").upper())
        if lic!=original or lic not in ("CCBY40","CCBY30","CCBY20","CCBYSA40","CCBYSA30","CCBYSA20"):raise ValueError("license mismatch or not approved: "+lic+"/"+original)
        artist=html.unescape(re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))).strip()
        if not artist:raise ValueError("artist missing")
        raw=get(info.get("thumburl") or info["url"])
        if not 10000<len(raw)<25000000:raise ValueError("unexpected byte length")
        im=Image.open(io.BytesIO(raw));im.verify()
        im=Image.open(io.BytesIO(raw)).convert("RGB")
        if min(im.size)<250:raise ValueError("small source")
        dest=p.parent/"images"/("commons-arundo-"+hashlib.sha256(source.encode()).hexdigest()[:12]+".jpg")
        dest.parent.mkdir(parents=True,exist_ok=True)
        im.save(dest,"JPEG",quality=90,optimize=True)
        item["archived_original_image_url"]=url
        item["image_url"]=str(dest).replace("\\","/")
        item["photo_status"]="LOCALLY ARCHIVED — PROVISIONAL USER PHOTO REVIEW PENDING; visible gross structure arrows only"
        item["archive_creator_from_commons"]=artist
        item["archive_license_verified"]=md["LicenseShortName"]["value"]
        s["images"].append({"file":"images/"+dest.name,"role":item.get("image_role",""),"creator":item.get("creator") or artist,"license":item["license"],"license_url":item.get("license_url"),"source_page":source,"archived_original_url":url,"source_creator_metadata":artist,"photo_status":"LOCALLY ARCHIVED; provisional ID/anatomy"})
        outcomes.append({"source":source,"archive":str(dest),"status":"archived"})
    except Exception as e:outcomes.append({"source":source,"status":"held","reason":str(e)})
if any(o["status"]=="archived" for o in outcomes):
    s.setdefault("field_id_finish_pass",{})["commons_photo_archive_20261023"]={"results":outcomes,"status":"FIELD_READY_PHOTO_GAPS","no_new_micro_arrows":True}
    p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
report=pathlib.Path("reports/arundo-commons-photo-archive-20261023.json")
report.write_text(json.dumps({"results":outcomes},indent=2)+"\n")
print(json.dumps(outcomes))

# Exact Arundo spikelet close-up (Harry Rose): independent Commons rights and byte gate.
# This source belongs only on the Arundo learner; Phragmites photos are already
# physically archived in their OWN canonical Phragmites species gallery.
source="https://commons.wikimedia.org/wiki/File:Arundo_donax_spikelets1_(6804285202)_(2).jpg"
target_name="harry-rose-spikelets-6804285202.jpg"
if not any(x.get("source_page")==source or x.get("file")=="images/"+target_name for x in s["images"]):
    try:
        def get_once(url):
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany/1.0 (licensed educational diagnostic photo archive)"})
            with urllib.request.urlopen(req,timeout=50) as response:
                return response.read()
        title="File:Arundo donax spikelets1 (6804285202) (2).jpg"
        q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
        page=json.loads(get_once("https://commons.wikimedia.org/w/api.php?"+q))
        info=next(iter(page["query"]["pages"].values()))["imageinfo"][0]
        md=info["extmetadata"]
        lic=re.sub(r"[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
        if lic!="CCBY20":raise ValueError("source-specific license not verified as CC BY 2.0: "+lic)
        artist=html.unescape(re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))).strip()
        if "Harry Rose" not in artist:raise ValueError("expected creator not verified: "+artist)
        image_source=info["url"]
        raw=get_once(image_source)
        if not 12000<len(raw)<15000000:raise ValueError("image byte size outside safe bounds")
        with Image.open(io.BytesIO(raw)) as im:
            im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            if im.format!="JPEG" or min(im.size)<700:raise ValueError("image format or resolution insufficient")
            width,height=im.size
            # A new image object and JPEG save deliberately strip original EXIF/GPS.
            clean=im.convert("RGB")
        dest=p.parent/"images"/target_name
        dest.parent.mkdir(parents=True,exist_ok=True)
        clean.save(dest,"JPEG",quality=90,optimize=True)
        with Image.open(dest) as check:
            check.verify()
        archived_sha=hashlib.sha256(dest.read_bytes()).hexdigest()
        s["images"].append({
            "file":"images/"+target_name,
            "role":"Source-authenticated Arundo donax group of purplish mature spikelets, narrow pointed glumes and floret tips. Does NOT resolve microscopic rachilla-versus-lemma hair origin.",
            "creator":"Harry Rose (Macleay Grass Man)",
            "license":"CC BY 2.0",
            "license_url":"https://creativecommons.org/licenses/by/2.0/",
            "source_page":source,
            "source_image_url":image_source,
            "source_taxon":"Arundo donax",
            "image_dimensions":[width,height],
            "archived_sha256":archived_sha,
            "modifications":"Re-encoded JPEG, stripped EXIF/GPS; no arrows or crops",
            "photo_status":"LOCALLY ARCHIVED — PROVISIONAL USER PHOTO REVIEW PENDING; annotation_pending"
        })
        s.setdefault("visual_comparison",{}).setdefault("items",[]).append({
            "label":"GIANT REED — true photographed Arundo spikelets (hair-origin macro still needed)",
            "scientific_name":"Arundo donax",
            "image_url":str(dest).replace("\\","/"),
            "image_fit":"contain",
            "image_role":"Exact-source Arundo spikelets: purplish pointed glumes and flowering tips; hair attachment and rachilla segments not independently resolved.",
            "caption":"Real Arundo donax spikelet cluster photographed by Harry Rose in Australia. Compare overall spikelet arrangement with the SEPARATELY labelled Phragmites australis card; this image cannot by itself prove which axis bears the fine silky hairs. No scale is shown.",
            "why_it_matters":"Adds the missing species-authenticated spikelet close-up without falsely claiming measured microscopic hair origin.",
            "creator":"Harry Rose (Macleay Grass Man)",
            "license":"CC BY 2.0",
            "license_url":"https://creativecommons.org/licenses/by/2.0/",
            "source_page":source,
            "photo_status":"LOCALLY ARCHIVED — PROVISIONAL USER PHOTO REVIEW PENDING; annotation_pending",
            "markers":[]
        })
        s.setdefault("curation_status",{})["photo_metadata_count"]=len(s["images"])
        s["curation_status"]["photo_files_present"]=len(s["images"])
        s.setdefault("learner_visual_status",{})["image_count"]=len(s["images"])
        s["learner_visual_status"]["status"]="field_ready_photo_gaps"
        s["learner_visual_status"]["note"]="Harry Rose CC BY 2.0 true Arundo spikelet image physically archived after byte, metadata and JPEG checks; microscopic hair origin still missing; no new arrows. No Phragmites photos assigned to Arundo."
        s["visual_comparison"]["subtitle"]="Four earlier local Arundo photographs, one licensed JMK external rhizome reference, and one newly archived Harry Rose Arundo spikelet close-up. Phragmites macros belong to the separately labelled comparison species."
        s["visual_comparison"]["overlay_note"]=s["visual_comparison"].get("overlay_note","")+"\nNew spikelet image is physically archived with verified bytes; no new arrows; 1-mm microscopic hair-origin dissection remains a photo gap."
        p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
        outcomes.append({"source":source,"archive":str(dest),"status":"archived","sha256":archived_sha,"dimensions":[width,height],"creator":artist,"license":"CC BY 2.0","arrows_added":0})
    except Exception as e:
        outcomes.append({"source":source,"status":"held","reason":str(e),"target":"content/taxa/Poaceae/Arundo/arundo-donax/images/"+target_name,"arrows_added":0})
    report.write_text(json.dumps({"results":outcomes},indent=2)+"\n")
else:
    print("Arundo spikelet already installed; no duplicate archive.")

# Two-phase safe publication: preserve concurrent Arundo species edits during image-only archive.
# A second worker edited the canonical species file during the previous archive run.
# Keep only the verified JPEG and audit report in this commit; the species gallery
# must be merged separately with a freshly fetched SHA after image readback.
if any(o.get("status")=="archived" and o.get("archive","").endswith(target_name) for o in outcomes):
    import subprocess
    original_species=subprocess.check_output(["git","show","HEAD:"+str(p)])
    p.write_bytes(original_species)
    print("PHOTO ARCHIVED IN WORKSPACE; canonical species metadata deferred to fresh-SHA follow-up")


# ARCHIVE_VERIFIED_MDPI_ARUNDO_FIGURES_20261026
# The user's Figure 2 upload was independently identified against:
# Ngernsaengsaruay et al. (2023), Plants 12(9):1850, DOI 10.3390/plants12091850.
# Figures 2 (Paweena Wessapak) and 5 (Chatchai Ngernsaengsaruay/
# Pichet Chanton) are original article illustrations/photos under CC BY 4.0.
# The article figure is NOT a Phragmites image. Only run image download under
# the original article's CC BY attribution and with verified pixels.
# Archive image bytes only; merge canonical species.json in a fresh-SHA pass
# to avoid overwriting parallel human/lane edits.
for fig, artist, purpose in [
    ("g002", "Paweena Wessapak", "scientific reproductive-anatomy plate: panicle, spikelet, paired glumes, hairy lemma and palea"),
    ("g005", "Chatchai Ngernsaengsaruay (panels A-C); Pichet Chanton (panels D-E)",
     "photographic inflorescence, spikelet and separated glumes and florets"),
]:
    outfile=p.parent/"images"/("research-arundo-2023-"+fig+".jpg")
    if outfile.exists():
        outcomes.append({"status":"already_archived","archive":str(outfile)})
        continue
    candidates=[
        f"https://www.mdpi.com/plants/plants-12-01850/article_deploy/html/images/plants-12-01850-{fig}.png",
        f"https://mdpi-res.com/plants/plants-12-01850/article_deploy/html/images/plants-12-01850-{fig}.png",
        f"https://www.mdpi.com/plants/plants-12-01850/article_deploy/html/images/plants-12-01850-{fig}.jpg",
        f"https://europepmc.org/articles/PMC10181382/bin/plants-12-01850-{fig}.jpg",
    ]
    errors=[]
    for media_url in candidates:
        try:
            req=urllib.request.Request(media_url,headers={"User-Agent":"HaysCountyBotany/1.0 (source-attributed educational botanical figure archiving)"})
            with urllib.request.urlopen(req,timeout=22) as response:
                raw=response.read(20_000_001)
            if not (10_000 < len(raw) < 20_000_000):
                raise ValueError("unexpected size")
            with Image.open(io.BytesIO(raw)) as image_check:
                image_check.verify()
            with Image.open(io.BytesIO(raw)) as image_in:
                if min(image_in.size)<400 or image_in.width*image_in.height>30_000_000:
                    raise ValueError("figure too small/large")
                image_rgb=image_in.convert("RGB")
                dims=image_rgb.size
            outfile.parent.mkdir(parents=True,exist_ok=True)
            image_rgb.save(outfile,"JPEG",quality=91,optimize=True,exif=b"")
            with Image.open(outfile) as archived_check: archived_check.verify()
            outcomes.append({
                "status":"archived", "archive":str(outfile),"source":media_url,
                "article":"https://doi.org/10.3390/plants12091850",
                "original_figure":fig,"artist":artist,"role":purpose,
                "license":"CC BY 4.0", "license_url":"https://creativecommons.org/licenses/by/4.0/",
                "modifications":"PNG/JPEG re-encoded as RGB JPEG, metadata removed; no arrows",
                "dimensions":dims,"sha256":hashlib.sha256(outfile.read_bytes()).hexdigest(),
                "human_review":"PROVISIONAL, crop/pixel-level arrow review pending"
            })
            break
        except Exception as e:
            errors.append(type(e).__name__+": "+str(e)[:180])
    else:
        outcomes.append({"status":"held","figure":fig,"target":str(outfile),
                         "attempts":errors,"license":"CC BY 4.0", "bytes_verified":False})
# Preserve original report path consumed by the existing guarded workflow.
report.write_text(json.dumps({"results":outcomes},ensure_ascii=False,indent=2)+"\n")

#!/usr/bin/env python3
"""Lane 4: exact source-licensed Digitaria ciliaris habit and uprooted base.

Source: Wikimedia Commons files by Forest & Kim Starr with photo-level
Creative Commons license. Site files will be provisional until panel pixels
are manually inspected. D. sanguinalis comparison MUST be labelled as different
species and does not raise ciliaris exact-photo count.
"""
import csv,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Digitaria/digitaria-ciliaris")
CARD=BASE/"species.json"
SRC=BASE/"image-sources.csv"
CANDIDATES=[
  {"title":"Starr 090121-1188 Digitaria ciliaris.jpg","file":"images/starr-090121-1188-excavated-base.jpg",
   "label":"EXCAVATED SPECIMEN BASE — inspect actual roots and culm connection",
   "role":"Source-photographed D. ciliaris specimen base from Maui, potentially showing several basal stems and attached roots",
   "caution":"Original archive description 'plant specimen base'. Individual true rooted nodes or underground structures require subsequent actual pixel inspection.",
   "expected":["ccby30","ccby30us"],"creator":"Forest & Kim Starr","taxon":"Digitaria ciliaris"},
  {"title":"Starr 090121-1189 Digitaria ciliaris.jpg","file":"images/starr-090121-1189-second-base-view.jpg",
   "label":"SECOND BASE VIEW — actual source specimen from Maui",
   "role":"Second plant specimen base view from exact-source D. ciliaris archive",
   "caution":"Check base anatomy and distinguish roots from non-root culms before arrows or scoring.",
   "expected":["ccby30","ccby30us"],"creator":"Forest & Kim Starr","taxon":"Digitaria ciliaris"},
  {"title":"Starr-140909-1746-Digitaria ciliaris-habit-Wailua-Maui (24950233530).jpg",
   "file":"images/starr-140909-1746-live-habit-maui.jpg",
   "label":"LIVE HABIT — southern crabgrass growing in field",
   "role":"Source-photographed in-situ habit at Wailua, Maui, 2014; potential basal architecture",
   "caution":"Actual growth form is provisional until photo inspected; multiple overlapping plants should not be traced as one specimen.",
   "expected":["ccby30us","ccby30"],"creator":"Forest & Kim Starr","taxon":"Digitaria ciliaris"},
  {"title":"Digitaria sanguinalis subsp. sanguinalis sl1.jpg",
   "file":"images/comparison-only-digitaria-sanguinalis-spikelet-bracts-stefan.jpg",
   "label":"LOOK-ALIKE — large crabgrass DISSECTED spikelet (DIFFERENT SPECIES)",
   "role":"Actual photographer-labelled bracts of Digitaria sanguinalis, NOT D. ciliaris; learn lower/upper glumes and sterile/fertile lemmas using a separately identified species",
   "caution":"OTHER SPECIES: D. sanguinalis. This photo cannot establish any D. ciliaris glume character or improve exact-species anatomy roles by itself.",
   "expected":["ccbysa40"],"creator":"Stefan.lefnaer","taxon":"Digitaria sanguinalis subsp. sanguinalis"}
]
def get(url,size=14500000):
    err=None
    for n in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (strict CC photo identification; github.com/Crking92/Hays-County-Botany)"})
            with urllib.request.urlopen(req,timeout=60) as res:
                blob=res.read(size+1)
            if len(blob)>size:raise ValueError("Oversize")
            return blob
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            err=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in [429,500,502,503,504]:
                raise
            time.sleep(2*(n+1))
    raise RuntimeError(str(err))
def norm(s):
    return re.sub(r"[^a-z0-9]","",html.unescape(re.sub("<[^>]*>"," ",s or "")).lower())
def main():
    d=json.loads(CARD.read_text(encoding="utf-8"))
    assert d["id"]=="digitaria-ciliaris"
    with SRC.open(newline="",encoding="utf-8") as f:
        table=csv.DictReader(f); cols=list(table.fieldnames); rows=list(table)
    added=[];blocked=[]
    for c in CANDIDATES:
        if any(i.get("file")==c["file"] for i in d["images"]):
            print("Already installed: "+c["file"],flush=True);continue
        args=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata|size|sha1","iiurlwidth":1500,"titles":"File:"+c["title"]})
        try:
            resp=json.loads(get("https://commons.wikimedia.org/w/api.php?"+args,4000000))
            page=next(iter(resp["query"]["pages"].values()))
            assert page.get("title","").casefold()==("File:"+c["title"]).casefold(),repr(page.get("title"))
            info=page["imageinfo"][0];meta=info["extmetadata"]
            lic=html.unescape(re.sub("<[^>]*>"," ",meta["LicenseShortName"]["value"])).strip()
            creator=html.unescape(re.sub("<[^>]*>"," ",meta.get("Artist",{}).get("value","")))
            assert norm(lic) in c["expected"], "Different photo license "+lic
            assert c["creator"].lower().split()[-1] in creator.lower(), "Wrong author "+creator[:180]
            assert info["width"]>1300 and info["height"]>1300,"Insufficient source px"
            source="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(c["title"].replace(" ","_"),safe="()-.")
            url=info.get("thumburl") or info["url"]
            assert urllib.parse.urlparse(url).hostname.endswith("wikimedia.org"),"Untrusted image domain"
            raw=get(url)
            test=Image.open(io.BytesIO(raw));test.verify()
            pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
            assert min(pic.size)>700
            filename=BASE/c["file"];filename.parent.mkdir(parents=True,exist_ok=True)
            pic.save(filename,"JPEG",quality=91,optimize=True)
            saved=filename.read_bytes(); proof=Image.open(io.BytesIO(saved))
            assert proof.size==pic.size and not proof.getexif() and "exif" not in proof.info
            assert saved[:2]==bytes.fromhex("ffd8") and saved[-2:]==bytes.fromhex("ffd9")
            actual=(c["taxon"]=="Digitaria ciliaris")
            validlicense="CC BY-SA 4.0" if norm(lic)=="ccbysa40" else ("CC BY 3.0 US" if norm(lic)=="ccby30us" else "CC BY 3.0")
            licenseurl="https://creativecommons.org/licenses/by-sa/4.0/" if "BY-SA" in validlicense else ("https://creativecommons.org/licenses/by/3.0/us/" if "US" in validlicense else "https://creativecommons.org/licenses/by/3.0/")
            record={"file":c["file"],"role":c["role"],"creator":c["creator"],"license":validlicense,"license_url":licenseurl,
                    "source_page":source,"public_reuse":"Source exact photo Commons CC BY/SA with attribution and adaptation note. No EXIF.",
                    "photo_status":"Exact source described taxon. Source license and real media bytes validated; anatomical pixels subject to user and independent photo review. NO new arrows or six-role credits from this archiver.",
                    "modifications":"Proportional max-1500px thumbnail re-encoded RGB with EXIF/GPS stripped; no changes to actual pixel features.",
                    "archive_sha256":hashlib.sha256(saved).hexdigest(),"image_dimensions":list(pic.size),
                    "source_locality":"Maui, Hawaii (not Texas). " + ("NOT same taxon" if not actual else "Not local voucher."),
                    "source_taxon":c["taxon"]}
            # Comparator does not enter exact-species images list: avoid accidental native/taxon miscount.
            if actual:d["images"].append(record)
            panel={"label":c["label"],"scientific_name":c["taxon"],
                   "image_url":(BASE/c["file"]).as_posix(),"image_fit":"contain",
                   "image_role":c["role"],"caption":c["role"]+". "+c["caution"]+" Original by "+c["creator"]+", "+validlicense+". PROVISIONAL — USER PHOTO REVIEW.",
                   "why_it_matters":"Pictured original is a real photo with photo-level reuse permission; no species ID or arrows beyond visible pixels claimed.",
                   "creator":c["creator"],"license":validlicense,"license_url":licenseurl,"source_page":source,
                   "modifications":record["modifications"],"markers":[],
                   "photo_status":"Source-/license-verified and physically archived; visual organ audit and mobile overlay QA still required. Comparator is DIFFERENT SPECIES." if not actual else "Actual source file archived; no anatomy role assigned before independent pixel inspection."}
            d["visual_comparison"]["items"].append(panel)
            rows.append({"file_name":pathlib.Path(c["file"]).name,"role":c["role"],"creator":c["creator"],"license":validlicense,"source_page":source,
                        "direct_url":info["url"],"study_use":"Public field-ID learner","public_reuse":"CC with source/credit and modification disclosure",
                        "observation_id":"","photo_id":""})
            added.append({"file":c["file"],"actual_species":actual,"source":source,"size_bytes":len(saved),"image_dimensions":pic.size,"license":validlicense,"sha256":hashlib.sha256(saved).hexdigest()})
            print("ARCHIVED "+c["file"]+" "+str(pic.size),flush=True)
        except Exception as exc:
            blocked.append({"title":c["title"],"reason":str(exc)[:450]})
            print("HELD "+c["title"]+" : "+str(exc)[:450],flush=True)
    if added:
        d["curation_status"]["photo_metadata_count"]=len(d["images"])
        d["curation_status"]["photo_files_present"]=len(d["images"])
        d["learner_visual_status"]["image_count"]=len(d["images"])
        d["field_photo_quickcheck"]["warning"]+=" "+str(sum(x["actual_species"] for x in added))+" source-verified new real D. ciliaris images plus "+str(sum(not x["actual_species"] for x in added))+" explicit different-species photo comparison; these source pixels require role audit before count increases."
        d["visual_comparison"]["overlay_note"]+="\n2026-10-27: exact-file Wikimedia Commons sources and photo-level license/real JPEG verified. Added gross habit/base photos and explicit OTHER SPECIES D. sanguinalis labelled bract plate, NO new scientific arrows or six-role score before independent pixel audit. Source Hawaii, not local Texas."
        d["field_id_finish_pass"]["lane4_starr_ciliaris_real_sources_20261027"]={
            "exact_species_photos_added":sum(x["actual_species"] for x in added),
            "comparison_only_photo_added":sum(not x["actual_species"] for x in added),
            "new_arrows":0,"roles_gained":0,"rights_verified":True,
            "files":[x["file"] for x in added],
            "publication":"NOT VERIFIED — no automatically publishing; main requires controlled marker and QA."}
        CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        with SRC.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
            writer.writeheader();writer.writerows(rows)
    report={"photos":added,"held":blocked,"note":"Do not count as six-role gains without actual pixel audit; precise soil rooting and glume identity may remain missing."}
    p=pathlib.Path("reports/lane4-ciliaris-commons-source-pass-20261027.json");p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report),flush=True)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Single-pass publication of CC BY 3.0 AoB PLANTS Fig 5 from the original PDF.
NO SDSU media; NO lineage-specific ligule/glume inference; no recurring schedule.
"""
from io import BytesIO
from pathlib import Path
import hashlib,json,urllib.request
import fitz
from PIL import Image

PDF_SOURCES=[
 "https://repository.si.edu/bitstreams/d9bd5b90-7286-4271-9da6-f0d7f7a2a414/download",
 "https://academic.oup.com/aobpla/article-pdf/doi/10.1093/aobpla/pls040/21896657/pls040.pdf",
]
ROOT=Path("content/taxa/Poaceae/Phragmites/phragmites-australis")
SPEC=ROOT/"species.json"
NAME="aobplants-2012-fig5-hood-gulf-berlandieri-introduced-comparison.jpg"
DEST=ROOT/"images"/NAME
REPORT=Path("reports/phragmites-aob-fig5-archive-20261027.json")
PUBLIC_FILE="content/taxa/Poaceae/Phragmites/phragmites-australis/images/"+NAME
SOURCE_PAGE="https://pmc.ncbi.nlm.nih.gov/articles/PMC3676263/"
CITATION="Kettenring KM, de Blois S, Hauber DP (2012). AoB PLANTS pls040, Figure 5, doi:10.1093/aobpla/pls040; photographs by C. S. Hood"
def log(d):
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
def main():
    result={"status":"HOLD_SOURCE_NOT_VERIFIED","source":SOURCE_PAGE,
      "license":"CC BY 3.0 (article-wide statement, no separate Figure 5 rights exclusion)",
      "photographer":"C. S. Hood","copyright_note":"Proper attribution and original DOI/source link mandatory",
      "sdsu_photos_untouched":True,"new_sdsu_photos":0,
      "scope":"Source-captioned Gulf Coast berlandieri versus introduced Short A / Short B / Delta whole-stand field reference; NOT diagnosis or anatomy macro"}
    try:
      d=json.loads(SPEC.read_text())
      if any(p.get("image_url")==PUBLIC_FILE for p in d["visual_comparison"]["items"]):
         result["status"]="ALREADY_INSTALLED";log(result);return
      if any(im.get("file")=="images/"+NAME for im in d["images"]):
         raise ValueError("Image metadata exists without comparison panel; manual inspection required")
      body=None; downloaded=None; errors=[]
      for url in PDF_SOURCES:
        try:
          req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany/1.0 (educational CC attribution verification)","Accept":"application/pdf"})
          with urllib.request.urlopen(req,timeout=45) as resp:
             buf=resp.read(9000000)
          if not buf.startswith(b"%PDF-"):raise ValueError("Response was not a PDF")
          body=buf;downloaded=url;break
        except Exception as e:errors.append(str(type(e).__name__)+": "+str(e)[:140])
      if not body:raise ValueError("Source PDF could not be downloaded: "+ "; ".join(errors))
      pdf=fitz.open(stream=body,filetype="pdf")
      if len(pdf)!=18:raise ValueError("Unrecognized number of PDF pages")
      first=pdf[0].get_text()
      if not ("Kettenring" in first and "pls040" in first and
              "Creative Commons Attribution License" in first and
              "creativecommons.org/licenses/by/3.0/" in first):
         raise ValueError("Exact article CC BY 3.0 rights not confirmed")
      page=pdf[12]
      st=page.get_text()
      if not ("Fig. 5" in st and "Photographs by C. S. Hood" in st):
         raise ValueError("Original figure caption/creator mismatch")
      options=[x for x in page.get_images(full=True) if x[2]>=750 and x[3]>=600]
      if len(options)!=1:raise ValueError("Cannot unambiguously identify Figure 5 source montage")
      jpeg=pdf.extract_image(options[0][0])["image"]
      img=Image.open(BytesIO(jpeg))
      if img.size!=(809,706):raise ValueError("Unexpected source figure dimensions "+str(img.size))
      img.load()
      # Strip EXIF and preserve native legibility/labels.
      out=BytesIO()
      img.convert("RGB").save(out,format="JPEG",quality=94,optimize=True)
      jpg=out.getvalue()
      if len(jpg)<90000:raise ValueError("Unexpectedly low source image byte count")
      DEST.parent.mkdir(parents=True,exist_ok=True)
      DEST.write_bytes(jpg)
      metadata={"file":"images/"+NAME,
        "role":"Published four-way source-captioned Gulf Coast Phragmites habit comparison (Gulf berlandieri; introduced Short A, Short B and Delta). NOT a collar/ligule/glume macro.",
        "creator":"C. S. Hood","license":"CC BY 3.0",
        "license_url":"https://creativecommons.org/licenses/by/3.0/",
        "source_page":SOURCE_PAGE,"original_article_doi":"10.1093/aobpla/pls040",
        "figure":"Figure 5 (A=Gulf Coast berlandieri; B=introduced Short A; C=introduced Short B; D=introduced Delta)",
        "source_credit":CITATION,"source_taxon":"Phragmites australis (multiple research-assigned lineages)",
        "archived_dimensions":[809,706],"archived_sha256":hashlib.sha256(jpg).hexdigest(),
        "modifications":"Original image extracted from PDF; recompressed JPEG with EXIF removed, retained original A-D labels; no arrows or crops",
        "public_reuse":"CC BY 3.0 open-access article includes Figure 5 without separately stated exclusion. Attribution to C. S. Hood and cited paper/DOI required.",
        "photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; source-labelled population forms, NOT molecular certificate for any Texas specimen"}
      d["images"].append(metadata)
      panel={"label":"GULF COAST STUDY — berlandieri vs three introduced sublineages",
        "scientific_name":"Phragmites australis — four lineage/sublineage research examples",
        "image_url":PUBLIC_FILE,"image_fit":"contain",
        "image_role":"Published A-D field habit comparison, not measurable anatomy",
        "caption":"A: Gulf Coast subsp. berlandieri; B: introduced Short A; C: introduced Short B; D: introduced Delta. Source-labelled Figure 5 from Kettenring et al. 2012 (AoB PLANTS, doi:10.1093/aobpla/pls040), photos by C. S. Hood, CC BY 3.0. Shows study-population habit variation, NOT a way to classify a Hays County reed by appearance alone.",
        "why_it_matters":"One research-associated reference showing Gulf Coast berlandieri is distinct from three recognized introduced sublineages, yet whole-stand appearance is not a diagnostic genotype test.",
        "creator":"C. S. Hood","license":"CC BY 3.0","license_url":"https://creativecommons.org/licenses/by/3.0/",
        "source_page":SOURCE_PAGE,"markers":[],
        "photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; source-authenticated study labels; anatomy macro gaps unchanged"}
      d["visual_comparison"]["items"].append(panel)
      index=len(d["visual_comparison"]["items"])-1
      for tile in d.get("field_id_short_tiles",[]):
        if tile.get("heading","").startswith(("02 ·","13 ·")):
          tile.setdefault("photo_panel_indices",[])
          if index not in tile["photo_panel_indices"]:tile["photo_panel_indices"].append(index)
      d.setdefault("field_photo_quickcheck",{}).setdefault("featured_photo_indices",[])
      if index not in d["field_photo_quickcheck"]["featured_photo_indices"]:d["field_photo_quickcheck"]["featured_photo_indices"].append(index)
      d["curation_status"]["photo_metadata_count"]=len(d["images"])
      d["curation_status"]["photo_files_present"]=len(d["images"])
      d["curation_status"]["genus_photo_panels"]=len(d["visual_comparison"]["items"])
      d["photo_note"]=f"{len(d['images'])} physically archived photos and {len(d['visual_comparison']['items'])} teaching panels, 23 existing visible anatomical arrows; added attributed CC BY 3.0 Figure 5 four-way Gulf Coast whole-stand comparison, NOT ligule/glume measurements. SDSU restricted originals excluded."
      d["phragmites_aob_fig5_ccby_20261027"]={
       "panel_index":index,"photo_file":"images/"+NAME,"source_pdf":downloaded,
       "copyright":"CC BY 3.0 open access (no figure-specific exclusion noted), photo C. S. Hood",
       "status":"PHYSICALLY ARCHIVED / RIGHTS-CREDITED / PROVISIONAL PHOTO REVIEW",
       "science_holds":"No Gulf true inner ligule with 1mm scale; no source/genotype-confirmed dissected Gulf glumes. Figure 5 is field growth form only."
      }
      SPEC.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
      result.update(status="ARCHIVED_FOR_PROVISIONAL_USER_REVIEW",sha256=metadata["archived_sha256"],file=str(DEST),
       photo_count=len(d["images"]),panels=len(d["visual_comparison"]["items"]),arrows=23,panel_index=index,source_pdf=downloaded)
    except Exception as e:
      result["error"]=type(e).__name__+": "+str(e)[:700]
    log(result)
if __name__=="__main__":main()

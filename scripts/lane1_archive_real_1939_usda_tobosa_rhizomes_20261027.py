#!/usr/bin/env python3
"""Archive actual photographed scaly tobosa rhizomes from U.S. USDA 1939.

Original federal government work: R.H. Canfield USDA Technical Bulletin 681,
May 1939, fig 9 printed p 28 / PDF page 30. Print figure caption and page
text verified from OCR, exact photo clipped conservatively; NO arrows.
"""
import io,json,hashlib,pathlib,re,time,urllib.request
import fitz
from PIL import Image

url="https://ageconsearch.umn.edu/nanna/record/168453/files/tb681.pdf?registerDownload=1&version=1&withMetadata=0&withWatermark=0"
base=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-mutica")
card=base/"species.json"
name="usda-canfield-1939-real-tobosa-bisected-rhizomes-figure9-public-domain.jpg"
dst=base/"images"/name
sp=json.loads(card.read_text(encoding="utf-8"))
assert sp.get("id")=="hilaria-mutica", "Not Tobosa card"
if any(x.get("file")=="images/"+name for x in sp.get("images",[])):
 assert dst.is_file(),"Photo record exists with no bytes"
 print("ALREADY INSTALLED",flush=True)
 raise SystemExit(0)
assert not dst.exists() and not any("tb681.pdf" in x.get("source_page","") for x in sp.get("images",[])),"Already archived source"

raw=None
for attempt in range(4):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (HaysCountyConservationBotany/1.0 historic public-domain USDA photograph source)","Referer":"https://ageconsearch.umn.edu/record/168453"})
  with urllib.request.urlopen(req,timeout=65) as r:
   raw=r.read()
  break
 except Exception as ex:
  print("SOURCE RETRY",attempt,str(ex)[:180],flush=True)
  if attempt==3:raise
  time.sleep(5*(attempt+1))
assert raw and raw.startswith(b"%PDF") and 100000 < len(raw) < 60000000, "PDF download invalid"
pdf=fitz.open(stream=raw,filetype="pdf")
assert 30 <= len(pdf) <= 60, "Incorrect historic bulletin pages"
pg=pdf[29] # printed 28, PDF index 29
t=" ".join(pg.get_text().split()).lower()
assert "bisect of tobosa grass plant" in t, "The actual USDA fig 9 caption isn't verified"
assert "ruler" in t and "rhizomes" in t and "rootlike" in t, "Author's source identification missing"
assert "technical bulletin 681" in t and "1939" not in t or "technical bulletin 681" in t
# Exact page-geometry from first scouting run, photo bbox between preceding
# prose bottom y170 and photographic negative accession at y384; caption y393.
before=next((b for b in pg.get_text("blocks") if "Until this flood-" in b[4]),None)
code=next((b for b in pg.get_text("blocks") if "F204916" in b[4]),None)
caption=next((b for b in pg.get_text("blocks") if "Bisect of tobosa" in b[4]),None)
assert before and code and caption, "Changed figure region, no permitted blind crop"
top=float(before[3])+2
bottom=float(caption[1])-2
assert 167 <= top <= 180 and 385 <= bottom <= 398 and bottom-top >= 205, "Figure bounds require visual review"
left=52.0;right=380.0
crop=fitz.Rect(left,top,right,bottom)
pix=pg.get_pixmap(matrix=fitz.Matrix(3.25,3.25),clip=crop,alpha=False,colorspace=fitz.csRGB)
assert pix.width>=1050 and pix.height>=680
im=Image.open(io.BytesIO(pix.tobytes("png")));im.load()
# source original scan already a single raster page; high render dpi can never
# create anatomical resolution beyond 1939 original, no sharpening/synthetic parts
dst.parent.mkdir(parents=True,exist_ok=True)
im.convert("RGB").save(dst,"JPEG",quality=94,optimize=True)
record={
 "file":"images/"+name,
 "role":"Genuine 1939 USDA historical black-and-white photograph of a BISECTED Hilaria mutica / Tobosa grass plant showing its thick scaly UNDERGROUND RHIZOMES beneath an actual ruler, isolated from flowering and leaves. Photographed real source figure, not line-art; no live in-soil root growth or tiny true ligule.",
 "creator":"U.S. Department of Agriculture, R. H. Canfield, Technical Bulletin 681 (May 1939), Figure 9",
 "license":"Public Domain — original work of U.S. federal government, USDA Technical Bulletin 681, 1939",
 "license_url":"https://www.copyright.gov/title17/92chap1.html#105",
 "source_page":url,
 "source_repository":"https://ageconsearch.umn.edu/record/168453",
 "source_publication_title":"The Effect of Intensity and Frequency of Clipping on Density and Yield of Black Grama and Tobosa Grass",
 "source_original":url,
 "source_figure":"Figure 9 (printed p. 28; digital PDF page 30/35)",
 "source_author":"R. H. Canfield",
 "source_year":1939,
 "source_taxon_name":"Tobosa grass (Hilaria mutica = Pleuraphis mutica)",
 "source_locality":"Jornada Experimental Range, southern New Mexico (1930s); exact specimen locality not documented in Figure 9",
 "public_reuse":"Original photograph in a 1939 U.S. Department of Agriculture federal government publication is public domain under 17 USC 105. Source mirror citation retained; not claiming the entire mirror compilation or later annotations are federally authored.",
 "image_dimensions_archived":[im.width,im.height],
 "source_pdf_page_index":29,
 "source_pdf_page_dimensions_points":[pg.rect.width,pg.rect.height],
 "source_pdf_crop_points":[left,round(top,2),right,round(bottom,2)],
 "image_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
 "photo_review":"Source document text directly associates Figure 9 real photographed bisected tobosa plant with large scaly underground rhizomes beneath ruler, independently located in original technical bulletin. Automated geometric crop targets photograph region between last preceding prose and Figure 9 caption. Full pixel/mobile review PENDING; do not place organ-specific arrows.",
 "modifications":"Original public-domain USDA scanned black-and-white figure excerpt clipped without reinterpretation, rendered and JPEG re-encoded, no synthetic anatomy or added arrow burn-in."
}
sp.setdefault("images",[]).append(record)
panel={
 "label":"1939 USDA REAL TOBOSA RHIZOMES — bisected plant, scaly underground stems beneath ruler",
 "scientific_name":"Hilaria mutica",
 "image_url":"content/taxa/Poaceae/Hilaria/hilaria-mutica/images/"+name,
 "image_fit":"contain",
 "creator":"U.S. Department of Agriculture · R. H. Canfield · 1939",
 "license":record["license"],
 "license_url":record["license_url"],
 "source_page":url,
 "image_role":"Real original USDA historical Figure 9 photograph of a bisected Tobosa plant, showing scaly, large underground rhizomes near an actual ruler; not a line illustration or planted rooted soil view.",
 "caption":"1939 USDA Technical Bulletin 681, Figure 9, photographed bisected tobosa grass. The original author specifically identifies the large scaly structures located UNDER the ruler as rhizomes—horizontal modified stems that create new grass shoots beneath hard clay. Compare with the attached flowering-head photographs elsewhere in this Learner. This is a historical scanned photo, so do not infer an exact node, root or bud attachment where the image lacks clarity.",
 "why_it_matters":"First archived source-photo evidence of real underground scaly rhizomes for this species; a crucial distinction from curlymesquite's thin stolons crawling along the soil surface.",
 "markers":[],
 "photo_status":"Historical source page, photograph caption and author's rhizome description verified; extraction pixel quality and mobile display still need human full image QA. No unverified anatomical arrows."
}
panels=sp.setdefault("visual_comparison",{}).setdefault("items",[])
index=next((i for i,p in enumerate(panels) if p.get("scientific_name")!="Hilaria mutica"),len(panels))
assert not any(p.get("image_url")==panel["image_url"] for p in panels), "Duplicate gallery panel"
panels.insert(index,panel)
sp.setdefault("curation_status",{})["photo_files_present"]=len(sp["images"])
sp["curation_status"]["lane1_usda_1939_real_rhizomes_20261027"]="REAL_1939_USDA_FIG9_TOBOSA_RHIZOMES_ARCHIVED_SOURCE_VERIFIED_NO_UNVERIFIED_ARROWS_FINAL_PIXEL_QA_PENDING"
sp.setdefault("learner_visual_status",{})["image_count"]=len(sp["images"])
sp["learner_visual_status"]["note"]="New original 1939 USDA photographed bisected tobosa underground scaly rhizomes (Fig. 9) archived. Unlike curlymesquite's surface stolons, tobosa spreads via buried thick scaly stems. This historical photo gives real rootstock/rhizome context; still need an exact fresh opened inner ligule and separated sexed triad microscopy."
sp.setdefault("field_photo_quickcheck",{})["steps"].append("LATER ROOTSTOCK REFERENCE — actual USDA 1939 photographed bisected plant has heavy scaly rhizomes below a ruler. This is an authentic historical photograph, NOT a growing rooted plant in clay and not a close-up of ligule. Keep belowground evidence AFTER true ligule and flowering fascicle instruction.")
sp["field_photo_quickcheck"]["warning"]="Twelve source-labelled Tobosa photo records archived, including one noncommercial research hold, and genuine original USDA Figure 9 photographed scaly underground rhizomes. Aboveground ligule (free lacerate membranous edge) and separately sexed triad scale still OPEN. Historic figure photo automated crop full-resolution QA and mobile Pages overlay still pending.";
sp.setdefault("last_mile_diagnostic_photo_hold_20261023",{})["source_photos_currently_verified"]=len(sp["images"])
sp["photo_note"]=(sp.get("photo_note") or "")+" 2026-10-27: original 1939 USDA Canfield Tech Bull 681 actual TOBOSA bisected plant Figure 9 scaly buried RHIZOMES photographed beneath ruler, accurately extracted as historic source photo and archived without unsupported arrows; final pixel crop QA pending.";
card.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":"REAL_HISTORIC_RHIZOME_FIG9_ARCHIVED","source":url,"path":str(dst),"size":[im.width,im.height],"bytes":dst.stat().st_size,"scanned_pdf_pages":len(pdf),"crop":[left,top,right,bottom],"photos_total":len(sp["images"]),"panels":len(panels)}),flush=True)

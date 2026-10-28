#!/usr/bin/env python3
"""Scout historic USDA Tech Bull 681 fig.9 with a real tobosa rhizome photo.

Print-only: do not auto publish until figure boundary and legibility verified.
1939 Canfield TB 681 is a US Government work; source mirror's download rights
notice is recorded, and faithful federal plate source must be attributed.
"""
import io, re, json, time, urllib.request, fitz
urls=[
"https://ageconsearch.umn.edu/nanna/record/168453/files/tb681.pdf?registerDownload=1&version=1&withMetadata=0&withWatermark=0",
"https://ageconsearch.umn.edu/record/168453/files/tb681.pdf",
"https://ageconsearch.umn.edu/nanna/record/168453/files/tb681.pdf?registerDownload=1",
]
data=None;used=None
for url in urls:
 for k in range(2):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; HaysCountyBotanyResearch/1.0; USDA historic public-domain botany educational source)","Accept":"application/pdf,*/*","Referer":"https://ageconsearch.umn.edu/record/168453"})
   with urllib.request.urlopen(req,timeout=50) as res: data=res.read()
   print("SOURCE_READ",url,len(data),data[:10],flush=True)
   if data.startswith(b"%PDF") and 50000 < len(data) < 60000000:
    used=url
    break
   data=None
  except Exception as e:
   print("FETCH_BLOCKED",url,k,str(e)[:160],flush=True)
   time.sleep(2)
 if used:break
if not data: 
 print(json.dumps({"status":"PDF_SOURCE_BLOCKED_NO_ARCHIVAL","tested":urls}),flush=True)
 raise SystemExit(0)
pdf=fitz.open(stream=data,filetype="pdf")
print("PDF_PAGE_COUNT",len(pdf),flush=True)
found=[]
for i,page in enumerate(pdf):
 t=" ".join(page.get_text().split())
 if re.search(r"(bisect|rhizomes|scaly.*stems)",t,re.I) and re.search(r"(tobosa|rhizome)",t,re.I):
  found.append({"index":i,"page_wh":[int(page.rect.width),int(page.rect.height)],"text":t[:2300]})
print("MATCHED_PAGES",json.dumps(found,ensure_ascii=False),flush=True)
if len(pdf)>29:
 print("PAGE29_TEXT_BLOCK_BOUNDS",json.dumps([{"r":[round(v,1) for v in b[:4]],"txt":" ".join(b[4].split())[:300]} for b in pdf[29].get_text("blocks")],ensure_ascii=False),flush=True)
 print("PAGE29_IMAGE_REGIONS",json.dumps([{"xref":it[0],"rects":[list(rect) for rect in pdf[29].get_image_rects(it[0])]} for it in pdf[29].get_images(full=True)][:20]),flush=True)
if not found: 
 print("FIGURE_9_NOT_SEARCHABLE; scanned PDF needs manual page screenshot. No archive.",flush=True)
 raise SystemExit(0)
print(json.dumps({"status":"FIGURE_LOCATED_FOR_MANUAL_VISUAL_QA_NO_AUTO_ARCHIVE","source":used,"pages":found}),flush=True)

#!/usr/bin/env python3
"""Safe preview only: source-verified photographs by Francois Rousseu on Rungrass Urochloa reptans.
Inspect exact INat original photo IDs and make small contact sheet; NO PUBLICATION.
"""
import io,re,json,base64,html
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
s=requests.Session();s.headers.update({"User-Agent":"HaysCountyBotany-Lane1-SourcePhotoInspection/1.0"})
u="https://rungrass.org/"
page=s.get(u,timeout=55);page.raise_for_status()
soup=BeautifulSoup(page.content,"html.parser")
node=soup.find(id="Urochloa_reptans")
if node is None:raise SystemExit("Original Rungrass taxon section not located")
items=[]
for el in node.find_all_next():
    if el.name=="div" and el is not node and "headersp" in el.get("class",[]):
        break
    if el.name=="img" and "imgsp" in el.get("class",[]):
        src=el.get("data-src","");title=el.get("title","");link=el.get("alt","")
        m=re.fullmatch(r"https://inaturalist-open-data\.s3\.amazonaws\.com/photos/(\d+)/original\.jpeg",src)
        if not m:continue
        if "François Rousseu" not in title or "CC BY-NC" not in title:raise SystemExit("Image-specific author license mismatch")
        if link!="https://www.inaturalist.org/observations/107116761":raise SystemExit("Image observation not identical")
        items.append((int(m.group(1)),src,title,link))
print("SOURCE_SECTION_IMAGE_ID_AND_LICENSE",json.dumps([(x[0],x[2],x[3]) for x in items],ensure_ascii=False))
if len(items)!=7:raise SystemExit("Expected 7 individually credited image files; investigate source changes")
# Cross-check observation photo licenses if iNat JSON API is reachable.
try:
    j=s.get("https://api.inaturalist.org/v1/observations/107116761",timeout=35)
    if j.status_code==200:
        t=j.json().get("results",[])
        if t:
            obs=t[0]
            pics={x["id"]:x.get("license_code") for x in obs.get("photos",[])}
            print("INAT_OBSERVATION_TAXON",obs.get("taxon",{}).get("name"))
            print("INAT_INDIVIDUAL_LICENSES",json.dumps({n:pics.get(n) for n,_,_,_ in items}))
    else: print("INAT_OBSERVATION_LICENSE_RECHECK_BLOCKED",j.status_code)
except (requests.RequestException,ValueError) as ex:print("INAT_INDIVIDUAL_LICENSE_RECHECK_ERROR",str(ex)[:170])
sheet=Image.new("RGB",(990,750),"#f7f7f5")
draw=ImageDraw.Draw(sheet)
for i,(n,src,title,link) in enumerate(items):
    q=s.get(src,timeout=70)
    if q.status_code!=200 or not q.content.startswith(b"\xff\xd8"):
        raise SystemExit("Cannot retrieve original photograph "+str(n)+" "+str(q.status_code))
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(q.content))).convert("RGB")
    print("PHOTO_ID_DIMENSIONS",n,im.size,len(q.content))
    im.thumbnail((310,302))
    col=i%3;row=i//3;x=col*330+10;y=row*250+20
    im.thumbnail((308,212))
    sheet.paste(im,(x+(310-im.width)//2,y))
    draw.text((x,y+215),"Photo "+str(n),fill="black")
    draw.text((x,y+230),"Francois Rousseu CC BY-NC",fill="black")
bf=io.BytesIO();sheet.save(bf,"JPEG",quality=55,optimize=True)
print("CONTACT_SHEET_B64_BEGIN")
print(base64.b64encode(bf.getvalue()).decode())
print("CONTACT_SHEET_B64_END")

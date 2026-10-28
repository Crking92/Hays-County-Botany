#!/usr/bin/env python3
"""Field guide page 1: source-photograph infographic; 11x8.5-inch landscape."""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"reed-field-ID-page-01-review.pdf"
PREVIEW=ROOT/"reed-field-ID-page-01-review.png"
W,H=792,612

font_dir=Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DVS",str(font_dir/"DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVS-Bold",str(font_dir/"DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVS-Oblique",str(font_dir/"DejaVuSans-Oblique.ttf")))

C={
 "pine":"#163F34", "ink":"#1F382F", "muted":"#50665A",
 "cream":"#FCFDF8", "sage":"#E6EEE6", "line":"#D4DED5",
 "rust":"#B35E35", "blue":"#3E7485", "olive":"#728453",
 "gold":"#F2E1BD", "white":"#FFFFFF", "pale":"#F1F6EF",
}

def clr(x):
 from reportlab.lib.colors import HexColor
 return HexColor(C.get(x,x))
def rect(x,y,w,h,fill,stroke=None,r=0,sw=1):
 c.setFillColor(clr(fill))
 if stroke: c.setStrokeColor(clr(stroke));c.setLineWidth(sw)
 if r: c.roundRect(x,y,w,h,r,fill=1,stroke=int(bool(stroke)))
 else: c.rect(x,y,w,h,fill=1,stroke=int(bool(stroke)))
def txt(x,y,text,size=10,color="ink",bold=False,italic=False):
 c.setFillColor(clr(color))
 c.setFont("DVS-Bold" if bold else "DVS-Oblique" if italic else "DVS",size)
 c.drawString(x,y,text)
def fitpic(path,x,y,w,h,mode="contain",back="sage"):
 assert path.is_file(),path
 im=Image.open(path).convert("RGB")
 rect(x,y,w,h,back)
 if mode=="crop":
  ratio=max(w/im.width,h/im.height)
  new=(round(im.width*ratio*3),round(im.height*ratio*3))
  image=ImageOps.fit(im,new,method=Image.Resampling.LANCZOS)
  # size maintained after proper center-crop
  image=ImageOps.fit(image,(round(w*3),round(h*3)),method=Image.Resampling.LANCZOS,centering=(.5,.45))
  c.drawImage(ImageReader(image),x,y,w,h,mask="auto")
 else:
  ratio=min(w/im.width,h/im.height)
  dw,dh=im.width*ratio,im.height*ratio
  c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask="auto")
def framedphoto(path,x,y,w,h,mode="contain"):
 fitpic(path,x,y,w,h,mode)
 c.setStrokeColor(clr("line"));c.setLineWidth(.6);c.rect(x,y,w,h,stroke=1,fill=0)
def path(gen,spec,file):
 return ROOT/"content"/"taxa"/"Poaceae"/gen/spec/"images"/file
P={
 "ar_habit":path("Arundo","arundo-donax","01-reed-stand-habit.jpg"),
 "ar_collar":path("Arundo","arundo-donax","commons-arundo-2009db5a4faf.jpg"),
 "ph_habit":path("Phragmites","phragmites-australis","commons-phragmites-australis.jpg"),
 "ph_collar":path("Phragmites","phragmites-australis","harry-rose-ligule-8253945012.jpg"),
 "zi_habit":path("Zizaniopsis","zizaniopsis-miliacea","giant-cutgrass-alex-abair-habit-264449018.jpg"),
 "zi_head":path("Zizaniopsis","zizaniopsis-miliacea","commons-zizaniopsis-miliacea.jpg"),
}
for k,v in P.items():assert v.is_file(),f"missing archival photo {k}: {v}"
c=canvas.Canvas(str(OUTPUT),pagesize=(W,H),pageCompression=1)
c.setTitle("Page 01 - Is it really Phragmites? | Glass Root Garden")
c.setAuthor("Glass Root Garden - Hays County Botanical Field Learner")

rect(0,0,W,H,"cream")
rect(0,529,W,83,"pine")
txt(26,588,"GLASS ROOT GARDEN  /  HAYS COUNTY FIELD LEARNER",9,"#BFD7C6",True)
txt(26,551,"FIRST: IS IT REALLY PHRAGMITES?",24.2,"white",True)
txt(27,535,"A photograph-first guide to the giant reeds you might find along creeks, ponds and trails.",9.7,"#DDEAE1")
rect(682,565,86,26,"#E6EEE6",r=7)
txt(695,574,"PAGE 01  /  SAMPLE",8.1,"pine",True)

cards=[
 dict(x=24,accent="rust",label="GIANT REED",latin="Arundo donax",badge="INTRODUCED",
      primary="ar_habit",secondary="ar_collar",
      cues=["Thick, cane-like stems","Long, broad, drooping leaves","Leaf base flares around stem"],
      next="CHECK THE CLASPING",next2="LEAF BASE",
      credit="Forest & Kim Starr / Harry Rose",
      rights="CC BY 3.0 / CC BY 2.0",
      links=("https://commons.wikimedia.org/wiki/File:Starr_980706-1529_Arundo_donax.jpg","https://commons.wikimedia.org/wiki/File:Arundo_donax_ligule_(6804293108)_(2).jpg")),
 dict(x=276,accent="blue",label="COMMON REED",latin="Phragmites australis",badge="LINEAGE UNKNOWN",
      primary="ph_habit",secondary="ph_collar",
      cues=["Tall stems with leafy sheaths","Usually a soft, feathery plume","Fringed ligule at leaf collar"],
      next="IF THIS FITS:",next2="CONTINUE TO LINEAGE ID",
      credit="Rlevse / Harry Rose",
      rights="Public domain / CC BY 2.0",
      links=("https://commons.wikimedia.org/wiki/File:Phragmites_Australis.jpg","https://commons.wikimedia.org/wiki/File:Phragmites_australis_ligule1_(8253945012).jpg")),
 dict(x=528,accent="olive",label="GIANT CUTGRASS",latin="Zizaniopsis miliacea",badge="NATIVE REGIONALLY",
      primary="zi_habit",secondary="zi_head",
      cues=["Very large, coarse wetland grass","Loose, widely branching head","Long inner ligule (6-20 mm)"],
      next="CHECK THE OPEN",next2="PANICLE + TRUE LIGULE",
      credit="Alex Abair / Alex Abair",
      rights="CC BY 4.0",
      links=("https://commons.wikimedia.org/wiki/File:Zizaniopsis_miliacea_264449018.jpg","https://commons.wikimedia.org/wiki/File:Zizaniopsis_miliacea_264449068.jpg")),
]
for card in cards:
 x=card["x"]; y=109; w=240; h=410
 rect(x,y,w,h,"white","line",r=10)
 rect(x,477,w,41,card["accent"])
 txt(x+13,493,card["label"],13,"white",True)
 txt(x+13,481,card["latin"],9.5,"white",italic=True)
 framedphoto(P[card["primary"]],x+11,307,w-22,160,"contain")
 rect(x+11,307,w-22,22,"#183F35")
 txt(x+17,314,"WHOLE PLANT / HABIT",9,"white",True)
 rect(x+11,228,w-22,70,"pale")
 for i,line in enumerate(card["cues"]):
  # 3 short signposts; no morphological arrows placed over unverifiable anatomy
  rect(x+19,278-i*19,5,5,card["accent"],r=2)
  txt(x+30,276-i*19,line,9.9,"ink",bold=(i==2))
 framedphoto(P[card["secondary"]],x+11,144,86,77,"contain")
 txt(x+108,202,card["next"],9.1,card["accent"],True)
 txt(x+108,189,card["next2"],8.8,"ink",True)
 txt(x+108,166,"Photo 2: zoom in on",8.3,"muted")
 txt(x+108,154,"the next useful clue.",8.3,"muted")
 rect(x+11,116,w-22,23,"#F3F6EE",r=3)
 txt(x+18,124,card["badge"],9.7,card["accent"],True)
 c.linkURL(card["links"][0],(x+11,307,x+w-11,467),relative=0)
 c.linkURL(card["links"][1],(x+11,144,x+97,221),relative=0)

rect(24,60,744,41,"#E5EEE5",r=7)
txt(37,83,"FIELD ROUTE",9.2,"pine",True)
txt(122,83,"1",11,"rust",True)
txt(140,83,"STEP BACK",9.2,"ink",True)
txt(232,83,">",10,"olive",True)
txt(253,83,"2",11,"blue",True)
txt(273,83,"CHECK THE LEAF BASE",9.2,"ink",True)
txt(440,83,">",10,"olive",True)
txt(460,83,"3",11,"olive",True)
txt(481,83,"PHOTO THE FLOWERING HEAD",9.2,"ink",True)
txt(37,67,"A fluffy plume alone cannot tell you whether a Phragmites stand is native or invasive.",9,"#694C25")
rect(0,0,792,48,"#153C32")
txt(25,31,"NEXT PAGE: CONFIRM PHRAGMITES, THEN CHECK NATIVE / INTRODUCED / GULF COAST.",9.2,"white",True)
txt(25,15,"Photos: source-linked CC/public-domain specimens; not Hays County vouchers. Layout and cropping for study.",7.4,"#D8E9DF")
txt(564,15,"For review - approve before Page 02",8.2,"#D8E9DF",True)
c.showPage();c.save()

doc=fitz.open(str(OUTPUT))
assert len(doc)==1,len(doc)
page=doc[0]
assert abs(page.rect.width-W)<1 and abs(page.rect.height-H)<1
assert len(page.get_images(full=True))>=6, len(page.get_images(full=True))
pix=page.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
pix.save(str(PREVIEW))
print("OK",OUTPUT,OUTPUT.stat().st_size,"bytes; preview",PREVIEW,PREVIEW.stat().st_size,"bytes; image-objects",len(page.get_images(full=True)))

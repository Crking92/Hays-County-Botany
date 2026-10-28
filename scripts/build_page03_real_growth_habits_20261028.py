from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import math,random,io,json,base64,os,time,urllib.request,urllib.error
random.seed(24)
W,H=1275,1650
BG="#F9FAF3";PAPER="#FFFFFF";DARK="#153D2D";GREEN="#3D6B48";GRASS="#608B47";ALT="#8DA35F";SOIL="#C6B096";ROOT="#916D4E";INK="#193529"
im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
fontb="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fontser="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
def F(n,b=False,ser=False):return ImageFont.truetype(fontser if ser else (fontb if b else font),n)
def rr(box,fill,rad=17,outline=None,width=2):d.rounded_rectangle(box,radius=rad,fill=fill,outline=outline,width=width)
def txt(x,y,t,size=24,fill=INK,b=False,ser=False):d.text((x,y),t,font=F(size,b,ser),fill=fill)
def line(points,color=GREEN,width=7):d.line(points,fill=color,width=width,joint="curve")
def arrow(points,color=DARK,width=6):
    line(points,color,width)
    (x1,y1),(x2,y2)=points[-2:]
    a=math.atan2(y2-y1,x2-x1)
    p=16
    d.polygon([(x2,y2),(x2-p*math.cos(a-.5),y2-p*math.sin(a-.5)),(x2-p*math.cos(a+.5),y2-p*math.sin(a+.5))],fill=color)
def stem(x,y,top):
    line([(x,y),(x,top)],DARK,7)
    for k,(dx,ht) in enumerate([(-62,89),(66,115),(-44,141),(57,165)]):
        sy=y-24-k*21
        d.polygon([(x-4,sy+5),(x+dx*.52,sy-ht*.65),(x+dx,sy-ht),(x+dx*.50,sy-ht*.56),(x+4,sy+4)],fill=[GREEN,ALT,GRASS][k%3])
def roots(x,y,num=16,h=80,spread=65):
    for k in range(num):
        dx=(k-(num-1)/2)/(num-1)*2*spread
        mid=(x+dx*.34+random.randint(-5,5),y+h*.54)
        end=(x+dx+random.randint(-7,7),y+h*random.uniform(.7,1.03))
        line([(x,y),mid,end],ROOT,random.choice([2,3,4]))
def crop_photo(img_path,box):
    a=Image.open(img_path)
    a=ImageOps.exif_transpose(a).convert("RGB")
    x0,y0,x1,y1=box
    tw,th=x1-x0,y1-y0
    thumbnail=ImageOps.fit(a,(tw,th),method=Image.Resampling.LANCZOS,centering=(.50,.78))
    im.paste(thumbnail,(x0,y0))
    d.rounded_rectangle((x0-1,y0-1,x1+1,y1+1),radius=7,outline="#9FAE9C",width=2)
    return a.size

d.rectangle((0,0,W,145),fill=DARK)
txt(47,22,"3. HOW GRASSES GROW",62,"white",True,True)
txt(55,101,"Look at the base: how do new shoots connect?",23,"#E4EEE3")
DATA=[
  {"y":173,"title":"BUNCH / TUFT","tag":"Shoots cluster at one crown","species":"Little bluestem","latin":"Schizachyrium scoparium","photo":"content/taxa/Poaceae/Schizachyrium/schizachyrium-scoparium/images/01-field-reference.jpeg","credit":"TheMongrelKoi · CC0","source":"https://www.inaturalist.org/observations/88166662"},
  {"y":614,"title":"STOLON","tag":"A stem travels ON the soil","species":"Bermudagrass","latin":"Cynodon dactylon","photo":"content/taxa/Poaceae/Cynodon/cynodon-dactylon/images/jimmex-410585094-stolon-leafy-node.jpg","credit":"iNaturalist photo 410585094 · CC0","source":"https://www.inaturalist.org/photos/410585094"},
  {"y":1055,"title":"RHIZOME","tag":"A stem travels UNDER the soil","species":"Johnsongrass","latin":"Sorghum halepense","photo":"content/taxa/Poaceae/Sorghum/sorghum-halepense/images/commons-moadeeb-johnsongrass-rhizome.jpg","credit":"Moadeeb · CC BY-SA 4.0","source":"https://commons.wikimedia.org/wiki/File:Sorghum_Halepense_Rhizome.jpg"}
]
for n,entry in enumerate(DATA):
    y=entry["y"];y2=y+428
    rr((33,y,1243,y2),PAPER,18,"#CBD9C8",3)
    d.rounded_rectangle((48,y+17,816,y+72),radius=12,fill=DARK)
    txt(64,y+25,str(n+1)+"  "+entry["title"],31,"white",True)
    txt(80,y+84,entry["tag"],26,DARK,True)
    rr((61,y+129,808,y+403),"#F3F5ED",13)
    sx=60;sy=y+311
    d.rectangle((82,sy,798,sy+8),fill="#8B9C78")
    if n==0:
        # tight bunch rooted at shared crown
        for k in range(17):
            sx=404+random.uniform(-29,29)
            ht=random.randint(100,171)
            ex=sx+random.uniform(-145,145)
            d.polygon([(sx-5,sy-4),(sx+6,sy-5),(ex+2,sy-ht),(ex-4,sy-ht)],fill=random.choice(["#426D3C","#779951","#8EAD67"]))
        roots(407,sy+9,22,80,100)
        d.ellipse((374,sy-17,442,sy+17),fill="#AA9469",outline=GREEN,width=3)
        rr((91,y+154,295,y+204),"#E0EADC",8);txt(112,y+164,"ONE CROWN",21,DARK,True)
        arrow([(272,y+205),(391,sy-10)],DARK,5)
        txt(518,y+181,"many tillers",21,GREEN,True)
        arrow([(588,y+207),(437,y+260)],GREEN,5)
        txt(89,y+356,"ROOTS",20,DARK,True);arrow([(166,y+355),(332,sy+63)],DARK,4)
    if n==1:
        # runner crossing soil surface at nodes
        ystem=sy-8;line([(121,ystem),(765,ystem)],"#577D38",16)
        for x in [197,405,621]:
            d.ellipse((x-16,ystem-13,x+16,ystem+14),fill="#A9C47F",outline=GREEN,width=3)
            stem(x,ystem-3,ystem-124-random.randint(0,11))
            roots(x,ystem+16,13,68,50)
        rr((101,y+147,281,y+194),"#E0EADC",8);txt(117,y+156,"STOLON",22,DARK,True)
        arrow([(230,y+195),(296,ystem-2)],DARK,5)
        txt(517,y+161,"NODE",21,GREEN,True)
        arrow([(543,y+194),(620,ystem-4)],GREEN,4)
        txt(612,y+356,"roots at nodes",18,DARK)
    if n==2:
        # underground connecting stem, roots
        soil_y=sy-35
        d.rectangle((82,soil_y+7,798,sy+110),fill="#DFD0B7")
        d.line((82,soil_y,798,soil_y),fill="#8B9C78",width=9)
        rh=sy+30
        line([(145,rh),(741,rh)],"#AD8B5B",21)
        for x in [194,417,645]:
            d.ellipse((x-16,rh-18,x+16,rh+18),fill="#D4B789",outline="#806849",width=3)
            line([(x,rh),(x,soil_y-30)],GREEN,13)
            stem(x,soil_y-30,soil_y-118-random.randint(0,10))
            roots(x,rh+16,14,51,45)
        rr((100,y+152,305,y+204),"#E0EADC",8);txt(118,y+162,"RHIZOME",23,DARK,True)
        arrow([(258,y+204),(320,rh-10)],DARK,5)
        txt(541,y+357,"ROOTS",20,DARK,True);arrow([(583,y+352),(639,rh+55)],DARK,4)
    # photo column
    rr((830,y+17,1226,y2-14),"#E9F0E3",12)
    rr((843,y+31,1213,y+72),DARK,8)
    txt(868,y+38,"REAL SPECIES PHOTO",22,"white",True)
    dims=crop_photo(entry["photo"],(846,y+80,1210,y+314))
    txt(864,y+328,entry["species"],24,DARK,True)
    txt(865,y+359,entry["latin"],18,DARK)
    txt(862,y+389,entry["credit"],14,"#4D6252")
    print("PHOTO_OK",entry["species"],dims)
# footer
rr((38,1500,1236,1618),"#E3ECDA",16,"#A4BE99",2)
txt(65,1514,"TRY IT",37,DARK,True,True)
txt(310,1520,"Trace the connected stem.",29,DARK,True)
txt(310,1564,"Above soil, below soil, or one crown?",24,DARK)
txt(48,1627,"Cutaway drawings are schematic. Bermudagrass makes BOTH stolons and rhizomes.",14,"#3B5845")
OUT="field-guides/page-03-grass-growth-habits-real-photos.jpg"
PDF="field-guides/page-03-grass-growth-habits-real-photos.pdf"
REPORT="field-guides/page-03-photo-credits.json"
B=io.BytesIO();im.save(B,"JPEG",quality=90,optimize=True,subsampling=0);b=B.getvalue()
from reportlab.pdfgen import canvas as reportcanvas
out=io.BytesIO();c=reportcanvas.Canvas(out,pagesize=(612,792))
from reportlab.lib.utils import ImageReader
c.drawImage(ImageReader(io.BytesIO(b)),0,0,width=612,height=792)
c.save()
pdf=out.getvalue()
R=os.environ["GITHUB_REPOSITORY"];TOKEN=os.environ["GITHUB_TOKEN"];API="https://api.github.com/repos/"+R
def gh(method,path,obj=None):
 req=urllib.request.Request(API+path,data=None if obj is None else json.dumps(obj,ensure_ascii=False).encode(),method=method,headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","Content-Type":"application/json","User-Agent":"HaysBotanyCrewPhotoWorkbook"})
 with urllib.request.urlopen(req,timeout=50) as response:return json.load(response)
def blob(data,binary=False):return gh("POST","/git/blobs",{"content":base64.b64encode(data).decode() if binary else data,"encoding":"base64" if binary else "utf-8"})["sha"]
entries=[{"path":OUT,"mode":"100644","type":"blob","sha":blob(b,True)},{"path":PDF,"mode":"100644","type":"blob","sha":blob(pdf,True)},{"path":REPORT,"mode":"100644","type":"blob","sha":blob(json.dumps(DATA,indent=2)+"\n")}]
for attempt in range(6):
 head=gh("GET","/git/ref/heads/main")["object"]["sha"]
 tree=gh("GET","/git/commits/"+head)["tree"]["sha"]
 nt=gh("POST","/git/trees",{"base_tree":tree,"tree":entries})["sha"]
 commit=gh("POST","/git/commits",{"tree":nt,"parents":[head],"message":"Crew guide page 3: real licensed species photographs beside cutaway growth habit diagrams [skip ci]"})["sha"]
 try:gh("PATCH","/git/refs/heads/main",{"sha":commit,"force":False});print("PAGE3_COMPLETE",commit,OUT,PDF,len(b),len(pdf));break
 except urllib.error.HTTPError as ex:
  if attempt==5 or ex.code!=422:raise
  time.sleep(2)

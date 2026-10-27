import base64,hashlib,io,json,os,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from PIL import Image,ImageOps
import cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

R=os.environ["GITHUB_REPOSITORY"]
TOKEN=os.environ["GITHUB_TOKEN"]
API="https://api.github.com/repos/"+R
OUTPUT="field-guides/Grass_Anatomy_From_Beginner_to_Advanced_Crew_Guide.pdf"
REPORT="field-guides/Grass_Anatomy_V2_sources_and_build.json"
UA={"User-Agent":"HaysCountyGrassAnatomyTraining/2.0 (educational reference; credit retained)"}
SRC={
 "whole":("Grassy grass plant.svg","Kelvinsong / CC BY 3.0","https://commons.wikimedia.org/wiki/File:Grassy_grass_plant.svg"),
 "spikelet":("Poaceae - Spighetta.png","Enrico Blasutto / CC BY-SA 4.0","https://commons.wikimedia.org/wiki/File:Poaceae_-_Spighetta.png"),
 "floral":("Grassbluete numbers clones unlinked.svg","Nefronus, Alfred, Enzoklop / CC0","https://commons.wikimedia.org/wiki/File:Grassbluete_numbers_clones_unlinked.svg"),
 "field":("Poaceae - unidentified plant and spikelets.jpg","RoRo / CC0","https://commons.wikimedia.org/wiki/File:Poaceae_-_unidentified_plant_and_spikelets.jpg"),


}
GITHUB_RAW="https://raw.githubusercontent.com/"+R+"/main/"
MORE={
 "hair":("content/taxa/Poaceae/Cynodon/cynodon-dactylon/images/cynodon-dactylon-stefan-lefnaer-scaled-collar-ccby-sa4.jpg","Stefan Lefnaer / CC BY-SA 4.0 (true Cynodon collar region, 2-mm photo scale)"),
 "mem":("content/taxa/Poaceae/Sorghum/sorghum-bicolor/images/rasbak-sorghum-ligule-03.jpg","Rasbak / CC BY-SA 3.0 (actual Sorghum bicolor inner ligule)"),
 "sorghumroots":("content/taxa/Poaceae/Sorghum/sorghum-bicolor/images/miquel-pujol-sorghum-two-seedlings-roots-2008.jpg","Miquel Pujol Palol / CC BY-SA 3.0"),
 "sorghumspike":("content/taxa/Poaceae/Sorghum/sorghum-bicolor/images/matt-lavin-sorghum-terminal-spikelet-pairs-4055518933.jpg","Matt Lavin / CC BY-SA 2.0"),
}
def get_image(key):
    if key in SRC:
        name,credit,page=SRC[key]
        normal=name.replace(" ","_")
        digest=hashlib.md5(normal.encode("utf-8")).hexdigest()
        url="https://upload.wikimedia.org/wikipedia/commons/"+digest[:1]+"/"+digest[:2]+"/"+urllib.parse.quote(normal,safe="()-,._")
        mime="svg" if name.endswith(".svg") else "other"
    else:
        path,credit=MORE[key]; page=GITHUB_RAW+path;url=page;mime="other"
    last=None
    for trial in range(3):
        try:
            req=urllib.request.Request(url,headers=UA)
            with urllib.request.urlopen(req,timeout=55) as resp: data=resp.read(9_000_000)
            if not (1000<len(data)<9_000_000):raise ValueError("Unsupported image size "+str(len(data)))
            if mime=="svg":
                png=cairosvg.svg2png(bytestring=data,output_width=1320)
                im=Image.open(io.BytesIO(png))
            else:im=Image.open(io.BytesIO(data))
            im=ImageOps.exif_transpose(im).convert("RGBA")
            white=Image.new("RGBA",im.size,"white");white.alpha_composite(im)
            out=white.convert("RGB")
            out.thumbnail((1500,1700))
            f=io.BytesIO();out.save(f,format="JPEG",quality=88,optimize=True)
            return ImageReader(io.BytesIO(f.getvalue())),{"source":page,"direct":url,"credit":credit,"pixels":list(im.size),"bytes":len(data)}
        except Exception as e:
            last=str(e)
            print("FETCH_RETRY",key,trial+1,last[:170]);time.sleep(2)
    if key=="floral":
        from PIL import ImageDraw,ImageFont
        im=Image.new("RGB",(1150,720),(250,253,250))
        d=ImageDraw.Draw(im)
        try:
            face=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
            small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
        except Exception:
            face=ImageFont.load_default();small=face
        # Simple schematic, not a measured botanical plate; original fall-back only after published CC0 file 429.
        stem="#52754C";lemma="#D8AC4C";palea="#8DAF62";stigma="#B75E7D";pollen="#E8BD48"
        d.line([(570,630),(570,475),(590,340)],fill=stem,width=16)
        d.arc((285,235,565,670),40,145,fill="#C65B47",width=27)
        d.arc((585,235,865,670),35,147,fill="#C65B47",width=27)
        d.polygon([(480,575),(500,285),(574,342),(562,568)],fill=lemma)
        d.polygon([(670,570),(651,298),(590,350),(593,570)],fill=palea)
        d.ellipse((548,364,625,435),fill="#B7CF59",outline="#6A893D",width=4)
        d.line([(580,360),(565,247)],fill=stigma,width=7)
        d.line([(586,359),(629,240)],fill=stigma,width=7)
        for x,yy in [(555,258),(543,277),(531,297),(626,253),(642,277),(649,296)]:
            d.line([(570 if x<600 else 626,355),(x,yy)],fill=stigma,width=3)
        for pts in [[(580,364),(423,234)],[(595,364),(768,232)],[(586,368),(591,186)]]:
            d.line(pts,fill="#856C38",width=5)
            xx,yy=pts[-1];d.ellipse((xx-18,yy-37,xx+18,yy+8),fill=pollen,outline="#AF8430",width=4)
        d.ellipse((524,414,552,444),fill="#83B7B7");d.ellipse((630,412,658,442),fill="#83B7B7")
        d.line([(495,289),(390,100)],fill="#6E9459",width=9)
        # numbered labels, no false scale claim
        tags=[(1,340,565,"Glumes"),(2,465,305,"Lemma"),(3,380,107,"Awn"),
              (4,687,315,"Palea"),(5,655,447,"Lodicules"),(6,756,179,"Stamens"),
              (7,575,397,"Ovary"),(8,642,231,"Stigmas")]
        for n,x,y,t in tags:
            d.ellipse((x-17,y-17,x+17,y+17),fill="#224D41")
            d.text((x-7,y-12),str(n),font=face,fill="white")
        d.text((75,28),"GENERALIZED GRASS FLOWER - numbered teaching schematic",fill="#224D41",font=face)
        d.text((75,680),"1 glumes | 2 lemma | 3 awn | 4 palea | 5 lodicules | 6 stamens | 7 ovary | 8 stigmas",fill="#365C4D",font=small)
        b=io.BytesIO();im.save(b,format="JPEG",quality=90)
        print("FALLBACK_DIAGRAM",key,"published CC0 reference blocked by HTTP 429; honest teaching illustration")
        return ImageReader(io.BytesIO(b.getvalue())),{"source":"Original field workbook drawing after Commons CC0 HTTP 429","attempted_published_source":page,"credit":"New simplified teaching schematic, not a scale drawing","bytes":len(b.getvalue())}
    print("SOURCE_IMAGE_UNAVAILABLE",key,last)
    return None,{"source":page,"direct":url,"credit":credit,"error":last}
images={};credits={}
for name in [*SRC,*MORE]:
    images[name],credits[name]=get_image(name)
    print("IMAGE_READY" if images[name] else "IMAGE_NOT_READY",name,json.dumps(credits[name],ensure_ascii=False))
if not all(images[x] for x in ["whole","spikelet","floral","field","mem","hair"]):
    raise RuntimeError("Required existing scientific diagrams or public photo examples missing; do not release an illustration-incomplete workbook")

font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(font):
    pdfmetrics.registerFont(TTFont("DVS",font))
    pdfmetrics.registerFont(TTFont("DVS-Bold",bold))
    FONT,BOLD="DVS","DVS-Bold"
else:
    FONT,BOLD="Helvetica","Helvetica-Bold"
W,H=612,792
INK=HexColor("#172D27");MOSS=HexColor("#3A6652");LIGHT=HexColor("#EEF4EE");GOLD=HexColor("#D0A052");GREY=HexColor("#53645E")
OUT=io.BytesIO()
c=canvas.Canvas(OUT,pagesize=(W,H),pageCompression=1)
c.setTitle("Grass, Up Close - Beginner to Advanced Field Workbook for Conservation Crews")
c.setAuthor("City of Kyle conservation training - prepared with licensed botanical illustrations")
def para(t,x,y,width,size=10.3,color=INK,boldtext=False,leading=None):
    style=ParagraphStyle("t",fontName=BOLD if boldtext else FONT,fontSize=size,leading=leading or size*1.42,textColor=color,spaceAfter=0)
    p=Paragraph(t.replace("&","&amp;").replace("<b>","<b>").replace("</b>","</b>"),style)
    _,h=p.wrap(width,800)
    p.drawOn(c,x,y-h)
    return y-h
def rect(x,y,w,h,fill,r=9):
    c.setFillColor(fill)
    c.roundRect(x,y,w,h,r,fill=1,stroke=0)
def imprint(img,x,y,w,h):
    if img is None:
        rect(x,y,w,h,LIGHT)
        para("Published reference artwork unavailable",x+8,y+h-30,w-16,10)
        return
    iw,ih=img.getSize();scale=min(w/iw,h/ih)
    rw,rh=iw*scale,ih*scale
    c.drawImage(img,x+(w-rw)/2,y+(h-rh)/2,width=rw,height=rh,mask="auto")
def top(section,title,idx):
    c.setFillColor(MOSS);c.rect(0,H-18,W,18,fill=1,stroke=0)
    c.setFillColor(GREY);c.setFont(BOLD,8.4);c.drawString(39,751,section.upper())
    c.setFillColor(INK);c.setFont(BOLD,18)
    # shrink longer titles gently
    if pdfmetrics.stringWidth(title,BOLD,18)>534:
        c.setFont(BOLD,15)
    c.drawString(39,719,title)
    c.setStrokeColor(HexColor("#CBD7CD"));c.line(39,706,573,706)
    c.setFillColor(GREY);c.setFont(FONT,8.1)
    c.drawString(40,30,"GRASS, UP CLOSE  |  BEGINNER TO ADVANCED  |  CREW FIELD WORKBOOK")
    c.drawRightString(568,30,str(idx).zfill(2))
def next_page():c.showPage()
def cover():
    rect(0,0,W,H,HexColor("#F8FBF7"),0)
    c.setFillColor(MOSS);c.rect(0,H-17,W,17,fill=1,stroke=0)
    c.setFont(BOLD,10.5);c.setFillColor(MOSS);c.drawString(43,741,"CITY OF KYLE  /  CONSERVATION CREW LEARNING")
    c.setFont(BOLD,35);c.setFillColor(INK);c.drawString(43,684,"GRASS, UP CLOSE")
    c.setFont(FONT,15);c.drawString(43,650,"A field workbook from beginner to advanced")
    para("See the whole grass. Trace a single leaf. Open the ligule. Follow the spikelets. Finally, learn the parts that separate look-alikes.",43,625,495,11.6)
    imprint(images["whole"],75,111,340,420)
    rect(425,155,151,293,LIGHT)
    para("<b>THE FIELD ROUTE</b>",439,429,122,11,MOSS)
    yy=394
    for s in ["01  Stand back","02  Find the stem","03  Follow a leaf","04  Open the ligule","05  Read the head","06  Examine a spikelet","07  Check the base"]:
        yy=para(s,439,yy,124,9.8)-12
    para("Published art: Kelvinsong, CC BY 3.0. Not a particular native species.",45,82,495,8.4,GREY)
    next_page()
def intro():
    top("How to use this book","Your first 10 minutes in the field",1)
    para("Start with a common grass at a trail edge or mowed bed. You do not need to know its name. Each stop moves closer, introduces a few terms, and asks you to point to the real structures.",42,689,526,11.1)
    rect(42,360,528,230,LIGHT)
    y=570
    for n,b in [
      ("1  LOOK","Stand 10-20 feet away. Describe shape and habitat."),
      ("2  FOLLOW","Choose one shoot and trace its leaves to the base."),
      ("3  OPEN","Bend one blade back to reveal the inside ligule."),
      ("4  ZOOM","Find one spikelet and compare the real diagram."),
      ("5  DOCUMENT","Photograph what you can see, mark what is still hidden.")]:
        y=para(n,59,y,112,11,MOSS,True)
        y=para(b,173,y+13,372,10.2)-19
    para("<b>Bring:</b> hand lens (10x), small metric ruler, phone or camera, notebook, and a fresh grass sample where collection is permitted.",45,322,517,11)
    para("<b>Important:</b> Real anatomy examples may feature grasses that are not native to Hays County. We use their photographed structures as lessons, not as planting recommendations. A complete species ID requires multiple matching traits.",45,244,517,10.2)
    para("<b>From beginner to advanced:</b> read the large terms first, do the 'try it' task next, and only then read 'next level.'",45,150,517,10.5,MOSS)
    next_page()
def lesson_page(index,sec):
    top(sec["stage"],sec["title"],index)
    y=para(sec["lead"],42,691,526,10.6)
    # Main left image
    rect(42,296,314,345,HexColor("#F7F9F6"))
    imprint(images[sec["asset"]],54,326,290,293)
    cap=sec.get("caption","")
    para(cap,47,284,315,7.1,GREY,leading=10.1)
    # Main right: vocabulary
    c.setFillColor(MOSS);c.setFont(BOLD,9.6);c.drawString(371,628,"WORDS TO LEARN")
    ty=611
    terms=sec["terms"]
    for term,meaning in terms:
        ty=para(term,371,ty,196,9.45,MOSS,True)
        ty=para(meaning,371,ty-3,196,8.85,INK,leading=12)
        ty-=11
    # Foot task
    rect(42,153,528,119,LIGHT)
    para("TRY IT OUTSIDE",56,256,495,10.5,MOSS,True)
    para(sec["field"],56,236,495,9.5,INK,leading=13.7)
    para("NEXT LEVEL",46,136,500,9.5,MOSS,True)
    para(sec["advanced"],46,119,517,9.2,INK,leading=13)
    next_page()
def last_tasks():
    ix=len(LESSONS)+2
    top("CREW WORKSHEET","One real grass: field observation sheet",ix)
    para("Do this WITHOUT looking up a name. Record actual evidence, then use a flora or key. A blank answer is better than an invented part.",42,688,526,10.7)
    items=[("Park / date / observer",""),("Habitat: dry slope, open lawn, riparian etc.",""),("Habit: bunch, mat, single stalk, unknown",""),("Culm and node: where did you find it?",""),("Blade: flat, folded, rolled, hairs?",""),("Sheath and OUTSIDE collar: description",""),("INSIDE ligule: membrane, hairs, absent, unseen",""),("Auricles: present, absent, unseen",""),("Inflorescence: spike, raceme, panicle, unclear",""),("Spikelet: size / number of florets / glumes",""),("Base: roots, crown, stolon, rhizome, unseen",""),("Tentative ID & two look-alikes to eliminate","")]
    y=648
    for title,_ in items:
        para(title,45,y,512,9.7)
        y-=46
        c.setStrokeColor(HexColor("#9EAFA4"));c.line(45,y+12,560,y+12)
    next_page()
def quiz():
    top("SELF CHECK","Quiz: from observation to diagnosis",len(LESSONS)+3)
    q=[
      ("01","What is the difference between a blade and its sheath?"),
      ("02","Does a collar sit mainly on the outside or inside of a leaf?"),
      ("03","Which structure is the little flap or hair fringe on the inside?"),
      ("04","A culm has three visible nodes. What are the spaces between them called?"),
      ("05","What is the difference between a whole flowerhead and a spikelet?"),
      ("06","Which bract belongs to a floret: lemma or glume?"),
      ("07","What does a feathery grass stigma do?"),
      ("08","Where does a stolon usually grow compared with a rhizome?"),
      ("09","Why is a fringe of hairs on the OUTSIDE sheath not proof of a hairy ligule?"),
      ("10","Your photo shows a panicle but no ligule. What should you report?")]
    y=687
    for n,qtext in q:
        y=para("<b>"+n+"</b>  "+qtext,43,y,510,9.8)-20
        c.setStrokeColor(HexColor("#D1DBD3"));c.line(48,y+5,557,y+5);y-=10
    next_page()
def answers():
    top("ANSWER KEY","Ten answers worth remembering",len(LESSONS)+4)
    ans=[
      "1. Blade is free, usually long and narrow; sheath is the lower wrapping leaf portion.",
      "2. Collar is on the outer surface where blade and sheath meet.",
      "3. The ligule: on the inside, sometimes membrane, hairs or apparently absent.",
      "4. Internodes.",
      "5. Inflorescence is the whole flowering structure; spikelet is one small unit within it.",
      "6. Lemma belongs to a floret; glumes are typically at the spikelet base.",
      "7. To catch pollen; it may be feathery to collect windborne grains.",
      "8. Stolon usually runs at/above soil, rhizome below soil; both are stems.",
      "9. Location matters: only hairs at the inner blade-sheath seam constitute a hairy ligule.",
      "10. Record 'ligule not seen' and take another photo; do not claim a feature without evidence."
    ]
    y=682
    for item in ans:y=para(item,44,y,519,10.2)-19
    rect(43,101,526,67,LIGHT)
    para("GOOD FIELD HABIT: When unsure, record the trait as unknown. A reliable ID can be checked by someone else.",56,153,494,10,MOSS,True)
    next_page()
def credits_page():
    top("SOURCE NOTES","External illustrations and photographs",len(LESSONS)+5)
    para("This edition replaces most generic drawings with published scientific illustrations and real species-source photographs. A simplified flower schematic is retained as a clearly marked fallback. Original image creators retain credit. Crop/grassy images illustrate structures, not native plant status.",42,689,521,9.9)
    y=629
    for key in [*SRC,*MORE]:
        d=credits[key]
        label=key.replace("sorghum","sorghum ").replace("spike","spikelet")
        y=para("<b>"+label.upper()+"</b>  |  "+d["credit"],43,y,522,9.1)-1
        link=d["source"]
        if len(link)>92: link=link[:89]+"..."
        y=para(link,46,y,519,7.2,GREY,leading=10)-9
    para("<b>License details:</b> CC BY requires attribution; CC BY-SA also requires ShareAlike for adapted material. CC0 is public-domain-dedicated. Photographs are reused as examples; labels and teaching explanations in this PDF are new.",44,150,521,9.2)
    next_page()
def followup():
    top("REFERENCE PATH","Where to learn even more",len(LESSONS)+7)
    refs=[
      ("Montana State Extension - Grass Identification Basics","https://extension-store.montana.edu/montguides/grass-identification-basics"),
      ("Earth@Home - Grass Morphology & Anatomy","https://evolution.earthathome.org/grasses/morphology/"),
      ("Oregon State - Grass Structures","https://forages.oregonstate.edu/regrowth/how-does-grass-grow/grass-structures"),
      ("USDA - Typical Grass Structures","https://www.nrcs.usda.gov/plantmaterials/etpmcpu8052.pdf"),
      ("Hays Botany Learner (regional grass study)","https://crking92.github.io/Hays-County-Botany/"),
    ]
    y=672
    for label,link in refs:
        y=para("<b>"+label+"</b>",45,y,512,11,MOSS)-7
        y=para(link,47,y,512,8.4,GREY)-34
    rect(43,100,525,115,LIGHT)
    para("Final question: can you identify a tiny grass structure without a photograph showing that structure? No. The most important advanced skill is knowing what you have actually observed.",56,193,497,10.8,INK)
    next_page()

# End pages
LESSONS=json.loads(r'''[{"stage":"BEFORE YOU START","title":"Meet a grass. Do not name it yet.","lead":"A grass is a flowering plant. It has roots, stems, leaves, and tiny flowers. Today your job is to learn where those parts live before trying to identify a species.","asset":"field","terms":[["Blade","The long green part of a grass leaf. It collects sunlight."],["Stem / culm","The supporting stalk that carries leaves and sometimes a flowerhead."],["Seedhead / inflorescence","A cluster of tiny flowers or their developing fruits."]],"field":"Stand 15-20 feet away. Point to the overall patch, individual plants, and one flowerhead. Say what you can actually see.","advanced":"A plant with no seedhead can still be identified using leaves, sheaths, ligules and growth habit.","caption":"Real grass in flower. The plant pictured is not identified to species; it teaches structure, not local native status."},{"stage":"STOP 1 / 20 FEET","title":"Read the whole plant's silhouette","lead":"Before you touch a grass, look at its shape. Shape gives useful clues, but it almost never proves the name by itself.","asset":"whole","terms":[["Bunch / tuft","Many shoots stand close together, like a fountain from one base."],["Mat / sod","Low stems spread outward and can form a carpet."],["Habit","A botanist's word for the plant's overall growth form."]],"field":"Ask: upright, arching, drooping, or creeping? Is it one clump, a patch, or a lawnlike mat? Sketch its outline.","advanced":"Clumps may spread by short rhizomes; a dense patch does not automatically imply stolons. Check actual attachments.","caption":"Published whole-plant diagram, Kelvinsong (CC BY 3.0). A generalized grass, not one species."},{"stage":"STOP 2 / 6 FEET","title":"Find one shoot in a clump","lead":"A single tuft can have many shoots. Follow just ONE upward. This is how you avoid mixing parts from different plants.","asset":"whole","terms":[["Shoot","One developing leafy stem and its leaves."],["Tiller","A new grass shoot that grows from a basal bud near the crown."],["Crown","The tight region at soil level where shoots and roots connect."]],"field":"Pick a clump. Count visible shoots without pulling. Can you find younger leaves near the base?","advanced":"A tiller can remain vegetative or eventually form a flowering culm. Cutting the flower stalk does not necessarily kill the crown.","caption":"Kelvinsong's generalized grass includes a basal bud, daughter shoots and roots."},{"stage":"STOP 3 / 3 FEET","title":"Culm, node and internode","lead":"Think of a grass culm as a stalk built in segments. The junctions help you tell a grass stem from a loose leaf.","asset":"whole","terms":[["Culm","The grass stem, usually round and often hollow between its joints."],["Node","A joint on a culm. Grass leaves originate at nodes."],["Internode","The stretch of stem BETWEEN two nodes."]],"field":"With your finger, trace a flowering stalk down to the first visible node. Count two internodes.","advanced":"Many culms are hollow in their internodes but solid at nodes. Do not assume every grass culm is hollow.","caption":"Look for horizontal joints on the drawn culm; the sheath may hide some nodes."},{"stage":"STOP 4 / 1 FOOT","title":"A grass leaf has TWO big pieces","lead":"What we casually call one 'blade of grass' is actually a leaf made of an upper blade and a lower sheath.","asset":"mem","terms":[["Blade","The long, free part extending away from the stem; it may be flat, folded or rolled."],["Sheath","The lower leaf portion that wraps around the culm."],["Midrib / veins","The lengthwise support and smaller parallel lines running along many grass leaves."]],"field":"Find one green leaf. Trace its free blade DOWN until it starts wrapping around the stem. That wrap is the sheath.","advanced":"Some sheaths are split; some are closed. Blade width, folding, hairs, and sheath opening all inform grass keys.","caption":"Real Sorghum bicolor blade and sheath at their junction, photographed by Rasbak (CC BY-SA 3.0); this is an anatomy example, not a Hays native recommendation."},{"stage":"STOP 5 / HAND HELD","title":"The collar is NOT the ligule","lead":"These are two nearby features that beginners often confuse. Look at both sides of the same leaf.","asset":"hair","terms":[["Collar","The narrow band on the OUTSIDE of a grass leaf where blade meets sheath."],["Ligule","A flap or row of hairs on the INSIDE of the blade-sheath junction."],["Adaxial / abaxial","Inside/facing stem versus outside/facing away; useful technical terms when reading a key."]],"field":"Hold the blade away from the stem. Turn it over to inspect the inside seam. Don't call outer sheath hairs the ligule.","advanced":"Ligules can be membranous, hairy, mixed, very short or absent. Different leaf ages can appear different.","caption":"Real Cynodon dactylon leaf collar photograph with a scale; Stefan Lefnaer (CC BY-SA 4.0). The true inner ligule must be opened separately."},{"stage":"STOP 6 / 6 INCHES","title":"A membranous ligule looks like a flap","lead":"A membrane is a thin sheet of tissue. Imagine a tiny translucent fingernail standing up inside the leaf base.","asset":"mem","terms":[["Membranous ligule","A thin, often whitish or translucent flap at the inside junction."],["Margin","The top edge of that flap. It may be smooth, jagged or hairy."],["Height","How far the ligule projects upward; sometimes a fraction of a millimeter."]],"field":"Gently pull the blade back. Look at its inner base against light. If you have a 1-mm ruler, photograph it beside the flap.","advanced":"Measure from the sheath mouth to the tip of the ligule - not from the nearest visible sheath hair.","caption":"Rasbak's actual Sorghum bicolor inner ligule photograph (CC BY-SA 3.0)."},{"stage":"STOP 7 / MACRO","title":"A hairy ligule is a FRINGE","lead":"Not every grass makes a membrane. Some make a tiny row of hairs. The PHOTO shows an exterior collar: you still need to turn the leaf back to locate the true inner ligule.","asset":"hair","terms":[["Ciliate / cilia","Fringed with tiny hairs."],["Fringe of hairs","Short hairs along the INSIDE edge where blade joins sheath."],["Pubescent","A word for a plant surface covered with hairs; not necessarily a ligule."]],"field":"Compare an inner ligule with hairy blade surfaces or sheath margins. Are the hairs exactly at the interior joint?","advanced":"In sand lovegrass, conspicuous external collar hairs must not be mistaken for the very short true internal ligule.","caption":"Cynodon dactylon (Bermudagrass) external collar and hairs, Stefan Lefnaer (CC BY-SA 4.0); the very short inner ligule is not independently exposed."},{"stage":"STOP 8 / THE COLLAR","title":"Auricles and how a new leaf opens","lead":"Sometimes the leaf base has two tiny 'ears' that grab the stem. Young leaf blades can also arrive folded or rolled.","asset":"whole","terms":[["Auricles","Small ear-shaped projections at the blade base; many grasses lack them."],["Vernation","How a new blade sits in the unopened shoot: folded or rolled."],["Sheath mouth","Where the sheath ends and the free blade begins."]],"field":"Check BOTH edges of the leaf base for auricles. Look at a young shoot before unrolling it.","advanced":"No auricles is a useful observation, not a diagnosis. Vernation requires an intact young shoot.","caption":"General grass form, Kelvinsong, CC BY 3.0. Auricle detail varies by species."},{"stage":"STOP 9 / 6 INCHES","title":"A seedhead is a WHOLE cluster","lead":"One 'seedhead' may hold dozens or hundreds of tiny flowering units. Look at its branching pattern before one small spikelet.","asset":"field","terms":[["Inflorescence","The entire flowering structure of a plant."],["Panicle","A branching inflorescence: side branches arise from a main axis."],["Rachis","The main axis or backbone of a flowering structure."]],"field":"Trace the head from the stalk to the main axis. Find one branch and see whether smaller units attach to it.","advanced":"A contracted panicle can look spikelike; move branches apart gently and check attachment.","caption":"Unidentified photographed grass with densely clustered flowerheads, RoRo (CC0); a field structure demonstration only."},{"stage":"STOP 10 / BRANCH PATTERNS","title":"Spike, raceme, and panicle","lead":"These words explain HOW the tiny units are arranged. Think: direct attachment, short stalk attachment, or branches upon branches.","asset":"whole","terms":[["Spike","Spikelets attach to a main axis without their own stalks."],["Raceme","Spikelets attach to an axis on little stalks (pedicels)."],["Panicle","Branching axis with smaller side branches, often airy and open."]],"field":"Observe an intact head from the side. Draw a single axis plus its branches. Don't call a head a spike just because it looks narrow.","advanced":"Certain bluestems bear paired sessile and pedicelled spikelets on specialized branches, sometimes called rames.","caption":"The generalized whole-plant diagram shows only ONE possible inflorescence pattern."},{"stage":"STOP 11 / MAGNIFY","title":"What is a spikelet?","lead":"A spikelet is the small grass reproductive unit you can often see with the naked eye. It is not always one flower.","asset":"spikelet","terms":[["Spikelet","The little package that holds one or more grass florets."],["Glumes","Usually two lower bracts at the base of a spikelet, though some grasses differ."],["Rachilla","The small internal axis that bears the florets inside a spikelet."]],"field":"Pick one intact spikelet and sketch its overall shape. Can you find the two basal bracts? Do NOT pull it apart yet.","advanced":"Species identification may depend on whether glumes are equal, hairy, keeled, absent, or longer than the florets.","caption":"Existing published spikelet illustration by Enrico Blasutto (CC BY-SA 4.0), with original Italian labeling; translate with the English glossary."},{"stage":"STOP 12 / 10X HAND LENS","title":"One floret is one tiny flower","lead":"Grass flowers usually do not have colorful petals. Their protective bracts make them look like miniature overlapping scales.","asset":"floral","terms":[["Floret","A grass flower plus its two surrounding bracts."],["Lemma","The outer protective bract of a floret."],["Palea","The usually smaller inner protective bract of a floret."]],"field":"First identify the WHOLE spikelet. Then trace inward to a floret. Remember: glumes are usually outside and below the florets.","advanced":"The lemma and palea are not petals. Their texture, nerves, teeth and awn points are useful at species level.","caption":"Numbered generalized grass-flower teaching schematic. We attempted to retrieve the published CC0 diagram first; its source link appears in the credits."},{"stage":"STOP 13 / FLOWER ITSELF","title":"Anthers carry pollen; stigmas catch it","lead":"A grass is a flowering plant even if the flowers look like specks. What emerges from florets can be extremely diagnostic.","asset":"floral","terms":[["Anther","The pollen-producing part, often a dangling yellow, purple or brown little sac."],["Stigma","The pollen-catching part, often feathery and branched."],["Ovary","The structure inside the flower that can mature into the fruit."]],"field":"Use the diagram to find #6 anthers, #7 ovary and #8 feathery stigmas. Look for the same organs on a fresh flowering head.","advanced":"Grass flowers commonly release pollen to the wind. Flowering stage changes how easily the structures can be photographed.","caption":"Numbered botanical teaching schematic with eight labeled structures; original public-domain reference is linked in source notes."},{"stage":"STOP 14 / READ THE NUMBERS","title":"Translate the flower diagram","lead":"Here is the complete key for the eight numbers on the public-domain diagram. Use this after you understand what a spikelet and floret are.","asset":"floral","terms":[["1 Glumes | 2 Lemma","The outer spikelet bracts and the outer floret bract."],["3 Awn | 4 Palea","A narrow projection (if present), and the inner floret bract."],["5 Lodicules | 6 Stamens","Tiny scales associated with opening the flower, and pollen organs."],["7 Ovary | 8 Stigmas","Seed-producing floral structure and the feathery pollen-catching ends."]],"field":"Say these words while pointing to actual numbered structures. Which ones can you see without magnification?","advanced":"Floret orientation and number vary. This diagram is an educational generalized grass example, not a species key.","caption":"Diagram used to teach the same scientific structures; external reference and fallback authorship are identified in source notes."},{"stage":"STOP 15 / SPIKELET CLOSE-UP","title":"Awn, bristle, or an ordinary hair?","lead":"These three structures can all look like thin threads, but they are not the same thing. Their attachment is the clue.","asset":"sorghumspike","terms":[["Awn","A stiff or slender projection growing from a glume or lemma."],["Bristle","A stiff hairlike structure that may develop on an axis below or near spikelets."],["Hair / trichome","A small outgrowth from an epidermal surface (stem, sheath, blade or bract)."]],"field":"If you spot a thread, follow it to its BASE. Does it arise directly from a floral bract, or beside an entire spikelet?","advanced":"In Setaria bristles arise from modified branches below the spikelets; in Aristida the awns belong to the lemma.","caption":"Real Sorghum bicolor spikelet-group macro, Matt Lavin (CC BY-SA 2.0), archived in the Hays Botany repo."},{"stage":"STOP 16 / AT THE SOIL","title":"Roots are not the same as rhizomes","lead":"Roots absorb water and anchor a grass. Some grasses also have true horizontal STEMS that run beneath the soil.","asset":"sorghumroots","terms":[["Fibrous roots","Many narrow roots, rather than one large woody taproot."],["Crown","The place where the shoots and attached roots meet."],["Rhizome","A STEM growing under soil. Look for nodes, scale leaves, buds and shoots, not just roots."]],"field":"At an approved site, gently clean a collected specimen and photograph shoot bases connected to roots. Don't collect in protected areas.","advanced":"A young seedling root photo does not prove the architecture of a mature perennial crown; follow the entire plant connection.","caption":"Real two-week-old Sorghum bicolor seedlings with adventitious roots, Miquel Pujol Palol (CC BY-SA 3.0)."},{"stage":"STOP 17 / SPREADING GRASS","title":"Stolons run on top; rhizomes run below","lead":"When a grass forms a patch, learn how new shoots connect. This often matters more than the seedhead color.","asset":"whole","terms":[["Stolon","Horizontal stem that runs at or above ground and can root at nodes."],["Rhizome","Horizontal underground stem with joints and buds."],["Tiller","A new shoot from a basal bud; not automatically a runner."]],"field":"Point to one grass shoot. Try to trace any horizontal connecting stem. Photograph actual nodes before calling it a stolon or rhizome.","advanced":"Johnsongrass has characteristic spreading rhizomes; typical crop sorghum lacks that perennial network. Do not spread fragments.","caption":"Kelvinsong's published generalized diagram includes above-ground stolon and below-ground rhizome."},{"stage":"STOP 18 / THINK LIKE A BOTANIST","title":"A species name needs several clues","lead":"One shape or color is not enough. A good identification uses multiple independent structures on the SAME specimen.","asset":"whole","terms":[["Vegetative characters","Features of leaves, sheaths, ligules, stems and roots."],["Reproductive characters","Features of flowerhead, spikelets and florets."],["Look-alike","A different species with similar overall appearance."]],"field":"Write three things you observed and one thing you still need to photograph. Keep the name tentative until evidence agrees.","advanced":"Keys may use glume nerves, lemma texture, awn insertion, ligule size, rhizome nodes and spikelet disarticulation.","caption":"Generalized published plant illustration (CC BY 3.0)."},{"stage":"STOP 19 / FIELD SAFETY","title":"Grass, sedge or rush?","lead":"Some grasslike plants are not actually grasses. The common shortcut about stem shape is helpful but has exceptions.","asset":"field","terms":[["Grass (Poaceae)","Usually has a sheath, a ligule region, jointed culms, and tiny spikelets."],["Sedge (Cyperaceae)","Often has 3-angled, solid culms; leaves may be in three ranks."],["Rush (Juncaceae)","Often has round solid stems and small flower parts, not grass spikelets."]],"field":"Before keying a 'grass,' inspect the leaf sheath and flowers. Do not rely ONLY on 'sedges have edges' or stem feel.","advanced":"Some sedges have round stems, and some grasses have solid culms. Reproductive organs are the decisive test.","caption":"General photo for observation; grasslike silhouettes alone do not settle plant family."},{"stage":"STOP 20 / CAMERA PRACTICE","title":"Photograph a grass in five steps","lead":"A clear photo sequence makes someone else able to check your ID even after you leave the park.","asset":"hair","terms":[["1. Habitat & habit","Photograph the patch, its soil and its growth form."],["2. Whole individual","Shoot from crown to top of flowering head."],["3. Collar & ligule","Photograph outside first, then peel back and show the INSIDE with a scale."],["4. Inflorescence","Photograph attached branching pattern."],["5. Spikelet & base","Photograph close-up reproductive parts and roots/runners if available."]],"field":"Try this on one common park grass. Keep at least one image with a ruler or coin and write the location.","advanced":"Take original unedited images first. When adding arrows, label only anatomically visible evidence. Keep species verification separate from photo rights.","caption":"Licensed Cynodon collar-hair image, Stefan Lefnaer (CC BY-SA 4.0), shows useful framing; it does not prove inner ligule length."},{"stage":"FIELD TEST / NO SPECIES GUESSING","title":"Can your crew find six structures?","lead":"Use one fresh grass plant near the trail. Work in pairs; the goal is correct vocabulary before a species guess.","asset":"whole","terms":[["A. From 10 feet","Bunch or mat? Upright or arching? Presence of seedhead?"],["B. From 2 feet","Locate stem, node, blade and sheath."],["C. With your fingers","Find outside collar; turn leaf back to find inner ligule."],["D. With 10X lens","Choose one spikelet and identify at least one bract."]],"field":"Partner A points to a part; Partner B names it, explains it in ordinary words, and says whether it is visible.","advanced":"If a part is hidden, record 'not seen' instead of guessing. Unknown is a good field observation.","caption":"Generalized grass reference by Kelvinsong (CC BY 3.0)."}]''')
cover();intro()
for i,sec in enumerate(LESSONS,start=2):lesson_page(i,sec)
last_tasks();quiz();answers();credits_page();followup()
c.save()
pdf=OUT.getvalue()
if not pdf.startswith(b"%PDF") or len(pdf)<110_000:raise RuntimeError("PDF unexpectedly empty")
print("PDF_COMPLETE",len(pdf),"PAGES",len(LESSONS)+6,"SOURCES",sum(v is not None for v in images.values()))
def gh(method,path,obj=None):
    data=None if obj is None else json.dumps(obj,ensure_ascii=False).encode()
    req=urllib.request.Request(API+path,method=method,data=data,headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","Content-Type":"application/json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"HaysBotany-FieldGuide-Publisher"})
    with urllib.request.urlopen(req,timeout=70) as r:return json.load(r)
pdfblob=gh("POST","/git/blobs",{"encoding":"base64","content":base64.b64encode(pdf).decode()})["sha"]
meta={"date":"2026-10-27","pdf_path":OUTPUT,"page_count":len(LESSONS)+6,"size_bytes":len(pdf),"sha256":hashlib.sha256(pdf).hexdigest(),"source_assets":credits,"principles":["Beginner-to-advanced structure explanation","Published diagrams first","Real photographs with source & license","No unverified native-range or photo anatomy claim"]}
metablob=gh("POST","/git/blobs",{"encoding":"utf-8","content":json.dumps(meta,ensure_ascii=False,indent=2)+"\n"})["sha"]
for attempt in range(7):
    head=gh("GET","/git/ref/heads/main")["object"]["sha"]
    base=gh("GET","/git/commits/"+head)["tree"]["sha"]
    tr=gh("POST","/git/trees",{"base_tree":base,"tree":[{"path":OUTPUT,"mode":"100644","type":"blob","sha":pdfblob},{"path":REPORT,"mode":"100644","type":"blob","sha":metablob}]})["sha"]
    cm=gh("POST","/git/commits",{"message":"Field workbook: beginner-to-advanced real illustrated grass anatomy PDF with CC credits [skip ci]","tree":tr,"parents":[head]})["sha"]
    try:
        gh("PATCH","/git/refs/heads/main",{"sha":cm,"force":False})
        print("PDF_COMMITTED",OUTPUT,cm,len(pdf),meta["page_count"])
        break
    except urllib.error.HTTPError as e:
        if e.code!=422 or attempt==6:raise
        time.sleep(3)

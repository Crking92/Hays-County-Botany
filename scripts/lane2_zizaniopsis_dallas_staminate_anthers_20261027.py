import base64,csv,hashlib,io,json,os,time,urllib.error,urllib.request
from PIL import Image,ImageOps
R=os.environ["GITHUB_REPOSITORY"];T=os.environ["GITHUB_TOKEN"];A="https://api.github.com/repos/"+R
ID=530923087; OBS=294943928; SP="Zizaniopsis miliacea"
BASE="content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea/"
NAME="annika-lindqvist-dallas-reproductive-orange-anthers-530923087.jpg"
PATH=BASE+"images/"+NAME
CARD=BASE+"species.json";CSV=BASE+"image-sources.csv"
SCORE="reports/lane2-six-role-photo-score-20261027.json"
REPORT="reports/lane2-zizaniopsis-dallas-visible-staminate-anthers-20261027.json"
PAGE="https://www.inaturalist.org/photos/"+str(ID)
def req(method,url,obj=None,gh=False,limit=12000000):
 h={"User-Agent":"HaysBotanyNativeGrassFieldIdentification/1.0"}
 if gh:h.update({"Authorization":"Bearer "+T,"Accept":"application/vnd.github+json","Content-Type":"application/json"})
 payload=None if obj is None else json.dumps(obj,ensure_ascii=False).encode()
 with urllib.request.urlopen(urllib.request.Request((A+url if gh else url),data=payload,method=method,headers=h),timeout=50) as f:
  out=f.read(limit+1)
  if len(out)>limit:raise ValueError("Unexpected oversize source")
  return out
def gh(method,path,obj=None):return json.loads(req(method,path,obj,True))
def read(p):return base64.b64decode(gh("GET","/contents/"+p+"?ref=main")["content"]).decode()
def blob(value,binary=False):return gh("POST","/git/blobs",{"content":base64.b64encode(value).decode() if binary else value,"encoding":"base64" if binary else "utf-8"})["sha"]
obs=json.loads(req("GET","https://api.inaturalist.org/v1/observations/"+str(OBS)))["results"][0]
assert obs.get("taxon",{}).get("name")==SP and obs.get("quality_grade")=="research","Source identification changed"
ph=next(x for x in obs["photos"] if x["id"]==ID)
assert ph.get("license_code")=="cc-by","Photo's license changed!"
url=ph["url"].replace("/square.","/original.").replace("/thumb.","/original.").replace("/medium.","/original.")
raw=req("GET",url,limit=6000000)
with Image.open(io.BytesIO(raw)) as im:
 if im.format!="JPEG" or im.size!=(1704,2048):raise ValueError("Original photograph changed "+str(im.size))
 out=io.BytesIO();ImageOps.exif_transpose(im).convert("RGB").save(out,format="JPEG",quality=92,subsampling=0,optimize=True)
image=out.getvalue();hashtext=hashlib.sha256(image).hexdigest();imageblob=blob(image,True)
rights={"creator":"Annika Lindqvist","license":"CC BY 4.0 (original photo-level code cc-by)","license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":PAGE,"source_observation_url":"https://www.inaturalist.org/observations/"+str(OBS),"source_image":url,"public_reuse":"yes, with attribution to Annika Lindqvist and CC BY license link","modifications":"Full-resolution 1704x2048 source re-encoded to RGB JPEG without crop and scrubbed EXIF/GPS; arrows are separate onscreen overlays","image_sha256":hashtext,"source_original_sha256":hashlib.sha256(raw).hexdigest()}
imgentry={"file":"images/"+NAME,"role":"True Zizaniopsis reproductive photograph showing EXSERTED ORANGE ANTHERS on attached branching flowering structures, alongside green subtending spikelet/bract structures; cannot sex each neighboring spikelet or measure glumes from this photo","photo_status":"Real original photo, Dallas Co, Texas, Research Grade; external dangling orange anthers clearly visible. Do NOT treat orange anthers as visible stigmas, or map position of both spikelet sexes without microscopic proof.",**rights}
panel={"label":"TRUE REPRODUCTIVE DETAIL · orange anthers on a flowering branch","scientific_name":SP,"image_url":PATH,"image_fit":"contain","image_role":imgentry["role"],
"caption":"Dallas County photograph by Annika Lindqvist shows conspicuous exserted orange anthers on branches carrying green cutgrass spikelets. Pair this with the existing Alex Abair image containing pale feathery floral structures. The reproductive organ types are visible, but individual neighboring spikelets are not independently mapped as staminate versus pistillate without dissection.",
"why_it_matters":"A photographed anther is better evidence than inferring male flowers from an ordinary distant seedhead.",
"markers":[{"label":"Orange anthers protruding from flowering branch","label_x":62,"label_y":83,"target_x":77,"target_y":57},{"label":"Attached green flower-bearing branchlets","label_x":4,"label_y":9,"target_x":40,"target_y":36}],
"photo_status":"Gross visible reproductive organs only, no ruler or definitive individual sex assignment.",**rights}
for attempt in range(7):
 head=gh("GET","/git/ref/heads/main")["object"]["sha"];tree=gh("GET","/git/commits/"+head)["tree"]["sha"]
 card=json.loads(read(CARD));scores=json.loads(read(SCORE));oldcsv=read(CSV)
 if any(x.get("file")=="images/"+NAME for x in card["images"]):
  print("ALREADY_INSTALLED_NO_DUPLICATE");break
 score=next(x for x in scores["records"] if x["canonical_id"]=="zizaniopsis-miliacea")
 if score["after_total"]!=4.5 or score["roles"]["reproductive_closeup"]!=0.5:raise ValueError("Baseline changed, hold for specialist reconciliation")
 card["images"].append(imgentry)
 gallery=card["visual_comparison"]["items"];insert=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!=SP),len(gallery))
 gallery.insert(insert,panel)
 card["photo_note"]=card.get("photo_note","")+"\n2026-10-27 Lane 2: original CC BY Dallas Texas Zizaniopsis close-up visibly shows exserted orange anthers on attached flowers. Two original-anatomy arrows. Existing Alex Abair macro shows distinct feathery floral structures. Full reproductive-detail category filled to 1 without claiming individually sex-verified spikelets or measured bracts. Inner true ligule and actual exposed rhizomes still absent."
 if isinstance(card.get("learner_visual_status"),dict):card["learner_visual_status"]["image_count"]=len(card["images"])
 score["roles"]["reproductive_closeup"]=1
 score["after_total"]=5;score["after_percentage"]=83
 score["gaps_warning"]="Orange anthers now truly photographed and existing feathered floral organs preserved. Mapping male/female individual spikelets, exposed underground rhizomes, and peeled inner ligule remain unproven."
 rows=io.StringIO();w=csv.writer(rows);w.writerow([NAME,imgentry["role"],"Annika Lindqvist","CC BY 4.0",PAGE,url,"yes","yes with attribution",OBS,ID])
 newcsv=oldcsv.rstrip("\r\n")+"\n"+rows.getvalue()
 summary=scores["summary"];values=[x["after_total"] for x in scores["records"]]
 summary["mean_after_percent"]=round(sum(values)/len(values)/6*100,1)
 summary["distribution"]={f"{v:.1f}/6":values.count(v) for v in sorted(set(values))}
 summary["new_exact_species_jpegs_archived_this_pass"]=int(summary.get("new_exact_species_jpegs_archived_this_pass",0))+1
 summary["new_gross_structure_overlay_arrows_this_pass"]=int(summary.get("new_gross_structure_overlay_arrows_this_pass",0))+2
 scores["final_photo_upgrade_source"]=REPORT
 scores["last_zizaniopsis_staminate_20261027"]={"new_photo":1,"gross_arrows":2,"source_photo_rights":"CC BY 4.0","new_reproductive_score":1,"warning":"Male anthers and pale feathery floral structures photographed, exact individual male/female spikelet position not microscopically verified","pages":"not independently verified"}
 report={"date":"2026-10-27","species":SP,"source_photo":PAGE,"location":"Dallas County Texas","creator":"Annika Lindqvist","license":"CC BY 4.0","local_photo":PATH,"source_dimensions":[1704,2048],"source_sha256":hashlib.sha256(raw).hexdigest(),"stored_photo_sha256":hashtext,"archived_bytes":len(image),"new_photo":1,"arrows_added":2,"before_photo_roles":4.5,"after_photo_roles":5,"percent":83,"remaining":["Peeled-open membranous inner ligule with scale","True excavated horizontal rhizomes with nodes and attached roots","Isolation and independent identification of staminate versus pistillate individual spikelets"],"public_pages":"not verified"}
 datafiles=[{"path":PATH,"mode":"100644","type":"blob","sha":imageblob}]
 for path,text in [(CARD,json.dumps(card,ensure_ascii=False,indent=2)+"\n"),(CSV,newcsv),(SCORE,json.dumps(scores,ensure_ascii=False,indent=2)+"\n"),(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+"\n")]:
  datafiles.append({"path":path,"mode":"100644","type":"blob","sha":blob(text)})
 newtree=gh("POST","/git/trees",{"base_tree":tree,"tree":datafiles})["sha"]
 commit=gh("POST","/git/commits",{"message":"Lane 2: add actual licensed giant cutgrass exserted male anthers [skip ci]","tree":newtree,"parents":[head]})["sha"]
 try:
  gh("PATCH","/git/refs/heads/main",{"sha":commit,"force":False})
  print("PHYSICAL_PHOTO_AND_SCORE_COMMITTED",commit,"image",PATH,"SHA256",hashtext,"mean",summary["mean_after_percent"])
  break
 except urllib.error.HTTPError as e:
  if e.code!=422 or attempt==6:raise
  print("CONCURRENT_PUSH_RETRY",attempt);time.sleep(2)
else:raise RuntimeError("No commit")

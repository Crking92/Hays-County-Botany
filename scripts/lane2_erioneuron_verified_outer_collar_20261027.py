import base64,csv,hashlib,io,json,os,time,urllib.error,urllib.request
from PIL import Image,ImageOps
R=os.environ["GITHUB_REPOSITORY"];T=os.environ["GITHUB_TOKEN"];API="https://api.github.com/repos/"+R
P="content/taxa/Poaceae/Erioneuron/erioneuron-pilosum/";C=P+"species.json";S="reports/lane2-six-role-photo-score-20261027.json";CS=P+"image-sources.csv"
ID=628337446; OBS=344829413
F="michelle-w-concho-visible-hairy-outer-collar-628337446.jpg";REL=P+"images/"+F
PAGE="https://www.inaturalist.org/photos/"+str(ID)
REPORT="reports/lane2-erioneuron-original-white-exterior-collar-20261027.json"
def req(method,url,obj=None,authorized=False):
 h={"User-Agent":"HaysBotanyActualGrassPhotographicAnatomy/1.0"}
 if authorized:h.update({"Authorization":"Bearer "+T,"Accept":"application/vnd.github+json","Content-Type":"application/json","X-GitHub-Api-Version":"2022-11-28"})
 b=None if obj is None else json.dumps(obj,ensure_ascii=False).encode()
 with urllib.request.urlopen(urllib.request.Request((API+url if authorized else url),data=b,method=method,headers=h),timeout=55) as v:
  out=v.read(10000001)
  if len(out)>=10000001:raise RuntimeError("Unexpectedly large response")
  return out
def gh(m,p,obj=None):return json.loads(req(m,p,obj,True))
def read(p):return base64.b64decode(gh("GET","/contents/"+p+"?ref=main")["content"]).decode()
def blob(data,binary=False):return gh("POST","/git/blobs",{"content":base64.b64encode(data).decode() if binary else data,"encoding":"base64" if binary else "utf-8"})["sha"]
o=json.loads(req("GET","https://api.inaturalist.org/v1/observations/"+str(OBS)))["results"][0]
if o.get("quality_grade")!="research" or o.get("taxon",{}).get("name")!="Erioneuron pilosum":raise RuntimeError("Not exact source ID")
p=next(x for x in o["photos"] if x["id"]==ID)
if p.get("license_code")!="cc-by":raise RuntimeError("Source photo reuse rights changed")
url=p["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/thumb.","/original.")
raw=req("GET",url)
with Image.open(io.BytesIO(raw)) as image:
 if image.format!="JPEG" or image.size!=(2048,2048):raise RuntimeError("Source original pixels changed")
 clean=ImageOps.exif_transpose(image).convert("RGB")
 out=io.BytesIO();clean.save(out,format="JPEG",quality=92,optimize=True,subsampling=0)
jpeg=out.getvalue();h=hashlib.sha256(jpeg).hexdigest();hraw=hashlib.sha256(raw).hexdigest()
binary=blob(jpeg,True)
credit=p.get("attribution") or "Michelle W. (鍾偉瑋)"
rights={"creator":"Michelle W. (鍾偉瑋)","license":"CC BY 4.0 (iNaturalist photo-level cc-by)","license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":PAGE,"source_observation_url":"https://www.inaturalist.org/observations/"+str(OBS),"source_image":url,"public_reuse":"yes — CC BY with named attribution","modifications":"Full 2048×2048 original RGB JPEG reencoded with GPS/EXIF removed; anatomy arrows are separate on-screen SVG overlays","image_sha256":h,"source_original_sha256":hraw}
role="Original live Erioneuron pilosum Concho County photograph clearly showing outer blade–sheath collar, long WHITE EXTERNAL HAIRS at collar, and folded pointed leaf; true 0.35-mm inner ligule NOT exposed or measurable"
entry={"file":"images/"+F,"role":role,"photo_status":"Actual CC BY photo-level research-grade Texas E. pilosum verified. Long white exterior collar tuft visually demonstrated, no claim of opened inner ligule or washed root.",**rights}
panel={"label":"ACTUAL EXTERIOR COLLAR · prominent white tuft at blade/sheath V", "scientific_name":"Erioneuron pilosum","image_url":REL,"image_fit":"contain",
"image_role":role,"caption":"Michelle W.'s Texas photograph clearly shows a living hairy tridens leaf meeting the stem, with conspicuous long white hairs protruding from the outer collar. Note the folded narrow gray-green pointed blade and nearby reproductive branch. The shorter microscopic true INNER ligule is NOT opened or measured here.",
"why_it_matters":"For the first time this lesson photographs the true external blade/sheathed-culm meeting area with its white hair tuft, rather than confusing silky reproductive florets with leaf hairs.",
"markers":[{"label":"Long WHITE HAIRS on outside of leaf collar","label_x":4,"label_y":82,"target_x":48,"target_y":87},{"label":"Narrow folded, pointed leaf blade","label_x":3,"label_y":11,"target_x":29,"target_y":52}],"photo_status":"External collar only (half-role). No inner 0.35mm ligule, rootstock or measured lemma/glume implied.",**rights}
for retry in range(7):
 head=gh("GET","/git/ref/heads/main")["object"]["sha"];tree=gh("GET","/git/commits/"+head)["tree"]["sha"]
 card=json.loads(read(C));scores=json.loads(read(S));cs=read(CS)
 if any(x.get("file")=="images/"+F for x in card["images"]):
  print("ALREADY_INSTALLED_NO_DOUBLE_COUNT");break
 row=next(x for x in scores["records"] if x["canonical_id"]=="erioneuron-pilosum")
 if row["after_total"]!=4.5 or row["roles"]["true_collar_ligule_sheath"]!=0:
  raise ValueError("Score changed; no unverified role promotion")
 card["images"].append(entry)
 gallery=card["visual_comparison"]["items"]
 pos=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!="Erioneuron pilosum"),len(gallery))
 gallery.insert(pos,panel)
 count=len(card["images"])
 card["photo_note"]=card.get("photo_note","")+"\n2026-10-27 Lane 2: new Concho County original Michelle W. CC BY exterior collar white-hair macro photo, two gross-only anatomy arrows, PHOTO ROLE 0->0.5 only. Actual short INNER hair-fringe ligule with ruler and exposed connected root still MISSING."
 if isinstance(card.get("curation_status"),dict):
  card["curation_status"]["photo_metadata_count"]=count
  card["curation_status"]["photo_files_present"]=count
  card["curation_status"]["lane2_concho_verified_collar_counter_sync_20261027"]="All "+str(count)+" true taxon JPEG records present; includes private owner image, excluded from public; external collar hairs are not a proven inner ligule"
 if isinstance(card.get("learner_visual_status"),dict):
  card["learner_visual_status"]["image_count"]=count
  card["learner_visual_status"]["note"]="Actual source-rights-screened teaching gallery, with verified external collar white hairs, reproductive florets and living clump. Genuine tiny internal ligule and washed roots remain photo gaps. A private owner image is excluded from public publishing."
 row["roles"]["true_collar_ligule_sheath"]=0.5
 row["after_total"]=5;row["after_percentage"]=83
 row["gaps_warning"]="Original Concho County white OUTER collar hair macro now verified: half collar role. Short inner true ligule still not opened or scaled, real root crown not excavated, glume/lemma venation unverified."
 fields=["file_name","role","creator","license","source_page","direct_url","study_use","public_reuse"]
 newrows=io.StringIO(newline="");writer=csv.DictWriter(newrows,fieldnames=fields);writer.writeheader()
 for image in card["images"]:
  lic=image.get("license","")
  use="private-study-only" if "All rights reserved" in lic else "yes"
  reuse="no-private" if use=="private-study-only" else image.get("public_reuse","conditional; check exact source")
  writer.writerow({"file_name":image.get("file","").replace("images/","",1),"role":image.get("role",""),"creator":image.get("creator",""),"license":lic,"source_page":image.get("source_page",""),"direct_url":image.get("source_image",image.get("direct_url","")),"study_use":use,"public_reuse":reuse})
 summary=scores["summary"];vals=[x["after_total"] for x in scores["records"]]
 summary["mean_after_percent"]=round(sum(vals)/len(vals)/6*100,1)
 summary["distribution"]={f"{n:.1f}/6":vals.count(n) for n in sorted(set(vals))}
 summary["new_exact_species_jpegs_archived_this_pass"]=int(summary.get("new_exact_species_jpegs_archived_this_pass",0))+1
 summary["new_gross_structure_overlay_arrows_this_pass"]=int(summary.get("new_gross_structure_overlay_arrows_this_pass",0))+2
 scores["final_photo_upgrade_source"]=REPORT
 report={"species":"Erioneuron pilosum","date":"2026-10-27","new_jpeg":1,"new_arrows":2,"source_photo":PAGE,"license":"CC BY 4.0","creator":rights["creator"],"local_file":REL,"source_dimensions_px":[2048,2048],"physical_JPEG_bytes":len(jpeg),"sha256":h,"original_source_sha256":hraw,"roles_before":4.5,"roles_after":5,"percent":83,"score_note":"Outer real leaf/sheathed-stem collar hairs add only 0.5; microscopic true inner ligule remains missing","remaining":["true internal 0.35 mm hairy ligule with measuring scale","real exposed connected roots and shallow stem","isolated measured glume/lemma veins"],"source_inventory_entries":count,"public_pages":"not verified"}
 parts=[{"path":REL,"mode":"100644","type":"blob","sha":binary}]
 for name,data in [(C,json.dumps(card,ensure_ascii=False,indent=2)+"\n"),(CS,newrows.getvalue()),(S,json.dumps(scores,ensure_ascii=False,indent=2)+"\n"),(REPORT,json.dumps(report,ensure_ascii=False,indent=2)+"\n")]:
  parts.append({"path":name,"mode":"100644","type":"blob","sha":blob(data)})
 newtree=gh("POST","/git/trees",{"base_tree":tree,"tree":parts})["sha"]
 commit=gh("POST","/git/commits",{"tree":newtree,"parents":[head],"message":"Lane 2: archive exact Texas hairy tridens photographed collar hairs without claiming microscopic ligule [skip ci]"})["sha"]
 try:
  gh("PATCH","/git/refs/heads/main",{"sha":commit,"force":False})
  print("INSTALLED_REAL_PHOTO",commit,REL,"SHA256",h,"scores",row["after_total"],"mean",summary["mean_after_percent"])
  break
 except urllib.error.HTTPError as e:
  if e.code!=422 or retry==6:raise
  time.sleep(2)
else:raise RuntimeError("Installer not committed")

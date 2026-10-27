import base64,csv,hashlib,io,json,os,time,urllib.error,urllib.request
from PIL import Image,ImageOps
REPO=os.environ["GITHUB_REPOSITORY"];TOKEN=os.environ["GITHUB_TOKEN"];API="https://api.github.com/repos/"+REPO
SCORE="reports/lane2-six-role-photo-score-20261027.json"
REPORT="reports/lane2-trichodes-scheelei-real-licensed-macros-20261027.json"
PHOTOS=[
 {"taxon":"eragrostis-trichodes","genus":"Eragrostis","name":"Eragrostis trichodes","photo":98799473,"obs":61724015,"filename":"cleveland-powell-attached-stacked-spikelet-98799473.jpg","expected":[1536,2048],"role":"TRUE same-species single spikelet macro; multiple stacked mature florets along an attached hairlike pedicel; no ruler or glume vein dissection","title":"TRUE SPIKELET · several visible stacked florets on attached pedicel","caption":"Cleveland Powell's exact-species Texas sand lovegrass macro. Follow the extremely thin pedicel to one spikelet; several overlapping florets are clearly visible. This does not establish millimeter-measured glume size, lemma venation or a peeled-open ligule.","markers":[{"label":"Attached hairlike spikelet pedicel","label_x":8,"label_y":12,"target_x":49,"target_y":33},{"label":"Stacked individual florets within one spikelet","label_x":6,"label_y":67,"target_x":49,"target_y":43}],"score_role":"reproductive_closeup"},
 {"taxon":"eragrostis-trichodes","genus":"Eragrostis","name":"Eragrostis trichodes","photo":98799515,"obs":61724015,"filename":"cleveland-powell-blade-sheath-exterior-hairs-98799515.jpg","expected":[2048,1536],"role":"True external leaf blade/sheath V and long white hairs at collar, species-confirmed original; tiny TRUE inner ligule not peeled open","title":"OUTER LEAF COLLAR · long true hairs; inner ligule STILL NOT exposed","caption":"Cleveland Powell's exact-species sand lovegrass photo shows the outer blade–sheath junction and long hairs projecting around the collar. The inner true ligule (hair fringe) is not isolated or calibrated, so this is supportive vegetative anatomy only.","markers":[{"label":"Clearly visible long external collar hairs","label_x":5,"label_y":13,"target_x":50,"target_y":45},{"label":"Green blade rising from the sheath junction","label_x":66,"label_y":84,"target_x":58,"target_y":29}],"score_role":None},
 {"taxon":"setaria-scheelei","genus":"Setaria","name":"Setaria scheelei","photo":729425948,"obs":397679971,"filename":"jackie-t-true-attached-spikelets-bristle-macro-729425948.jpg","expected":[1536,2048],"role":"Exact live Setaria scheelei close-up, numerous attached pale spikelet clusters and distinct long bristles radiating from short side branches; no glume/lemma dissection or physical mm scale","title":"REAL ATTACHED BRISTLES AND SPIKELETS · individual units clearly visible","caption":"Jackie T's same-species Texas macro shows small pale spikelets clustered on side branches beneath exceptionally long slender bristles. Follow how bristles project far beyond the adjacent spikelet bodies; unlike another whole bristly seedhead, the attachment pattern is visible. This is not a measured isolated glume or mature root crown.","markers":[{"label":"Long projecting sterile bristles","label_x":6,"label_y":28,"target_x":53,"target_y":54},{"label":"Small attached pale spikelet clusters","label_x":58,"label_y":88,"target_x":48,"target_y":70}],"score_role":"reproductive_closeup"}]
def call(method,path,obj=None,limit=15000000,github=False):
  headers={"User-Agent":"HaysBotanyNativeFieldLearner/1.0 photo-rights-verified"}
  if github: headers.update({"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","Content-Type":"application/json","X-GitHub-Api-Version":"2022-11-28"})
  payload=None if obj is None else json.dumps(obj,ensure_ascii=False).encode()
  req=urllib.request.Request((API+path if github else path),method=method,data=payload,headers=headers)
  with urllib.request.urlopen(req,timeout=55) as r:
    data=r.read(limit+1)
    if len(data)>limit:raise RuntimeError("Over source byte cap")
    return data
def gh(method,path,obj=None):return json.loads(call(method,path,obj,github=True))
def blob(content,binary=False):
  return gh("POST","/git/blobs",{"content":base64.b64encode(content).decode() if binary else content,"encoding":"base64" if binary else "utf-8"})["sha"]
def read(path):
  o=gh("GET","/contents/"+path+"?ref=main")
  return base64.b64decode(o["content"]).decode()
images=[];licenses={}
for p in PHOTOS:
  info=json.loads(call("GET","https://api.inaturalist.org/v1/observations/"+str(p["obs"])))["results"][0]
  if info.get("taxon",{}).get("name")!=p["name"] or info.get("quality_grade")!="research":raise ValueError("Taxon source research ID changed for "+str(p["photo"]))
  ph=next(x for x in info["photos"] if x["id"]==p["photo"])
  if ph.get("license_code")!="cc-by":raise ValueError("License source-level changed for "+str(p["photo"]))
  url=ph["url"].replace("/square.","/original.").replace("/thumb.","/original.").replace("/medium.","/original.")
  raw=call("GET",url,limit=8500000)
  with Image.open(io.BytesIO(raw)) as im:
    if im.format!="JPEG" or list(im.size)!=p["expected"]:raise ValueError("Original expected real image dimensions changed "+str((p["photo"],im.size)))
    img=ImageOps.exif_transpose(im).convert("RGB")
    out=io.BytesIO();img.save(out,format="JPEG",quality=92,optimize=True,subsampling=0)
  final=out.getvalue()
  p["image_bytes"]=final;p["source"]=url;p["sha256"]=hashlib.sha256(final).hexdigest();p["source_sha256"]=hashlib.sha256(raw).hexdigest()
  p["attribution"]=ph.get("attribution") or ("Cleveland Powell" if p["taxon"]=="eragrostis-trichodes" else "Jackie T")
  p["creator"]=("Cleveland Powell" if p["taxon"]=="eragrostis-trichodes" else "Jackie T")
  p["page"]="https://www.inaturalist.org/photos/"+str(p["photo"])
  p["rel"]="content/taxa/Poaceae/"+p["genus"]+"/"+p["taxon"]+"/images/"+p["filename"]
  images.append({"path":p["rel"],"mode":"100644","type":"blob","sha":blob(final,True)})
  print("PHYSICAL_SOURCE_VERIFIED",p["photo"],"dimensions",p["expected"],"license","cc-by","size",len(final),"sha256",p["sha256"])
for attempt in range(7):
  main=gh("GET","/git/ref/heads/main")["object"]["sha"];tree=gh("GET","/git/commits/"+main)["tree"]["sha"]
  files=list(images)
  scores=json.loads(read(SCORE))
  changed=[]
  for taxon in ["eragrostis-trichodes","setaria-scheelei"]:
    subset=[p for p in PHOTOS if p["taxon"]==taxon]
    base="content/taxa/Poaceae/"+subset[0]["genus"]+"/"+taxon+"/"
    card=json.loads(read(base+"species.json"))
    csvtext=read(base+"image-sources.csv")
    row=next(r for r in scores["records"] if r["canonical_id"]==taxon)
    if row["after_total"] not in (4.5,5.0):raise RuntimeError("Score baseline needs review for "+taxon)
    if any(im["file"]=="images/"+p["filename"] for im in card["images"] for p in subset):
      raise RuntimeError("Already installed unexpected; no duplicate scores permitted")
    was=row["after_total"]
    for p in subset:
      rights={"creator":p["creator"],"license":"CC BY 4.0 (original iNaturalist individual photo metadata cc-by)","license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":p["page"],"source_observation_url":"https://www.inaturalist.org/observations/"+str(p["obs"]),"source_image":p["source"],"public_reuse":"yes with photographer credit and license","image_sha256":p["sha256"],"original_source_sha256":p["source_sha256"],"modifications":"Original full-resolution image re-encoded JPEG with EXIF/GPS removed, without crop; arrows are separate SVG overlays"}
      card["images"].append({"file":"images/"+p["filename"],"role":p["role"],"photo_status":"Research Grade exact-species Texas original photographed; only directly visible anatomical structures annotated. Score assignment is role specific; no hidden organ claimed.",**rights})
      item={"label":p["title"],"scientific_name":p["name"],"image_url":p["rel"],"image_fit":"contain","image_role":p["role"],"caption":p["caption"],"why_it_matters":"Actual close photographed diagnostic anatomy, not a repeated general seedhead or assumed unseen roots.","markers":p["markers"],"photo_status":"Anatomical arrows only on clearly photographed external features; no fabricated inner ligule, mm calibration or rhizome.",**rights}
      gallery=card["visual_comparison"]["items"]
      idx=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!=p["name"]),len(gallery))
      gallery.insert(idx,item)
      p["rights"]=rights
      changed.append(p["photo"])
    if row["after_total"]==4.5 and row["roles"]["reproductive_closeup"]==0.5:
      row["roles"]["reproductive_closeup"]=1
      row["after_total"]=5.0;row["after_percentage"]=83
      row["gaps_warning"]=("True inner ligule with measured scale, exposed connected roots, and calibrated glume vein dissection not yet photographed" if taxon=="eragrostis-trichodes" else "True scaled ligule pictured earlier; roots/crown still entirely missing, actual bristle/spikelet groups now clearly photographed, isolated glumes not measured")
    card["photo_note"]=card.get("photo_note","")+"\n2026-10-27 Lane 2: source licensed original full-resolution photographs physically archived: "+",".join(str(p["photo"]) for p in subset)+". Actual attached spikelet/floret/bristle visible anatomy only; no invented true inner ligule or root/rhizome score. "
    if isinstance(card.get("learner_visual_status"),dict):
      card["learner_visual_status"]["image_count"]=len(card["images"])
    out=io.StringIO(newline="");writer=csv.writer(out)
    for p in subset:
      if taxon=="eragrostis-trichodes":
        writer.writerow([p["filename"],p["role"],p["creator"],"CC BY 4.0","https://creativecommons.org/licenses/by/4.0/",p["page"],p["source"],"yes","yes with attribution","JPEG metadata scrubbed; SVG arrows separate"])
      else:
        writer.writerow([p["filename"],p["role"],p["creator"],"CC BY 4.0",p["page"],p["source"],"yes","yes with attribution",str(p["obs"]),str(p["photo"])])
    newcsv=csvtext.rstrip("\r\n")+"\n"+out.getvalue()
    for name,data in ((base+"species.json",json.dumps(card,ensure_ascii=False,indent=2)+"\n"),(base+"image-sources.csv",newcsv)):
      files.append({"path":name,"mode":"100644","type":"blob","sha":blob(data)})
  values=[float(r["after_total"]) for r in scores["records"]]
  scores["summary"]["mean_after_percent"]=round(sum(values)/len(values)/6*100,1)
  scores["summary"]["distribution"]={f"{v:.1f}/6":values.count(v) for v in sorted(set(values))}
  scores["summary"]["new_exact_species_jpegs_archived_this_pass"]=int(scores["summary"].get("new_exact_species_jpegs_archived_this_pass",0))+len(PHOTOS)
  scores["summary"]["new_gross_structure_overlay_arrows_this_pass"]=int(scores["summary"].get("new_gross_structure_overlay_arrows_this_pass",0))+sum(len(p["markers"]) for p in PHOTOS)
  scores["final_photo_upgrade_source"]=REPORT
  scores["last_verified_trichodes_scheelei_pass_20261027"]={"new_actual_jpegs":len(PHOTOS),"new_gross_anatomical_arrows":sum(len(p["markers"]) for p in PHOTOS),"taxa_promoted":["eragrostis-trichodes","setaria-scheelei"],"role_gains":"Both reproductive closeup 0.5 to 1.0, with actual visible florets/spikelet-bristle closeups","remaining":"inner ligule roots and measured dissections","pages":"Release not yet confirmed"}
  report={"date":"2026-10-27","type":"lane2-open-license-photographic-upgrade","rights":"All three individually verified iNaturalist cc-by Research Grade original species photos","new_original_photos":len(PHOTOS),"arrows_added":sum(len(p["markers"]) for p in PHOTOS),"new_species_scores":{"eragrostis-trichodes":"5/6 = 83%","setaria-scheelei":"5/6 = 83%"},"overall_mean":scores["summary"]["mean_after_percent"],"photos":[{"source":p["page"],"species":p["name"],"stored_path":p["rel"],"creator":p["creator"],"license":"CC BY 4.0","sha256":p["sha256"],"source_original_sha256":p["source_sha256"],"image_bytes":len(p["image_bytes"]),"anatomy_role":p["role"]} for p in PHOTOS],"no_credit_given_for":"unseen rhizomes, true internal ligules or calibrated glumes","public_pages":"NOT YET VERIFIED"}
  files.append({"path":SCORE,"mode":"100644","type":"blob","sha":blob(json.dumps(scores,ensure_ascii=False,indent=2)+"\n")})
  files.append({"path":REPORT,"mode":"100644","type":"blob","sha":blob(json.dumps(report,ensure_ascii=False,indent=2)+"\n")})
  nt=gh("POST","/git/trees",{"base_tree":tree,"tree":files})["sha"]
  commit=gh("POST","/git/commits",{"tree":nt,"parents":[main],"message":"Lane 2: archive three true licensed sand lovegrass and Scheele diagnostic macros [skip ci]"})["sha"]
  try:
    gh("PATCH","/git/refs/heads/main",{"sha":commit,"force":False})
    print("PHOTOS_AND_SCORES_VERIFIED_COMMIT",commit,"taxa",changed,"Lane2_mean",scores["summary"]["mean_after_percent"])
    break
  except urllib.error.HTTPError as err:
    if err.code!=422 or attempt==6:raise
    print("COMPETING_HEAD_RETRY",attempt+1);time.sleep(2)
else:raise RuntimeError("No safe commit completed")

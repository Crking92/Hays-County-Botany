import base64,concurrent.futures,io,json,os,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps,ImageDraw
R=os.environ["GITHUB_REPOSITORY"];T=os.environ["GITHUB_TOKEN"];API="https://api.github.com/repos/"+R
TARGETS=[("eragrostis-trichodes","Eragrostis trichodes"),("erioneuron-pilosum","Erioneuron pilosum"),("setaria-scheelei","Setaria scheelei")]
LICENSES={"cc0","cc-by","cc-by-sa"}
UA={"User-Agent":"HaysCountyBotany/1.0 (native-plant-educational-open-license-research)"}
def request(url,limit=6000000,method="GET",obj=None,auth=False):
    data=json.dumps(obj,ensure_ascii=False).encode() if obj is not None else None
    headers={**UA}
    if auth:headers.update({"Authorization":"Bearer "+T,"Accept":"application/vnd.github+json","Content-Type":"application/json","X-GitHub-Api-Version":"2022-11-28"})
    req=urllib.request.Request(url,data=data,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=52) as resp:
        raw=resp.read(limit+1)
        if len(raw)>limit:raise RuntimeError("Image response over cap")
    return raw
def gh(method,path,obj=None):
    return json.loads(request(API+path,limit=12000000,method=method,obj=obj,auth=True))
def blob(data,binary=False):
    return gh("POST","/git/blobs",{"content":base64.b64encode(data).decode() if binary else data,"encoding":"base64" if binary else "utf-8"})["sha"]
def fetch_url(photo):
    url=(photo.get("url") or "").replace("/square.","/medium.").replace("/thumb.","/medium.")
    if not url.startswith("https://"):return None
    try:
        raw=request(url,limit=1600000)
        with Image.open(io.BytesIO(raw)) as im:
            x=ImageOps.exif_transpose(im).convert("RGB")
            x.thumbnail((295,214))
            return x
    except Exception as err:
        print("THUMB_FAILED",photo.get("id"),str(err)[:90])
        return None
newfiles=[]
results={}
for slug,name in TARGETS:
    matching=[]; seen=set()
    for page in range(1,4):
        q=urllib.parse.urlencode({"taxon_name":name,"quality_grade":"research","place_id":18,"photos":"true","per_page":70,"page":page,"order_by":"created_at","order":"desc"})
        data=json.loads(request("https://api.inaturalist.org/v1/observations?"+q,limit=6500000))
        print("QUERY",name,"page",page,"total",data.get("total_results"),"returned",len(data.get("results",[])))
        for ob in data.get("results",[]):
            if ob.get("taxon",{}).get("name")!=name: continue
            photos=[p for p in ob.get("photos",[]) if p.get("license_code") in LICENSES]
            if not photos:continue
            for p in photos[:6]:
                if p["id"] in seen:continue
                seen.add(p["id"])
                matching.append({"species":name,"photo_id":p["id"],"observation_id":ob["id"],"license":p["license_code"],"creator":p.get("attribution"),"place":ob.get("place_guess"),"source":"https://www.inaturalist.org/photos/"+str(p["id"]),"url":p["url"],"observation_taxon":ob["taxon"]["name"]})
                if len(matching)>=35:break
            if len(matching)>=35:break
        if len(matching)>=35 or page*70>=data.get("total_results",0):break
    print("LICENSED_EXACT_SPECIES_CANDIDATES",name,len(matching))
    if not matching:
        results[slug]=[];continue
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        thumbs=list(pool.map(lambda c:fetch_url({"id":c["photo_id"],"url":c["url"]}),matching))
    canvas=Image.new("RGB",(6*325,6*274),"white")
    draw=ImageDraw.Draw(canvas)
    for idx,(row,img) in enumerate(zip(matching,thumbs)):
        x=(idx%6)*325;y=(idx//6)*274
        if img is not None:canvas.paste(img,(x+(325-img.width)//2,y+5))
        draw.text((x+5,y+222),str(idx)+" photo="+str(row["photo_id"]),fill="black")
        draw.text((x+5,y+241),"obs="+str(row["observation_id"])+" "+row["license"],fill="black")
        print("CANDIDATE",json.dumps({"taxon":name,"index":idx,"photo":row["photo_id"],"license":row["license"],"obs":row["observation_id"],"source":row["source"]}))
    b=io.BytesIO()
    canvas.save(b,format="JPEG",quality=80,optimize=True)
    local="reports/lane2-open-license-photo-scout-20261027/"+slug+"-photo-contact.jpg"
    newfiles.append({"path":local,"mode":"100644","type":"blob","sha":blob(b.getvalue(),True)})
    results[slug]=matching
    print("CONTACT_SHEET",slug,"bytes",len(b.getvalue()),"path",local)
    del canvas
report="reports/lane2-open-license-photo-scout-20261027/source-records.json"
newfiles.append({"path":report,"mode":"100644","type":"blob","sha":blob(json.dumps({"purpose":"Photo candidates ONLY, no photo roles raised or archival card added","date":"2026-10-27","license_policy":"CC0/CC BY/CC BY-SA only; source photo-level metadata captured; thumbnails used for diagnostic visual review","candidates":results},ensure_ascii=False,indent=2)+"\n")})
for attempt in range(7):
    head=gh("GET","/git/ref/heads/main")["object"]["sha"]
    tree=gh("GET","/git/commits/"+head)["tree"]["sha"]
    newtree=gh("POST","/git/trees",{"base_tree":tree,"tree":newfiles})["sha"]
    commit=gh("POST","/git/commits",{"tree":newtree,"parents":[head],"message":"Lane 2: stage CC-licensed actual anatomy photo candidate sheets for expert review [skip ci]"})["sha"]
    try:
        gh("PATCH","/git/refs/heads/main",{"sha":commit,"force":False})
        print("SCOUT_COMMITTED",commit,"no scores touched")
        break
    except urllib.error.HTTPError as err:
        if err.code!=422 or attempt==6:raise
        time.sleep(2)
else:raise RuntimeError("No scout commit")

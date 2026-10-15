#!/usr/bin/env python3
"""Optional Wikimedia Commons first photo for currently zero-photo species.
Select exact scientific-name categories only; keep metadata and provenance; no science changes.
"""
import collections,copy,csv,datetime,hashlib,html,io,json,pathlib,re,sys,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path(".");sys.path.insert(0,str(ROOT.resolve()))
API="https://commons.wikimedia.org/w/api.php"
UA={"User-Agent":"HaysBotanyResearch/1.0 (education; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/*"}
LICENSES={"cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
          "cc-by":("CC BY","https://creativecommons.org/licenses/by/4.0/"),
          "cc-by-sa":("CC BY-SA","https://creativecommons.org/licenses/by-sa/4.0/"),
          "pd":("Public domain","https://creativecommons.org/publicdomain/mark/1.0/")}
def grab(url,limit=16000000):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers=UA)
            with urllib.request.urlopen(req,timeout=35) as r:body=r.read(limit+1)
            if len(body)>limit:raise ValueError("oversize")
            return body
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
            if attempt==2:raise
            time.sleep(1.5*(attempt+1))
def metadata(name):
    q={"action":"query","format":"json","generator":"categorymembers",
       "gcmtitle":"Category:"+name,"gcmtype":"file","gcmlimit":25,
       "prop":"imageinfo","iiprop":"url|extmetadata|mime|size","iiurlwidth":960}
    js=json.loads(grab(API+"?"+urllib.parse.urlencode(q)))
    if "error" in js:raise RuntimeError(str(js["error"])[:120])
    return sorted((js.get("query") or {}).get("pages",{}).values(),key=lambda x:x.get("title",""))
def plain(s):
    return html.unescape(re.sub(r"<[^>]+>","",str(s or ""))).strip()
def field(meta,key):
    return plain((meta.get(key) or {}).get("value",""))
def rights(meta):
    short=field(meta,"LicenseShortName").lower()
    code=field(meta,"License").lower()
    url=field(meta,"LicenseUrl")
    if re.search(r"\bcc0\b|creative commons zero",short) or code=="cc-zero":
        return LICENSES["cc0"][0],LICENSES["cc0"][1]
    if re.search(r"\bcc by.sa\b|\bcc-by-sa\b",short):
        return short.upper(),url or LICENSES["cc-by-sa"][1]
    if re.search(r"\bcc by\b|\bcc-by\b",short) and not re.search(r"\bnc\b|\bnd\b|noncommercial|no derivatives",short):
        return short.upper(),url or LICENSES["cc-by"][1]
    if code in ("pd","pd-old","pd-us","pd-user","pd-self") or short in ("public domain","pd"):
        return LICENSES["pd"]
    return None
def photo_file(page,name):
    t=page.get("title") or ""
    info=(page.get("imageinfo") or [{}])[0]
    if not t.startswith("File:") or len(info)==0 or info.get("mime") not in ("image/jpeg","image/png","image/webp"):return None
    # Commons category is exact taxon; don't accept media with obviously different taxon in title.
    filename=t[5:].lower().replace("_"," ")
    genus=name.split()[0].lower()
    if filename.startswith(("codiaeum","euphorbia","opuntia")) and not filename.startswith(genus):return None
    ext=info.get("extmetadata") or {}
    lic=rights(ext)
    if not lic:return None
    creator=field(ext,"Artist") or field(ext,"Credit")
    if not creator and "CC0" not in lic[0] and lic[0]!="Public domain":return None
    license_name,lic_url=lic
    url=info.get("thumburl") or info.get("url") or ""
    if not url.startswith("https://upload.wikimedia.org/"):return None
    if (info.get("width") or 0)<600 or (info.get("height") or 0)<400:return None
    return {"file_title":t,"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(t.replace(" ","_"),safe=":/_()"),
            "image_url":url,"creator":creator or "Wikimedia Commons public-domain contributor",
            "license":license_name,"license_url":lic_url}
def normalized_image(url):
    with Image.open(io.BytesIO(grab(url))) as image:
        image.load();img=ImageOps.exif_transpose(image).convert("RGB")
    if min(img.size)<360 or max(img.size)<690:raise RuntimeError("too small")
    img.thumbnail((1280,1280),Image.Resampling.LANCZOS)
    out=io.BytesIO();img.save(out,format="JPEG",quality=88,optimize=True,progressive=True)
    if len(out.getvalue())<18000:raise RuntimeError("tiny jpg")
    return out.getvalue(),list(img.size)
def science(sp):
    x=copy.deepcopy(sp)
    for k in ("images","photo_note","learner_visual_status"):x.pop(k,None)
    if isinstance(x.get("curation_status"),dict):
        for k in ("photo_metadata_count","photo_files_present","commons_first_photo_install"):x["curation_status"].pop(k,None)
        if not x["curation_status"]:x.pop("curation_status",None)
    return x
def csv_add(file,row):
    t=file.read_text(encoding="utf-8-sig") if file.exists() else ""
    reader=csv.DictReader(io.StringIO(t));columns=list(reader.fieldnames or []);old=list(reader)
    for k in row:
        if k not in columns:columns.append(k)
    old.append(row)
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=columns,lineterminator="\n")
    w.writeheader();w.writerows(old);file.write_text(b.getvalue(),encoding="utf-8")
def main():
    q=json.loads((ROOT/"reports/photo-fast-fill-zero-queue.json").read_text())
    man=json.loads((ROOT/"data/manifest.json").read_text())
    refs={x["id"]:x["path"] for x in man["species"]}
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text())
    busy=set()
    for c in claims["claims"]:
        if c.get("status") in ("active","queued","blocked"):busy.update(c.get("taxa") or [])
    inbox=set()
    for f in (ROOT/"curation-inbox").rglob("species.json"):
        try:inbox.add(json.loads(f.read_text())["id"])
        except (OSError,ValueError,KeyError):pass
    result={"created_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"attempted":0,"installed":[],"skipped":[]}
    chosen=[]
    for t in q["items"]:
        if len(chosen)>=6 or result["attempted"]>=15:break
        sid=t["id"]
        if sid in busy or sid in inbox or t.get("in_curation_inbox") or t.get("active_claims"):continue
        target=refs.get(sid)
        if not target:continue
        path=ROOT/target
        sp=json.loads(path.read_text())
        if (sp.get("images") or []) or (path.parent/"images").exists() and list((path.parent/"images").glob("*")):continue
        name=sp.get("scientific_name")
        if not name or "×" in name or " subsp." in name or " var." in name:continue
        result["attempted"]+=1
        try:pages=metadata(name)
        except Exception as e:
            result["skipped"].append({"id":sid,"reason":"API: "+str(e)[:90]});continue
        good=None
        for page in pages:
            record=photo_file(page,name)
            if not record:continue
            try:blob,dim=normalized_image(record["image_url"])
            except Exception:continue
            good=(record,blob,dim);break
        if not good:
            result["skipped"].append({"id":sid,"reason":"No exact-species category media with cleared license and adequate pixels"})
            continue
        chosen.append((sid,path,sp,good))
        print("READY",sid,good[0]["file_title"],flush=True)
    for sid,path,sp,(record,blob,dim) in chosen:
        before=science(sp)
        unique=hashlib.sha1(record["file_title"].encode()).hexdigest()[:12]
        filename="commons-first-"+unique+".jpg"
        dest=path.parent/"images"/filename
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():raise RuntimeError("Existing media collision")
        dest.write_bytes(blob)
        credit=record["creator"]
        media={"file":"images/"+filename,"role":"Exact-species Commons-category first photo; anatomy not yet inspected",
               "creator":credit,"license":record["license"],"license_url":record["license_url"],
               "source_platform":"Wikimedia Commons","source_page":record["source_page"],
               "downloaded_from":record["image_url"],"image_dimensions":dim,
               "study_use":"yes","public_reuse":"license terms and attribution apply",
               "modifications":"resized, JPEG converted, EXIF removed",
               "photo_review":"Automated exact scientific-name Commons category, individual license, and image validation; provisional, anatomy not verified"}
        sp["images"]=[media]
        cs=sp.setdefault("curation_status",{});cs["photo_metadata_count"]=1;cs["photo_files_present"]=1;cs["commons_first_photo_install"]=result["created_at_utc"][:10]
        lv=sp.setdefault("learner_visual_status",{});lv.update({"status":"provisional_learner_ready","mode":"learner_fast_fill","image_count":1,"note":"Commons first-pass exact-category photo installed; visual diagnostic verification pending.","missing_diagnostic_views":["Confirmed reproductive and diagnostic close-up views"]})
        sp["photo_note"]=((sp.get("photo_note") or "")+" Provisional Wikimedia Commons licensed first photo; botanical feature matching requires later visual review.").strip()
        if science(sp)!=before:raise AssertionError("Scientific record changed: "+sid)
        csv_add(path.parent/"image-sources.csv",{"file_name":filename,"role":media["role"],"creator":credit,
              "license":media["license"],"license_url":media["license_url"],"source_page":media["source_page"],
              "direct_url":media["downloaded_from"],"study_use":"yes","public_reuse":media["public_reuse"],
              "modifications":media["modifications"]})
        with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as f:
            f.write("\nWIKIMEDIA COMMONS PROVISIONAL FIRST PHOTO "+result["created_at_utc"]+"\n"+record["file_title"]+"\n"+credit+"\n"+record["license"]+"; "+record["license_url"]+"\n"+record["source_page"]+"\nScaled and metadata stripped. Recheck botanical diagnostics visually.\n")
        path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n")
        result["installed"].append({"id":sid,"path":str(dest),"source":record["source_page"],
                                     "license":record["license"],"creator":credit,"bytes":len(blob),"dimensions":dim})
    report=ROOT/"reports/commons-first-photo-batch-latest.json"
    report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    if result["installed"]:
        from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
        rebuild_photo_fast_fill_queue()
    print(json.dumps(result,indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":main()

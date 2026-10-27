#!/usr/bin/env python3
"""Lane 5: image-specific CC licensing gate for actual Chloris andropogonoides tuft.
The image is visible in the iNaturalist taxon page as a grassy tuft IN SOIL,
not an uprooted crown. Do not infer inner ligule or attached roots.
"""
import hashlib,io,json,pathlib,urllib.parse,urllib.request,urllib.error,time,re
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
CARD=ROOT/"species.json"
OUT=pathlib.Path("reports/lane5-chloris-andropogonoides-field-tuft-screen-20261027.json")
PHOTO_ID=17219416
REPORT={"species":"Chloris andropogonoides","photo_id":PHOTO_ID,
        "public_photo_source":"https://www.inaturalist.org/photos/17219416",
        "added":[],"holds":[],"related_photos":[],"new_arrows":0,
        "anatomy_caveat":"Basal aboveground leaves in habitat are not proof of a rooted crown, true inner ligule, or individual mature glumes/lemmas."}
def get(url):
    for i in range(4):
        req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyEducationalLicensedPhotograph/1.0 (botanical conservation educational use)","Accept":"application/json,image/jpeg,*/*"})
        try:
            with urllib.request.urlopen(req,timeout=45) as f:
                raw=f.read(19000000)
            if len(raw)>18000000:raise ValueError("Image/API response exceeds limit")
            return raw
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,502,503,504) or i==3:raise
            time.sleep(3*(i+1))
try:
    found=None
    for page in range(1,5):
        q=urllib.parse.urlencode({"taxon_id":160518,"photos":"true","per_page":200,"page":page,"order":"desc","order_by":"created_at"})
        j=json.loads(get("https://api.inaturalist.org/v1/observations?"+q))
        results=j.get("results",[])
        for obs in results:
            p=next((p for p in obs.get("photos",[]) if int(p.get("id",0))==PHOTO_ID),None)
            if p:found=(obs,p);break
        if found or len(results)<200:break
    if not found:raise ValueError("Source photo not confirmed inside a current exact-taxon iNaturalist observation; no import")
    obs,p=found
    taxon=obs.get("taxon") or {}
    if taxon.get("name")!="Chloris andropogonoides" or int(taxon.get("id",0))!=160518:
        raise ValueError("Exact iNaturalist taxon mismatch")
    license=(p.get("license_code") or "").lower().replace("_","-")
    REPORT.update({"observation_id":obs["id"],"quality_grade":obs.get("quality_grade"),
                  "taxon_verified":taxon["name"],"photo_license":license,
                  "photo_attribution":p.get("attribution"),"date_observed":obs.get("observed_on"),
                  "source_observation":"https://www.inaturalist.org/observations/"+str(obs["id"])})
    REPORT["related_photos"]=[{"id":x.get("id"),"license":x.get("license_code"),"url":x.get("url")} for x in obs.get("photos",[]) if x.get("id")!=PHOTO_ID][:20]
    # Main repo prefers public reuse without noncommercial ambiguity.
    licenses={"cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
              "cc-by":("CC BY","https://creativecommons.org/licenses/by/4.0/"),
              "cc-by-sa":("CC BY-SA","https://creativecommons.org/licenses/by-sa/4.0/")}
    if license not in licenses:raise ValueError("Photo license is not CC0/CC BY/CC BY-SA: "+repr(license))
    attribution=(p.get("attribution") or "").strip()
    if not attribution:raise ValueError("Individual photo lacks photographer attribution")
    photo_url=p.get("url") or ""
    if not re.match(r"^https://(static|inaturalist-open-data|.*\.inaturalist)\.",photo_url):
        raise ValueError("Source image host mismatch: "+photo_url)
    image_url=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpg|jpeg|png)",r"/original.\1",photo_url)
    if image_url==photo_url:raise ValueError("Unrecognized photo URL size suffix")
    raw=get(image_url)
    with Image.open(io.BytesIO(raw)) as im:im.verify()
    with Image.open(io.BytesIO(raw)) as im:
        im=ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((2000,2000))
        if min(im.size)<600:raise ValueError("Insufficient resolution for habitat tuft photograph: "+str(im.size))
        buf=io.BytesIO();im.save(buf,"JPEG",quality=88,optimize=True)
        clean=buf.getvalue();dims=list(im.size)
    d=json.loads(CARD.read_text())
    if d["id"]!="chloris-andropogonoides":raise ValueError("Wrong canonical target")
    rel="images/inat-licensed-"+str(PHOTO_ID)+"-basal-tuft.jpg"
    full=ROOT/rel
    if any(x.get("file")==rel for x in d["images"]):
        REPORT["holds"].append("Previously installed, no duplicate")
    else:
        full.parent.mkdir(parents=True,exist_ok=True);full.write_bytes(clean)
        with Image.open(full) as im:im.verify()
        src=REPORT["public_photo_source"]
        d["images"].append({
          "file":rel,"role":"Flowering tuft growing in soil with visible basal leaves, not exposed roots or open true ligule",
          "creator":attribution,"license":licenses[license][0],
          "license_code_exact":license,"license_url":licenses[license][1],
          "source_page":src,"observation_page":REPORT["source_observation"],
          "source_original_url":image_url,
          "source_determination":"iNaturalist exact Ch. andropogonoides observation "+str(obs["id"]),
          "modifications":"Source photo re-encoded as RGB JPEG and EXIF/GPS removed; no arrows",
          "photo_status":"PUBLIC-LICENSE SOURCE VERIFIED — habitat/field tuft only; no rooted-anatomy certification",
          "sha256":hashlib.sha256(clean).hexdigest(),"pixels":dims,
          "public_reuse":"Individual open photo license checked at archive time; photographer/source/license credited"
        })
        idx=len(d["visual_comparison"]["items"])
        d["visual_comparison"]["items"].append({
            "label":"FIELD HABIT — live tuft growing in rocky soil with multiple flowering stalks",
            "scientific_name":"Chloris andropogonoides",
            "image_url":str(full),"image_fit":"contain",
            "image_role":"Genuine in-situ tuft and emerging mature windmill seedheads, crown underground",
            "caption":"A compact bunch of narrow leaves emerges from dry rocky soil with several radiating windmill heads on attached shoots. This shows the live aboveground bunch in habitat; soil conceals the roots, actual connected crown and true inner leaf ligule, and there is no scale for 1-cm spikelet counts.",
            "why_it_matters":"Shows what a crew member might see at ground level, not just a detached flowering star.",
            "creator":attribution,"license":licenses[license][0],
            "license_url":licenses[license][1],"source_page":src,"markers":[],
            "photo_status":"OPEN-LICENSE photo with source-linked exact taxon, subject habitat-level view only; no pixel-certified fine-anatomy arrows"
        })
        if len(d.get("field_id_short_tiles",[]))>=2:
            for index in (0,1):
                if idx not in d["field_id_short_tiles"][index]["photo_panel_indices"]:
                    d["field_id_short_tiles"][index]["photo_panel_indices"].append(idx)
        d.setdefault("lane5_habitat_basal_tuft_20261027",{}).update({
            "archived_source_photo_id":PHOTO_ID,"photo_role":"Actual tuft growing in soil; NOT root crown",
            "status":"FIELD_READY_PHOTO_GAPS","source_license":license,
            "still_missing":["Exposed rooted crown","True measured inner ligule","Measured mature glumes and fertile/sterile lemmas"]
        })
        CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
        REPORT["added"].append({"path":str(full),"sha256":hashlib.sha256(clean).hexdigest(),
            "pixels":dims,"license":license,"gallery_index":idx})
except Exception as e:REPORT["holds"].append(str(e))
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(REPORT,indent=2)+"\n")
print(json.dumps({k:v for k,v in REPORT.items() if k!="related_photos"}))

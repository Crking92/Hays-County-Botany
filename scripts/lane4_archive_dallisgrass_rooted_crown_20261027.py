#!/usr/bin/env python3
"""Lane 4: publish a physically archived, source-labelled Dallisgrass rooted-base photograph.

Image provenance: Wikimedia Commons File:Paspalum dilatatum-rhizome-SEQueensland-SouthernDowns.jpg
Source photograph attributed to Steve Finlayson, Commons CC0 1.0.
The uploaded Commons file says the photographer gave it to the uploader; creator's
independent CC0 declaration has not been obtained, so note that in provenance.
Gross rooted plant base is visible; individual rhizome vs. root identification
is NOT independently resolved by pixels. Do not mark underground organs as rhizomes.
"""
import csv, hashlib, io, json, pathlib, re, time, urllib.parse, urllib.request, urllib.error
from PIL import Image, ImageOps

REPO = pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-dilatatum")
CARD = REPO/"species.json"
REPORT = pathlib.Path("reports/lane4-six-role-photographic-progress-20261027.json")
SOURCES = REPO/"image-sources.csv"
TITLE = "Paspalum dilatatum-rhizome-SEQueensland-SouthernDowns.jpg"
SOURCE = "https://commons.wikimedia.org/wiki/File:"+TITLE
FILE = "images/steve-finlayson-2026-rooted-crown-cc0.jpg"
LICENSE = "https://creativecommons.org/publicdomain/zero/1.0/"
def request(url, limit=15000000):
    err=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyFieldID/1.0 (educational image provenance verification; contact via github.com/Crking92/Hays-County-Botany)"})
            with urllib.request.urlopen(req,timeout=55) as response:
                data=response.read(limit+1)
            if len(data)>limit: raise ValueError("Source response larger than media cap")
            return data
        except (urllib.error.URLError,TimeoutError) as e:
            err=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
            time.sleep(3*(attempt+1))
    raise RuntimeError("Could not retrieve Wikimedia Commons: "+str(err))
def main():
    assert CARD.is_file() and REPORT.is_file() and SOURCES.is_file()
    card=json.loads(CARD.read_text(encoding="utf-8"))
    assert card["id"]=="paspalum-dilatatum"
    if any(x.get("file")==FILE or x.get("source_page")==SOURCE for x in card["images"]):
        print("Already installed; no duplicate");return
    q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo",
        "iiprop":"url|extmetadata|sha1|size","iiurlwidth":1400,"titles":"File:"+TITLE})
    response=json.loads(request("https://commons.wikimedia.org/w/api.php?"+q,2000000))
    page=next(iter(response["query"]["pages"].values()))
    assert page.get("title","").casefold()==("File:"+TITLE).casefold(), "Wrong file identity"
    info=page["imageinfo"][0]
    license_text=re.sub(r"<[^>]+>","",info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")).strip().lower()
    assert license_text.startswith("cc0") or "creative commons zero" in license_text, "Not confirmed CC0: "+license_text
    assert info.get("width",0)>=2000 and info.get("height",0)>=2000, "Source too small"
    artist=info.get("extmetadata",{}).get("Artist",{}).get("value","")
    assert "Finlayson" in artist, "Source artist does not match Commons photographer: "+artist[:140]
    url=info.get("thumburl") or info["url"]
    assert url.startswith("https://") and ("wikimedia.org" in urllib.parse.urlparse(url).hostname), "Unexpected media host"
    raw=request(url)
    pic=Image.open(io.BytesIO(raw));pic.verify()
    pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    assert pic.width>=1000 and pic.height>=1000
    dst=REPO/FILE;dst.parent.mkdir(parents=True,exist_ok=True)
    pic.save(dst,"JPEG",quality=91,optimize=True)
    saved=dst.read_bytes();check=Image.open(io.BytesIO(saved))
    assert saved[:2]==bytes.fromhex("ffd8") and saved[-2:]==bytes.fromhex("ffd9")
    assert check.size==pic.size and not check.getexif() and "exif" not in check.info
    sha=hashlib.sha256(saved).hexdigest()
    meta={"file":FILE,
        "role":"True uprooted Dallisgrass clump, connected basal shoots, knotty base and real roots (photo does NOT separately prove scaly rhizome)",
        "creator":"Steve Finlayson","license":"CC0 1.0","license_url":LICENSE,
        "source_page":SOURCE,"source_date":"2026-01-08","source_region":"Southern Downs, Queensland, Australia (not Texas)",
        "source_taxon_name":"Paspalum dilatatum",
        "license_evidence":"Commons file explicitly marked CC0; uploaded by Rosiemay28 with photographer listed as Steve Finlayson; original independent photographer waiver not independently audited.",
        "public_reuse":"CC0 per Commons individual file; retain photographer/source for provenance; PROVISIONAL USER PHOTO REVIEW.",
        "modifications":"Original source photograph proportionally resized to 1400px and re-encoded RGB; GPS/EXIF stripped. No pixel editing or embedded text.",
        "photo_status":"Original photo preview visually inspected 2026-10-27. Gross rooted base and attached fibrous roots visible. Distinguish roots from rhizomes only with another labelled view.",
        "archive_sha256":sha,"image_dimensions":list(pic.size)}
    card["images"].append(meta)
    card["visual_comparison"]["items"].append({
      "label":"CONNECTED ROOTED CROWN — Dallisgrass dug from the ground",
      "scientific_name":"Paspalum dilatatum",
      "image_url":(REPO/FILE).as_posix(),"image_fit":"contain",
      "image_role":"True species-labelled uprooted grass with bases of multiple culms and connected fibrous roots. Anatomical identity of any horizontal rhizome not proven.",
      "caption":"Real excavated Dallisgrass (*Paspalum dilatatum*) from Queensland, Australia. Follow the upright shoot bases into the tangled crown and attached fine roots. This view teaches how a planted-looking clump connects underground; the true short rhizome should NOT be labelled from this photo alone. Steve Finlayson; Wikimedia Commons CC0 1.0. PROVISIONAL — USER PHOTO REVIEW PENDING.",
      "why_it_matters":"Much stronger than a generic seedhead photo for teaching the crew the perennial rooted clump; still not proof of separately resolved rhizome scales.",
      "creator":"Steve Finlayson","license":"CC0 1.0","license_url":LICENSE,"source_page":SOURCE,
      "modifications":"1400px proportional resized, JPEG RGB EXIF/GPS removed; visual overlay annotations external to original pixels.",
      "markers":[
        {"label":"Upright basal shoots","label_x":6,"label_y":7,"target_x":47,"target_y":13},
        {"label":"Attached fine roots","label_x":64,"label_y":89,"target_x":56,"target_y":70}
      ],
      "photo_status":"CC0 source and artist asserted on Commons, local bytes verified; image gross organ markers verified at source preview. Rhizome scales NOT claimed. Provisional photo review."})
    if isinstance(card.get("curation_status"),dict):
        card["curation_status"]["photo_metadata_count"]=len(card["images"])
        card["curation_status"]["photo_files_present"]=len(card["images"])
    if isinstance(card.get("learner_visual_status"),dict):
        card["learner_visual_status"]["image_count"]=len(card["images"])
    card.setdefault("field_id_finish_pass",{})["lane4_dallisgrass_rooted_crown_20261027"]={
      "new_photos":1,"new_gross_arrows":2,"source":SOURCE,"license":"CC0 source-file label",
      "role_gain":"rooted crown role 0 to 0.5, since specific horizontal rhizome is not proven",
      "publication":"NOT VERIFIED until public Pages run succeeds and photo appears"}
    CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with SOURCES.open("r",newline="",encoding="utf-8") as stream:
        rows=list(csv.DictReader(stream))
        names=list(rows[0].keys()) if rows else ["file_name","role","creator","license","source_page","direct_url","study_use","public_reuse"]
    row={"file_name":pathlib.Path(FILE).name,"role":"Connected excavated live basal crown and attached roots, not independently labelled rhizome",
         "creator":"Steve Finlayson","license":"CC0 1.0","source_page":SOURCE,"direct_url":info.get("descriptionurl","") or info.get("url",""),
         "study_use":"Public botanical learner","public_reuse":"Wikimedia Commons exact-file CC0 per uploader, original photographer not independently attested"}
    for key in row:
        if key not in names:names.append(key)
    with SOURCES.open("w",newline="",encoding="utf-8") as stream:
        wr=csv.DictWriter(stream,fieldnames=names,extrasaction="ignore");wr.writeheader();wr.writerows(rows);wr.writerow(row)
    audit=json.loads(REPORT.read_text(encoding="utf-8"))
    sp=next(x for x in audit["species"] if x["id"]=="paspalum-dilatatum")
    prev=float(sp.get("total") or sum(x or 0 for x in sp["role_scores"]))
    assert sp["role_scores"][1]==0, "Root role no longer missing; review rather than double count"
    sp["role_scores"][1]=0.5;new=sum(sp["role_scores"])
    sp.update({"previous_total":prev,"previous_pct":int(round(prev/6*100)),
        "total":new,"pct":int(round(new/6*100)),"target_status":"at_70_80",
        "new_species_photos":sp.get("new_species_photos",0)+1,
        "new_arrows":sp.get("new_arrows",0)+2,
        "new_root_photo":FILE,"root_photo_license":"Commons CC0 1.0",
        "root_photo_restriction":"Only attached roots and rooted crown proven, rhizome scales unverified.",
        "next_photo":"Same-plant flowering tuft OR photograph separately resolved knotty short rhizome; standalone measured glume-lemma dissection also held."})
    audit["confirmed_at_or_above_70"]=sum((x.get("pct") or 0)>=75 for x in audit["species"])
    audit["photo_physical_progress_today"]["new_local_originals"]+=1
    audit["photo_physical_progress_today"]["new_gross_arrows"]+=2
    audit["photo_physical_progress_today"]["newly_pixel_inspected_archived_exact_photos"]+=1
    audit["progress_disclaimer"]="Dallisgrass moved 4/6 (67%) to provisional 4.5/6 (75%) via one true CC0 excavated rooted crown photo, with rhizome itself not isolated. Existing floridanum 75%. Site QA still pending."
    REPORT.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"installed":FILE,"bytes":len(saved),"image_px":pic.size,"sha256":sha,
        "source":SOURCE,"license":license_text,"photo_role":new,"pct":sp["pct"]},indent=2),flush=True)
if __name__=="__main__": main()

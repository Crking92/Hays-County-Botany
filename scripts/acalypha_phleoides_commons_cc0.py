#!/usr/bin/env python3
"""Install Gaiacoyote Commons CC0 exact Acalypha phleoides reproductive images.
Recheck individual photo license and source name, decode images, preserve science + credits.
No invented anatomy arrows; two verified-source macros added without reusing cropped photos.
"""
import json,csv,io,pathlib,requests,re
from PIL import Image,ImageOps
ROOT=pathlib.Path(".")
F=ROOT/"content/taxa/Euphorbiaceae/Acalypha/acalypha-phleoides"
SF=F/"species.json"
TARGET=[
("File:Acalypha phleoides (2).jpg","commons-gaiacoyote-cc0-mixed-spike.jpg",
 "Terminal bisexual spike: visible upper male flowering portion and lower female bracts",
 "Actual CC0 Gaiacoyote photo: narrow male-bearing flower segment projects above the several larger pointed female bracts. The positions can be taught; don't invent individual microscopic styles."),
("File:Acalypha phleoides (3).jpg","commons-gaiacoyote-cc0-female-bracts.jpg",
 "Female bracts with sharp broad teeth and stalked gland hairs",
 "Actual CC0 Gaiacoyote photo: big pointed bract lobes and small head-tipped stalked glands. Individual glands are tiny; confirm on full-size macro before detailed arrow placement.")
]
S=requests.Session()
S.headers["User-Agent"]="HaysCountyBotanyPhotoVerification/1.0 (educational field guide; github.com/Crking92/Hays-County-Botany)"
def main():
    orig=json.loads(SF.read_text(encoding="utf-8"))
    assert orig["id"]=="acalypha-phleoides" and orig["scientific_name"]=="Acalypha phleoides"
    claims=json.loads((ROOT/"workflow/work-claims.json").read_text(encoding="utf-8"))
    for c in claims.get("claims",[]):
        if orig["id"] in c.get("taxa",[]) and c.get("status") in ("active","claimed","in_progress"):
            raise RuntimeError("Acalypha photo claimed by another workflow")
    if any("commons-gaiacoyote-cc0-" in str(x.get("file","")) for x in orig.get("images",[])):
        print("Already installed. No-op");return
    q=S.get("https://commons.wikimedia.org/w/api.php",params={
     "action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata",
     "titles":"|".join(x[0] for x in TARGET)},timeout=40)
    q.raise_for_status()
    metadata={p["title"]:p["imageinfo"][0] for p in q.json().get("query",{}).get("pages",{}).values() if p.get("imageinfo")}
    results=[]
    for title,filename,role,caption in TARGET:
        if title not in metadata:raise RuntimeError("Exact Commons file missing "+title)
        info=metadata[title];meta=info.get("extmetadata",{})
        lic=(meta.get("LicenseShortName",{}).get("value","")+" "+meta.get("UsageTerms",{}).get("value","")).upper()
        author=re.sub(r"<[^>]*>"," ",meta.get("Artist",{}).get("value",""))
        if "CC0" not in lic or "gaiacoyote" not in author.lower():
            raise RuntimeError("CC0 / creator not individually verified for "+title)
        url=info.get("url","")
        if not url.startswith("https://upload.wikimedia.org/wikipedia/commons/"):
            raise RuntimeError("Untrusted original media URL "+url)
        blob=S.get(url,timeout=45);blob.raise_for_status()
        if len(blob.content)>10_000_000:raise RuntimeError("Oversized source image")
        with Image.open(io.BytesIO(blob.content)) as im:
            im.load();out=ImageOps.exif_transpose(im).convert("RGB")
        if min(out.size)<325 or max(out.size)<500:raise RuntimeError("Not a usable macro resolution "+title)
        out.thumbnail((1600,1600))
        buf=io.BytesIO();out.save(buf,format="JPEG",quality=91,optimize=True)
        if len(buf.getvalue())<12_000:raise RuntimeError("Bad photo bytes")
        results.append((title,filename,role,caption,url,list(out.size),buf.getvalue()))
    # Checks complete before mutations.
    sources=[]
    for title,filename,role,caption,url,dimensions,data in results:
        f=F/"images"/filename
        if f.exists():raise RuntimeError("Existing path; never overwrite")
        f.write_bytes(data)
        with Image.open(f) as check:check.verify()
        page="https://commons.wikimedia.org/wiki/"+title.replace(" ","_")
        rec={"file":"images/"+filename,"role":role,"creator":"Gaiacoyote",
         "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
         "source_platform":"Wikimedia Commons","source_page":page,"downloaded_from":url,
         "image_dimensions":dimensions,"study_use":"yes","public_reuse":"yes",
         "modifications":"JPEG recompression with EXIF/GPS removed, no artificial content",
         "photo_review":"Original photo-specific Commons exact taxon, author, CC0 and image bytes verified; no additional photo arrow without pixel review"}
        orig["images"].append(rec)
        orig["visual_comparison"]["items"].append({
          "label":"CC0 verified flower anatomy: "+("mixed-sex spike" if "(2)" in title else "female bract glands"),
          "scientific_name":orig["scientific_name"],
          "image_url":"content/taxa/Euphorbiaceae/Acalypha/acalypha-phleoides/images/"+filename,
          "image_fit":"contain","creator":"Gaiacoyote","license":"CC0 1.0","source_page":page,
          "image_role":role,"caption":caption,
          "why_it_matters":"A real diagnostic reproductive closeup, replacing vague shape-only comparisons.",
          "markers":[]})
        sources.append({"file_name":filename,"role":role,"creator":"Gaiacoyote","license":"CC0 1.0",
          "source_page":page,"direct_image_url":url,"study_use":"yes","public_reuse":"yes",
          "license_url":rec["license_url"],"source_context":"Source-exact CC0 and locally installed verified image, no EXIF"})
    orig["curation_status"]["photo_metadata_count"]=len(orig["images"])
    orig["curation_status"]["photo_files_present"]=len([x for x in orig["images"] if str(x["file"]).startswith("images/")])
    orig["curation_status"]["visual_status"]="FIELD_READY_PHOTO_GAPS: two verified Gaiacoyote CC0 female/male spike and lobed female bract closeups added; precise tissue annotations pending pixel placement"
    orig["learner_visual_status"]["image_count"]=len(orig["images"])
    orig["photo_note"]=(orig.get("photo_note") or "")+" Installed physically verified two CC0 Gaiacoyote reproductive closeups 2026-10-21."
    csvfile=F/"image-sources.csv"
    with csvfile.open(newline="",encoding="utf-8-sig") as fl:
        read=csv.DictReader(fl);cols=list(read.fieldnames or []);rows=list(read)
    for row in sources:
        for k in row:
            if k not in cols:cols.append(k)
        rows.append(row)
    with csvfile.open("w",newline="",encoding="utf-8") as fl:
        writer=csv.DictWriter(fl,fieldnames=cols,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    with (F/"SOURCES.txt").open("a",encoding="utf-8") as fl:
        fl.write("\n2026-10-21 Commons Gaiacoyote CC0 validated reproductive photo enrichment\n")
        for name,*_ in results:fl.write(name+" / Gaiacoyote CC0 1.0 photo-specific license\n")
    SF.write_text(json.dumps(orig,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":"installed","id":orig["id"],"new_exact_CC0":len(results),
      "total_images":len(orig["images"]),"panels":len(orig["visual_comparison"]["items"]),
      "science_status":orig["project_inclusion"]["target_zone_status"]}))
if __name__=="__main__":main()

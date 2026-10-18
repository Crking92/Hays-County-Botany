#!/usr/bin/env python3
"""Batch 004: technical quality review of only screened candidate images.

No botanical identity or anatomical role is inferred from this process. Only
read the immutable permanent GitHub release archive and the two metadata-only
shortlists. Never alter canonical photos, credits, or species records.
"""
import argparse
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageStat


def avg_hash(image):
    im=ImageOps.grayscale(image).resize((8,8),Image.Resampling.LANCZOS)
    pixels=list(im.getdata())
    mean=sum(pixels)/len(pixels)
    return ''.join("1" if v>mean else "0" for v in pixels)


def hamming(a,b):
    return sum(x!=y for x,y in zip(a,b))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--shortlist-a", required=True)
    ap.add_argument("--shortlist-b", required=True)
    ap.add_argument("--out", default="batch004-technical-review")
    ap.add_argument("--archive-sha256", default="")
    args=ap.parse_args()
    source=Path(args.archive)
    output=Path(args.out)
    output.mkdir(parents=True,exist_ok=True)
    if args.archive_sha256:
        observed=hashlib.sha256(source.read_bytes()).hexdigest()
        if observed!=args.archive_sha256:
            raise SystemExit("Release archive SHA256 does not match persistent record")
    records=[]
    for p in (args.shortlist_a,args.shortlist_b):
        d=json.loads(Path(p).read_text(encoding="utf-8"))
        assert d["safe_to_install"] is False
        for species in d["species_screened"]:
            rows=species.get("selected_for_pixel_review",species.get("candidate_shortlist",[]))
            for row in rows:
                key=row.get("local_archive_file",row.get("archived_file",""))
                records.append({"id":species["id"],"file":key,"creator":row["creator"],"license":row.get("license_metadata",""),"source":row["source_page"],"image_url":row["image_url"]})
    if len(records)!=54:
        raise SystemExit(f"Expected 54 saved candidate image references, got {len(records)}")
    report={"batch":"diagnostic-39139862679",
            "state":"ARCHIVE_TECHNICAL_SCREEN_ONLY__BOTANICAL_ID_UNVERIFIED",
            "archive_sha256_verified":bool(args.archive_sha256),
            "source_species":len(set(x["id"] for x in records)),
            "shortlisted_metadata_records":len(records),
            "canonical_files_modified":0,
            "photos_installed":0,
            "cloudflare_deployment":False,
            "warnings":[],"selected":[],"possible_duplicate_pairs":[]}
    tiles=[]
    seen={}
    with ZipFile(source) as z:
        images=[n for n in z.namelist() if n.lower().endswith((".jpg",".jpeg",".png"))]
        for item in records:
            key=item["file"]
            matches=[n for n in images if n==key or n.endswith("/"+key)]
            if len(matches)!=1:
                report["warnings"].append({"file":key,"issue":f"archived_file_lookup_{len(matches)}_matches"})
                continue
            try:
                data=z.read(matches[0])
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    width,height=image.size
                    original_format=image.format
                    display=ImageOps.exif_transpose(image).convert("RGB")
                    thumb=ImageOps.contain(display,(350,250),Image.Resampling.LANCZOS)
                    grey=ImageOps.grayscale(display)
                    edge=grey.filter(ImageFilter.FIND_EDGES)
                    edge_stats=ImageStat.Stat(edge)
                    edge_spread=round(edge_stats.stddev[0],2)
                    contrast=round(ImageStat.Stat(grey).stddev[0],2)
                    avg=round(ImageStat.Stat(grey).mean[0],2)
                    ahash=avg_hash(display)
                    localWarnings=[]
                    if min(width,height)<450: localWarnings.append("small_image_fine_anatomy_caution")
                    if contrast<25: localWarnings.append("low_contrast_manual_review")
                    if avg<35 or avg>225: localWarnings.append("extreme_brightness_manual_review")
                    if edge_spread<10: localWarnings.append("low_edge_detail_manual_review")
                    if image.getexif().get_ifd(0x8825): localWarnings.append("gps_exif_in_source_archive_strip_from_published_copy")
                    r={**item,"archive_entry":matches[0],"bytes":len(data),"dimensions":[width,height],"format":original_format,"edge_spread_nonclinical":edge_spread,"luminance_contrast":contrast,"luminance_average":avg,"quality_warnings":localWarnings,"possible_botanical_role":"NOT_VERIFIED","identity_visual_confirmation":False,"install_status":"HOLD"}
                    report["selected"].append(r)
                    tiles.append((r,thumb))
                    seen[item["file"]]=ahash
            except Exception as e:
                report["warnings"].append({"file":key,"issue":"could_not_decode","error":type(e).__name__})
    for i,a in enumerate(report["selected"]):
        for b in report["selected"][i+1:]:
            if a["id"]!=b["id"]: continue
            dist=hamming(seen.get(a["file"],""),seen.get(b["file"],""))
            if dist<=4:
                report["possible_duplicate_pairs"].append({"id":a["id"],"first":a["file"],"second":b["file"],"image_hash_distance":dist,"note":"PERCEPTUAL SIMILARITY ONLY; different organs can share appearance"})
    for start in range(0,len(tiles),12):
        group=tiles[start:start+12]
        canvas=Image.new("RGB",(3*370,4*315),"#f0efe9")
        draw=ImageDraw.Draw(canvas)
        for j,(item,thumb) in enumerate(group):
            x=(j%3)*370+9
            y=(j//3)*315+10
            canvas.paste(thumb,(x,y))
            name=item["id"][:26]
            short=item["file"].split("/")[-1][:35]
            draw.text((x,y+253),name,fill="#111111")
            draw.text((x,y+269),short,fill="#111111")
            draw.text((x,y+284),f'{item["license"]} | {item["dimensions"][0]}x{item["dimensions"][1]}',fill="#111111")
        canvas.save(output/f"private-technical-contact-{start//12+1:02d}.jpg",quality=87)
    report["totals"]={
        "images_physically_decoded":len(report["selected"]),
        "image_lookup_or_decode_warnings":len(report["warnings"]),
        "photo_technical_warnings":sum(bool(x["quality_warnings"]) for x in report["selected"]),
        "possible_duplicate_pairs":len(report["possible_duplicate_pairs"]),
        "different_species":len(set(x["id"] for x in report["selected"])),
        "source_archive_files":len(images),
    }
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    (output/"README.txt").write_text(
        "This report is an image-quality prescreen only. Contact sheets and metrics\n"
        "do NOT constitute botanical identification, verification of flowers/leaves,\n"
        "new publication permission, installation approval, or site deployment.\n"
        "Verify exact pictured species, diagnostic organ, source attribution and\n"
        "licensing, competing gallery roles and current GitHub work claims before\n"
        "installing or reusing any image.\n")
    print(json.dumps(report["totals"],indent=2))
    if report["warnings"]:
        print("WARN: archive lookups and/or decode errors; see report.json")


if __name__=="__main__":
    main()

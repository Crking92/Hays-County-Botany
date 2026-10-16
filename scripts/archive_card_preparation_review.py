"""Archive reviewed research photos only; never create learner cards or READY markers."""
import argparse, base64, csv, hashlib, html, io, json, os, re, time, urllib.request, zipfile
from pathlib import Path
from PIL import Image, ImageOps
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
a = p.parse_args()
doc = json.loads(Path(a.input).read_text(encoding="utf-8-sig"))
out = Path(a.output); out.mkdir(parents=True, exist_ok=True)
def get(url):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HaysBotanyReviewedPhotoArchive/1.0"})
            with urllib.request.urlopen(req, timeout=40) as response:
                return response.read()
        except Exception as exc:
            last = exc
            time.sleep(attempt + 1)
    raise last
records = []
for source in doc["selected_photos"]:
    try:
        raw = get(source["image_url"])
    except Exception:
        if source["source"] != "ncstate":
            raise
        page = get(source["source_page"]).decode("utf-8")
        matching = []
        for figure in page.split("<figure")[1:]:
            attrs = {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', figure)}
            if attrs.get("data-image-id") == str(source["photo_id"]):
                matching.append(attrs["data-downloadurl"])
        if len(matching) != 1:
            raise RuntimeError("Cannot re-resolve exact university image ID")
        raw = get(matching[0])
    digest = hashlib.sha256(raw).hexdigest()
    if digest != source["sha256"]:
        raise RuntimeError("Original source bytes changed: " + source["id"] + "/" + str(source["photo_id"]))
    image = Image.open(io.BytesIO(raw))
    image.load()
    if image.size != (source["width"], source["height"]) or max(image.size) < 600:
        raise RuntimeError("Image resolution mismatch")
    clean = ImageOps.exif_transpose(image).convert("RGB")
    dest = out / source["archive_filename"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    clean.save(dest, format="JPEG", quality=94, optimize=True, exif=b"")
    with Image.open(dest) as test:
        test.load()
        if test.getexif():
            raise RuntimeError("EXIF removal failed")
    record = dict(source)
    record["original_sha256"] = record.pop("sha256")
    record["stored_sha256"] = hashlib.sha256(dest.read_bytes()).hexdigest()
    record["stored_bytes"] = dest.stat().st_size
    record["processing"] = "Orientation normalized and JPEG reencoded; EXIF removed. Original source hash and rights retained. No arrows/crops."
    records.append(record)
if len(records) != doc["counts"]["selected_photos"]:
    raise RuntimeError("Selection count mismatch")
metadata = {"batch": doc["batch"], "private_only": True, "photos": records,
            "permission_notice": "Owner-authorized files remain private-only. Retain individual CC NC/SA restrictions and watermarks."}
(out / "image-sources.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
with (out / "image-sources.csv").open("w", encoding="utf-8", newline="") as f:
    fields = ["id", "photo_id", "creator", "source_license", "permission_basis", "private_use", "public_reuse",
              "source_page", "image_url", "archive_filename", "original_sha256", "stored_sha256"]
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(records)
archive = out / "reviewed-photos.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for file in sorted(out.rglob("*")):
        if file.is_file() and file != archive:
            z.write(file, file.relative_to(out).as_posix())
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:
        raise RuntimeError("ZIP integrity failure")
    for record in records:
        if hashlib.sha256(z.read(record["archive_filename"])).hexdigest() != record["stored_sha256"]:
            raise RuntimeError("Archived image hash mismatch")
receipt = {"date": "2026-10-16", "status": "LOCAL_ARCHIVE_VERIFIED_NOT_YET_PUBLISHED",
           "photos": len(records), "species": len({r["id"] for r in records}),
           "zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
           "zip_bytes": archive.stat().st_size, "exif_removed": True,
           "source_hashes_verified": True, "zip_entry_hashes_verified": True,
           "cards_installed": 0, "photos_installed": 0}
(out / "archive-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(json.dumps(receipt))

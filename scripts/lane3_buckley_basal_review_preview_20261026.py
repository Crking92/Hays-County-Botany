#!/usr/bin/env python3
"""Make a compact audit preview of an existing true Buckley grass JPEG; no card edits."""
import hashlib,io,json,pathlib
from PIL import Image, ImageOps
root=pathlib.Path("content/taxa/Poaceae/Tridentopsis/tridentopsis-buckleyana")
card=json.loads((root/"species.json").read_text())
assert card["id"]=="tridentopsis-buckleyana"
src="images/buckley-tridens-inat-173616239-cc-by-original.jpg"
e=next(x for x in card["images"] if x.get("file")==src)
assert e.get("creator")=="Sam Kieschnick" and e.get("license")=="CC BY 4.0"
assert e.get("source_page")=="https://www.inaturalist.org/photos/173616239"
p=root/src;assert p.exists()
sha=hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(p) as im:
 im=ImageOps.exif_transpose(im).convert("RGB")
 original=[im.width,im.height]
 im.thumbnail((900,900),Image.Resampling.LANCZOS)
 buf=io.BytesIO()
 im.save(buf,"JPEG",quality=75,optimize=True)
 payload=buf.getvalue()
assert 5000<len(payload)<450000
out=pathlib.Path("reports/lane3-buckley-basal-pixel-review-20261026.jpg")
out.parent.mkdir(exist_ok=True,parents=True)
out.write_bytes(payload)
report={"status":"AUDIT_PREVIEW_ONLY","species":"Tridentopsis buckleyana","original_file":str(p),"original_sha256":sha,"source_page":e["source_page"],"creator":"Sam Kieschnick","license":"CC BY 4.0","dimensions_original":original,"preview_file":str(out),"preview_dimensions":[im.width,im.height],"preview_sha256":hashlib.sha256(payload).hexdigest(),"license_note":"Not a new photograph. EXIF-stripped thumbnail for review of existing licensed source image, no visual arrows, all full-resolution original pixels preserved.","no_anatomy_certification":True}
pathlib.Path("reports/lane3-buckley-basal-preview-audit-20261026.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))

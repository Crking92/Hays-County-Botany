#!/usr/bin/env python3
"""Produce UTF-8 base64 text of a compact licensed candidate contact sheet for visual audit."""
import base64,io,pathlib
from PIL import Image
src=pathlib.Path("reports/lane3-pine-muhly-license-source-contact-20261025.jpg")
with Image.open(src) as im:
 im=im.convert("RGB")
 im.thumbnail((1060,1500))
 out=io.BytesIO();im.save(out,"JPEG",quality=49,optimize=True)
 b=out.getvalue()
p=src.with_suffix(".b64.txt")
p.write_text(base64.b64encode(b).decode("ascii")+"\n")
print({"path":str(p),"binary_bytes":len(b),"text_chars":p.stat().st_size,"pixels":im.size})

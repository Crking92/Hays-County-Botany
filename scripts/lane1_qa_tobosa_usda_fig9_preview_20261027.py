#!/usr/bin/env python3
"""Preview public-domain 1939 USDA photo from locally archived jpg for anatomy QA."""
import io,base64,pathlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Hilaria/hilaria-mutica/images/usda-canfield-1939-real-tobosa-bisected-rhizomes-figure9-public-domain.jpg")
assert p.is_file(),"source figure not archived"
im=Image.open(p);im.load()
assert im.width>=1000 and im.height>=700
im.thumbnail((760,600),Image.Resampling.LANCZOS)
b=io.BytesIO()
im.save(b,"JPEG",quality=78,optimize=True)
encoded=base64.b64encode(b.getvalue()).decode("ascii")
print("REAL_USDA_TOBOSA_FIG9_PREVIEW_BEGIN")
print(encoded)
print("REAL_USDA_TOBOSA_FIG9_PREVIEW_END")
print(f"ORIGINAL_SIZE {p.stat().st_size}, QA_SIZE {len(b.getvalue())}, PIXELS {im.size}")

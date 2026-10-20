#!/usr/bin/env python3
"""Generate provisional crops/previews from attributed CC BY 4.0 article figures.
Photo-review only. Human visual inspection before any arrows or species installation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageOps
BASE=Path("workflow/photo-library/candidates/solanum-nigrescens-fruit-20261020")
OUTPUT=Path("reports/solanum-nigrescens-scholarly-fruit-preview-20261020.json")
FIG3=BASE/"solanum-nigrescens-paper-fig003.png"
FIG14=BASE/"solanum-nigrescens-paper-fig014.png"
for file in (FIG3,FIG14):
    if not file.is_file():raise SystemExit("No staged licensed source figure "+str(file))
images=[]
entries=[
  (FIG3,(0,0,1880,1317),"fig03a-mature-cluster-preview.jpg","Fig 3(a): ripe cluster, green calyx lobes and 5 mm scale","Sara Monzerrat Ramírez-Olvera"),
  (FIG3,(1890,0,2530,755),"fig03c-calyx-close-preview.jpg","Fig 3(c): mature berry base, calyx and 3 mm scale","Jorge Manuel Valdez-Carrasco"),
  (FIG14,None,"fig14-ripening-sequence-preview.jpg","Fig 14: six stages of ripening and calyx senescence","Sara Monzerrat Ramírez-Olvera")
]
for src,box,name,role,creator in entries:
    with Image.open(src) as original:
        im=original.convert("RGB")
        if box:im=im.crop(box)
        im.thumbnail((1600,1400),Image.Resampling.LANCZOS)
        dest=BASE/name
        im.save(dest,format="JPEG",quality=84,optimize=True,exif=b"")
    with Image.open(dest) as verify:verify.verify()
    images.append({"path":str(dest),"role":role,"credit":creator,"license":"CC BY 4.0",
                   "source":"https://www.mdpi.com/2223-7747/12/8/1645",
                   "modifications":("Crop "+str(box) if box else "Reduced resolution for visual review")+
                       ", JPEG conversion; original figure and credits retained in archive.",
                   "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"status":"CANDIDATE_REQUIRES_VISUAL_INSPECTION"})
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps({"date":"2026-10-20","species":"Solanum nigrescens","images":images,
"never_count_as_installed":True},indent=2)+"\n")
print("CREATED",len(images),"CC BY scholarly figure crops for visual study, not canonical")

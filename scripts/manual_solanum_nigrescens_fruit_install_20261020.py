#!/usr/bin/env python3
"""Install 3 individually inspected CC BY 4.0 S. nigrescens scholarly fruit images.
Prerequisite: source Figure 3 & 14 archived and review JPEG previews checked.
Nondestructive image arrows are data overlays, separate from the researchers' photographs.
"""
from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,csv,shutil
ROOT=Path("content/taxa/Solanaceae/Solanum/solanum-nigrescens")
STAGE=Path("workflow/photo-library/candidates/solanum-nigrescens-fruit-20261020")
SRC=ROOT/"species.json"
REPORT=Path("reports/solanum-nigrescens-fruit-install-20261020.json")
ARTICLE="https://www.mdpi.com/2223-7747/12/8/1645"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
SPECS=[
 dict(source="fig03a-mature-cluster-preview.jpg",
      output="05-ripe-fruit-cluster-fig03a.jpg",
      role="Mature black berry cluster and green fruiting calyces, with original 5 mm scale",
      creator="Sara Monzerrat Ramírez-Olvera",fig="3(a)",
      caption="EXACT-SPECIES research photograph of THREE RIPE dark-purple/black S. nigrescens berries. Five green calyx lobes remain spread against the fruit BASE, not strongly reflexed backwards like typical American black nightshade. The 5 mm bar belongs to the original scientific figure; no invented enlargement scale.",
      markers=[
        dict(label="Green five-lobed CALYX",label_x=3,label_y=15,target_x=30,target_y=45),
        dict(label="Fruiting pedicel",label_x=65,label_y=9,target_x=52,target_y=26),
        dict(label="Ripe dark berry",label_x=66,label_y=86,target_x=79,target_y=67)
      ]),
 dict(source="fig03c-calyx-close-preview.jpg",
      output="06-single-fruit-calyx-fig03c.jpg",box=(125,60,635,720),
      role="Ripe black berry, sharply defined five-pointed green fruiting calyx and original 3 mm scale",
      creator="Jorge Manuel Valdez-Carrasco",fig="3(c)",
      caption="EXACT-SPECIES close view of the BASE of a mature berry and five GREEN calyx lobes. These lobes spread across/touch the dark berry surface instead of bending back down towards the fruit stalk. The original 3 mm scientific scale bar is still present. Crop from the 2023 paper's Figure 3(c).",
      markers=[
        dict(label="5 green CALYX lobes",label_x=3,label_y=13,target_x=59,target_y=37),
        dict(label="Dark mature berry",label_x=3,label_y=80,target_x=49,target_y=72),
        dict(label="3 mm scale",label_x=43,label_y=96,target_x=82,target_y=85)
      ]),
 dict(source="fig14-ripening-sequence-preview.jpg",
      output="07-berry-ripening-sequence-fig14.jpg",
      role="Six photographed stages from green berries to fully black ripe fruit and calyx senescence",
      creator="Sara Monzerrat Ramírez-Olvera",fig="14(a–f)",
      caption="Six exact-species stages photographed by the researchers: (a) green immature berries, (b) early purple pigmentation, (c) partially purple berries, (d) fully purple-black berries, (e) greenish-yellow sepals on mature fruit, (f) drying brownish sepals. Original panel labels (a–f) identify stages; arrows are intentionally omitted to keep six small photographs legible.",
      markers=[])
]
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def save(path,j):path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
  if not SRC.is_file():raise SystemExit("Existing species card missing; no new species creation here")
  j=load(SRC)
  if j.get("id")!="solanum-nigrescens":raise SystemExit("Unexpected taxon")
  installed={a.get("file") for a in j.get("images",[])}
  if any("images/"+s["output"] in installed for s in SPECS):
    if all("images/"+s["output"] in installed for s in SPECS):
      print("SKIP: three scholarly fruit images already canonical; preserve existing arrows");return
    raise SystemExit("Partial fruit install collision; hold for manual reconciliation")
  if not STAGE.joinpath("solanum-nigrescens-paper-fig003.png").is_file() or not STAGE.joinpath("solanum-nigrescens-paper-fig014.png").is_file():
    raise SystemExit("Archived scholarly original figure missing")
  records=[];panels=[]
  for n,s in enumerate(SPECS):
    fromfile=STAGE/s["source"]
    if not fromfile.is_file():raise SystemExit("Reviewed preview absent: "+str(fromfile))
    with Image.open(fromfile) as im:
      image=ImageOps.exif_transpose(im).convert("RGB")
      if "box" in s:image=image.crop(s["box"])
      dest=ROOT/"images"/s["output"]
      image.save(dest,"JPEG",quality=88,optimize=True,exif=b"")
    with Image.open(dest) as verify:verify.verify()
    if dest.stat().st_size<20000:raise SystemExit("Fruit source compressed unusably: "+str(dest))
    item={"file":"images/"+s["output"],"role":s["role"],
      "creator":s["creator"],"license":"CC BY 4.0","license_url":LICENSE,
      "source_page":ARTICLE,"source_figure":s["fig"],
      "source_article_doi":"https://doi.org/10.3390/plants12081645",
      "source_research_plant":"Solanum nigrescens Martens & Galeotti, cultivated from field-collected plants in Texcoco, State of Mexico, voucher CHAPA 155812",
      "media_source_url":"https://mdpi-res.com/plants/plants-12-01645/article_deploy/html/images/plants-12-01645-g"+("003" if n<2 else "014")+".png",
      "source_photo_review":"Direct high-resolution figure and derivative crop inspected 2026-10-20 for actual visible calyx/berry, study purposes.",
      "image_dimensions":list(image.size),
      "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
      "modifications":"Cropped from published Figure "+s["fig"]+" and saved as JPEG. Research figure panel source retained; website SVG arrow overlay separate." if n<2 else "Published Figure 14 downscaled and JPEG converted for website; original (a)–(f) stage labels preserved.",
      "study_use":"yes","public_reuse":"yes","visual_role_reviewed":True}
    records.append(item)
    panels.append({"label":str(len(j["images"])+n+1)+" — "+s["role"],
      "scientific_name":"Solanum nigrescens",
      "image_url":"content/taxa/Solanaceae/Solanum/solanum-nigrescens/"+item["file"],
      "image_fit":"contain","image_role":s["role"],"creator":s["creator"],
      "license":"CC BY 4.0","license_url":LICENSE,
      "source_page":ARTICLE,"source_figure":s["fig"],
      "caption":s["caption"]+" Photo source: Ramírez-Olvera & Sandoval-Villa (2023), Plants 12(8):1645. Cropped/converted as indicated, CC BY 4.0.",
      "why_it_matters":"Use fruiting calyx orientation and surface texture with measured flower anthers to separate divine from American black nightshade. A calyx contact trait is better than black color alone.",
      "markers":s["markers"]})
  j["images"].extend(records)
  comparison=j.get("visual_comparison",{}).get("items",[])
  insert=next((k for k,it in enumerate(comparison) if it.get("scientific_name")!="Solanum nigrescens"),len(comparison))
  comparison[insert:insert]=panels
  v=j["visual_comparison"]
  v["title"]="Divine nightshade: longer anthers + mature berry CALYX pressed close"
  v["subtitle"]="Seven exact-species licensed photo views including verified research fruit/calyx macros, plus a DIFFERENT-SPECIES American black nightshade reference."
  v["memory_rule"]="Longer flower anthers; at ripe fruit look for CALYX LOBES that touch/spread across the berry rather than bending sharply backward."
  v["overlay_note"]="The 2023 CC BY 4.0 scholarly pictures are cropped from Figure 3 and Figure 14 with researchers credited; non-destructive anatomy arrows only on visually inspected clear structures. Original (a–f) ripening panels intentionally have no arrows. Mobile arrow placement still awaiting user verification."
  q=j.setdefault("field_photo_quickcheck",{})
  q["fruit_photo_status"]="FIG3A_FIG3C_FIG14_INSTALLED_EXACT_SPECIES_CC_BY"
  q["missing"]=[s for s in q.get("missing",[]) if "ripe" not in s.lower() and "calyx" not in s.lower()]
  q["missing"].append("Compare calyx arrows at normal iPhone viewing size, then mark approved only after user confirms.")
  j["photo_note"]=(j.get("photo_note") or "")+" Added scholarly exact-species fruit/calyx figures 3(a),3(c),14 (cropped/credited CC BY 4.0); published researchers' photos from Mexican research population, NOT local provenance."
  c=j.setdefault("curation_status",{})
  c["photo_metadata_count"]=len(j["images"]);c["photo_files_present"]=len(j["images"])
  c["fruit_photo_review"]="PASS_ANATOMICAL_SOURCE_VISUAL_REVIEW_PENDING_MOBILE_CONFIRMATION"
  c["field_id_finish_status"]="PASS_IN_PROGRESS"
  l=j.setdefault("learner_visual_status",{})
  l["image_count"]=len(j["images"]);l["note"]="Seven physically installed exact-species photos, including scholarly ripe fruit + calyx closeups and six-stage ripening montage. Remains provisional pending final phone arrow review and county-native HOLD."
  save(SRC,j)
  # Keep source ledger per photo.
  csvfile=ROOT/"image-sources.csv"
  with csvfile.open("r",newline="",encoding="utf-8") as inp:
    reader=csv.DictReader(inp);cols=reader.fieldnames;rows=list(reader)
  if cols:
    for a in records:
      rows.append({k:a.get(k,"") for k in cols})
    with csvfile.open("w",newline="",encoding="utf-8") as out:
      w=csv.DictWriter(out,fieldnames=cols);w.writeheader();w.writerows(rows)
  sourcefile=ROOT/"SOURCES.txt"
  if sourcefile.is_file():
    note=sourcefile.read_text(encoding="utf-8")
    note=note.replace("No current photo illustrates verified ripe S. nigrescens berries/calyx. Do not infer fruit from these photos.", "Previous flower-only photos do not show fruit. As of 2026-10-20, Figures 3(a), 3(c), and 14 from the CC BY 4.0 2023 study provide real mature berry, calyx, and ripening images.")
    note=note.replace("Additional scientific ripe fruit figures: https://www.mdpi.com/2223-7747/12/8/1645 (Figure 3). Requires separate image-integrity review before installation.", "Installed fruit image source: https://www.mdpi.com/2223-7747/12/8/1645 (Figure 3[a], Figure 3[c], Figure 14). 2023 study Ramírez-Olvera and Sandoval-Villa; fig3[a], fig14 photos by Sara Monzerrat Ramírez-Olvera; fig3[c] photo by Jorge Manuel Valdez-Carrasco. Creative Commons BY 4.0. Cropped, converted and credited. Original source PDF/figures remain preserved in archived review sources; no Hays occurrence is inferred.")
    sourcefile.write_text(note,encoding="utf-8")
  report={"date":"2026-10-20","species_id":"solanum-nigrescens","status":"PASS_IN_PROGRESS",
    "source":"Ramírez-Olvera & Sandoval-Villa 2023, Plants 12(8) 1645, doi:10.3390/plants12081645",
    "license":"CC BY 4.0", "added_photo_files":records,
    "added_annotated_panels":len([p for p in panels if p["markers"]]),
    "new_total_photos":len(j["images"]),
    "county_native_hold_preserved":j["project_inclusion"]["target_zone_status"]=="PROVISIONAL",
    "mobile_arrow_user_review_pending":True}
  REPORT.parent.mkdir(exist_ok=True);save(REPORT,report)
  print("VERIFIED",len(records),"fruit/calyx/sequence photos installed",len(j["images"]),"total")
if __name__=="__main__":main()

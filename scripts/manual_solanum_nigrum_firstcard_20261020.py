#!/usr/bin/env python3
"""Install user-directed provisional comparison S. nigrum, real CC BY-SA images only.
Accepted introduced-to-Texas taxon: FNA14 / POWO.
Do not upgrade beyond FIELD_READY_PHOTO_GAPS without measured/verified characters.
"""
from pathlib import Path
from PIL import Image, ImageOps
import requests,io,json,csv,hashlib,time
ROOT=Path("content/taxa/Solanaceae/Solanum/solanum-nigrum")
G=Path("content/taxa/Solanaceae/Solanum/genus.json")
M=Path("data/manifest.json")
PREFIX="content/taxa/Solanaceae/Solanum/solanum-nigrum/"
LIC="https://creativecommons.org/licenses/by-sa/3.0/"
PICS=[
  dict(filename="01-leaves-flowers-fruit.jpg",title="Solanum_nigrum_leafs_flowers_fruits.jpg",stem="0/01",author="Harald Hubich",
       source_page="https://commons.wikimedia.org/wiki/File:Solanum_nigrum_leafs_flowers_fruits.jpg",
       role="Flowering and fruiting branch showing alternate leaves, white stars, green and dark berries",
       markers=[{"label":"WHITE flower","label_x":63,"label_y":12,"target_x":91,"target_y":9},
                {"label":"GREEN immature berries","label_x":1,"label_y":25,"target_x":32,"target_y":48},
                {"label":"DARK ripe berry","label_x":58,"label_y":84,"target_x":42,"target_y":55}]),
  dict(filename="02-white-flower-yellow-anthers.jpg",title="Solanum_nigrum_flower_close-up.jpg",stem="f/f3",author="Calimo",
       source_page="https://commons.wikimedia.org/wiki/File:Solanum_nigrum_flower_close-up.jpg",
       role="Close flower view: white five-lobed corolla, yellow anthers and hairy pedicel",
       markers=[{"label":"WHITE corolla lobe","label_x":1,"label_y":21,"target_x":24,"target_y":30},
                {"label":"YELLOW anthers","label_x":63,"label_y":81,"target_x":43,"target_y":62},
                {"label":"Hairy flower stalk","label_x":67,"label_y":5,"target_x":59,"target_y":21}]),
  dict(filename="03-mature-dark-fruit.jpg",title="Solanum_nigrum_fruits.JPG",stem="2/2c",author="Vinayaraj",
       source_page="https://commons.wikimedia.org/wiki/File:Solanum_nigrum_fruits.JPG",
       role="Ripe and unripe berry clusters on a green branching Solanum nigrum",
       markers=[{"label":"RIPE dark berry","label_x":3,"label_y":39,"target_x":35,"target_y":37},
                {"label":"GREEN immature berry","label_x":65,"label_y":7,"target_x":64,"target_y":15},
                {"label":"Individual berry stalk (pedicel)","label_x":3,"label_y":86,"target_x":41,"target_y":61}])
]
def save(p,j):
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def actual_photo(d):
  url=f'https://upload.wikimedia.org/wikipedia/commons/{d["stem"]}/{d["title"]}'
  urls=[url,f'https://commons.wikimedia.org/wiki/Special:FilePath/{d["title"]}']
  s=requests.Session();s.headers.update({"User-Agent":"HaysBotanyCrewEducationalLearner/1.0 (rights-cleared source photo copy, photographer attributed)","Accept":"image/jpeg,image/*;q=0.9"})
  errors=[]
  for u in urls:
    try:
      r=s.get(u,timeout=22)
      if r.status_code==429:
        errors.append(f"{u} HTTP429; defer");continue
      r.raise_for_status()
      if not 20000<len(r.content)<17000000:raise ValueError("unexpected size")
      i=Image.open(io.BytesIO(r.content));i.verify()
      i=Image.open(io.BytesIO(r.content))
      if min(i.size)<500:raise ValueError("image source resolution below minimum")
      i=ImageOps.exif_transpose(i).convert("RGB")
      i.thumbnail((1800,1800),Image.Resampling.LANCZOS)
      dest=ROOT/"images"/d["filename"];dest.parent.mkdir(parents=True,exist_ok=True)
      i.save(dest,"JPEG",quality=88,optimize=True,exif=b"")
      with Image.open(dest) as im: im.verify()
      return (dest,u,list(i.size),hashlib.sha256(dest.read_bytes()).hexdigest())
    except Exception as exc:errors.append(f"{u} {str(exc)[:150]}")
  raise RuntimeError(d["title"]+" unavailable: "+"; ".join(errors))
def main():
  if (ROOT/"species.json").exists():
    v=json.loads((ROOT/"species.json").read_text())
    if v.get("id")=="solanum-nigrum" and v.get("images"):print("SKIP existing installed card, no overwrites");return
    raise SystemExit("Existing partial canonical card; reconcile before writing")
  manifest=json.loads(M.read_text())
  genus=json.loads(G.read_text())
  assert not any(a.get("id")=="solanum-nigrum" for a in manifest["species"])
  assert "solanum-nigrum" not in genus["project_scope"]["species_ids"]
  images=[];panels=[];holds=[]
  for d in PICS:
    try: file,url,dimensions,sha=actual_photo(d)
    except Exception as e:
      holds.append(str(e));continue
    rec={"file":"images/"+file.name,"role":d["role"],"creator":d["author"],"license":"CC BY-SA 3.0",
     "license_url":LIC,"source_page":d["source_page"],"media_source_url":url,
     "source_taxon":"Solanum nigrum L.","source_region":"Photographs sourced internationally; NOT Hays County occurrences",
     "sha256":sha,"image_dimensions":dimensions,
     "modifications":"Resized and re-encoded for public site; EXIF/GPS removed. SVG labels are separate overlays.",
     "derivative_licensing":"Photo derivatives are distributed CC BY-SA 3.0 with original creator attribution, same/share-alike license and adaptation notice.",
     "visual_role_reviewed":True,"public_reuse":"yes","study_use":"yes"}
    images.append(rec)
    panels.append({"label":str(len(images))+" — "+d["role"],"scientific_name":"Solanum nigrum","image_url":PREFIX+rec["file"],
     "image_fit":"contain","image_role":d["role"],"creator":rec["creator"],"license":rec["license"],
     "license_url":LIC,"source_page":rec["source_page"],"caption":d["role"]+". "+rec["creator"]+
      " / Wikimedia Commons, CC BY-SA 3.0. JPEG adaptation disclosed; anatomy arrows are separate teaching overlays. Exact features need look-alike comparison.",
     "why_it_matters":"White flowers and black fruit alone overlap other Solanum. Inspect anther length, fruit stalk thickness, mature calyx, and seed/stone cells separately.",
     "markers":d["markers"]})
    print("INSTALLED",rec["file"],rec["image_dimensions"])
  if not images:
    raise SystemExit("HOLD: All original images unavailable; do not count as first card. "+"; ".join(holds))
  key=[
   {"taxon":"Solanum nigrum · EUROPEAN BLACK NIGHTSHADE","flower":"White five-lobed corolla; yellow anthers ~2–2.5 mm","berries":"Usually dull/slightly glossy purple-black or sometimes mature greenish, ~5–10 mm","calyx":"Small, spreading to reflexed","seeds":"Relatively large ~1.8–2 mm; North American berries usually NO stone cells","quick_rule":"Thicker peduncle/pedicel + longer anthers + large seeds + no stone cells (North American material)."},
   {"taxon":"Solanum americanum · AMERICAN BLACK NIGHTSHADE","flower":"Short plump yellow anthers ~0.8–1.5 mm","berries":"Usually glossy purple-black","calyx":"Small lobes strongly reflexed away","seeds":"Typically smaller; fruit stone cells vary","quick_rule":"SHORT anthers with tiny backward-curling ripe calyx."},
   {"taxon":"Solanum emulans · EASTERN BLACK NIGHTSHADE","flower":"Shorter anthers and relatively longer free filaments","berries":"Dull to mildly glossy dark fruit","calyx":"Appressed to spreading","seeds":"Hard sclerotic granules often present","quick_rule":"Short anthers + appressed calyx + pedicel drops with berry."},
   {"taxon":"Solanum nigrescens · DIVINE NIGHTSHADE","flower":"Longer anthers overlap S. nigrum","berries":"Purple-black often matte","calyx":"Appressed/spreading; can overlap other species","seeds":"Smaller seeds and often many stone cells","quick_rule":"Anthers alone overlap; fruit dissection and multiple traits needed."},
   {"taxon":"Solanum interius · PLAINS BLACK NIGHTSHADE","flower":"Uneven-looking branches; anthers ~1.8–2.5 mm","berries":"Often bigger ~10–14 mm black","calyx":"Long oblong/rectangular rounded-tip lobes","seeds":"Larger seeds with 2–4 stone cells","quick_rule":"UNEVEN branching flower cluster + rounded-tip long calyx + larger fruit."}
  ]
  j={"id":"solanum-nigrum","entry_type":"provisional_species",
   "family":"Solanaceae","genus":"Solanum","species":"nigrum","scientific_name":"Solanum nigrum","authority":"L.",
   "common_name":"European black nightshade",
   "look_here_first":"LOOK HERE FIRST · Non-prickly herb with alternate simple oval leaves, small white five-lobed stars, and round berries green when immature, purplish-black or sometimes greenish when mature. DON'T call it from black berries: check yellow anther length (~2–2.5 mm), relatively THICK flower/fruit stalks, and (if a verified specimen) the larger seeds and typically NO hard stone cells in North American fruits. Short anthers point toward S. americanum/emulans; longer rounded calyx lobes and uneven flower branches suggest S. interius. Introduced in Texas.",
   "learner_role":"COMPARISON_NONNATIVE","native_metrics_excluded":True,"native_target_zone_calculated":False,
   "county_occurrences_target_zone":[],"target_zone_count":0,
   "project_inclusion":{"target_zone_status":"COMPARISON_NONNATIVE","range_basis":"FNA: Solanum nigrum introduced and recorded in Texas; POWO accepted Eurasian-native species. Not presumed native to Hays County.","strict_native_filter_deferred":True},
   "morphology_keys":{
    "family_pattern":"Solanaceae flowers typically fused five-part corolla and five stamens, superior ovary maturing into a many-seeded berry.",
    "habit":"Unarmed annual or short-lived perennial, sprawling/erect, often to ~1 m, stems glabrous to pubescent, a disturbance-associated plant.",
    "leaves":"Alternate simple petiolate ovate leaves, entire to coarsely toothed, often 3.5–7 cm long. Variable and not enough for species ID.",
    "flower":"Small white five-pointed corolla, typically 1–1.5 cm across, yellow slender anthers ~2–2.5 mm according to FNA, flowering in short unbranched or forked racemelike clusters. Flower photo has no scale; don't claim photographed exact measurement.",
    "fruit":"Globose ~5–10 mm berries dull to slightly shiny purple-black or green-yellowish at maturity, small calyx spreads to reflexes in fruit. Thickish peduncles and pedicels compared with native North American black nightshades. In North American S. nigrum fruit, stone cells absent—requires specialized safely handled specimen to verify, not photo proof.",
    "habitat":"Disturbed areas, irrigated fields, roadsides and similar waste places; introduced in Texas according to Flora of North America.",
    "management":"Treat as nonnative comparison plant; exact ID needed for management. Do NOT suggest berries edible from visual ID; unripe fruit and foliage may contain toxic glycoalkaloids.",
    "crew_field_sequence":["1 · Check for prickles; no prickles plus white star flowers and round berries suggests MORELLOID group.","2 · Flower macro with ruler: anthers about 2–2.5 mm in S. nigrum; shorter in S. americanum and S. emulans.","3 · Check racemelike clusters and fruiting pedicel thickness, not simply fruit color.","4 · Mature berries can be dark OR greenish; photograph berry calyx and pedicel from side.","5 · If exact science ID is needed, compare seed size and hard stone cells under trained supervision: in North America S. nigrum fruits typically lack them.","6 · If only black fruit without flower structure is visible, label Solanum morelloid group until a measured photo and comparison are available."],
    "field_terms":{"anther":"Pollen-bearing yellow tip of a stamen; macro ruler helps separate anther lengths.","peduncle":"Shared stalk supporting an entire flower or fruit cluster; thicker in S. nigrum than many native black nightshades.","pedicel":"Individual flower/berry stalk.","sclerotic granule":"Small hardened stone cell in fruit, not a seed; presence/absence is advanced dissection trait, not visible on intact fruit.","calyx":"Five green sepals at berry base; orientation matters but overlaps species."},
    "comparison_training":"FNA's most practical S. nigrum confirmation among American morelloids combines thicker peduncles/pedicels, larger seeds, and absence of stone cells in North American fruit. The first photo does NOT prove those internal traits."
   },
   "comparisons":{"field_matrix":key,"not_reliable_alone":["Black berry sheen or color","Leaf shape, as different morelloids overlap","One unmeasured open white flower","Fruit maturity judged solely from color","Absence of stone cells from a whole-fruit photo"]},
   "visual_comparison":{"instance_id":"solanum-nigrum-20261020-provisional","title":"European black nightshade — compare anthers, fruit stalk thickness and stone cells",
    "subtitle":"Genuine attributed Commons photographs showing flower/fruit roles. Internal stone cells require specimen examination; none of the photo arrows claim them.",
    "memory_rule":"Longer anthers and THICKER fruiting stalks than American black nightshade. North American ripe berries usually lack the stone cells of several similar species.",
    "items":panels,"overlay_note":"CC BY-SA 3.0 photo adaptations with per-image creator/source and share-alike attribution. Separate overlay markers chosen from source pixels; phone positional QA pending."},
   "images":images,
   "field_photo_quickcheck":{"recognition":"European nonnative black nightshade: white five-lobed flowers, small black or greenish berries, relatively thick peduncles and typically ~2–2.5 mm anthers. Confident ID uses combined traits.","what_to_photograph":["Flower front and side with mm anther scale","Flower/fruit cluster stalk compared with adjacent morelloid","Whole branch with both green and ripe berries","Mature berry with calyx orientation clearly visible","Advanced: safely prepared seed size and berry stone-cell examination"],"missing":["Measured 2–2.5 mm anther macro with ruler; current flower photo has no scale.","Voucher-controlled North American berry dissection for stone-cell trait; photos cannot prove absence.","User iPhone visual review of anatomy arrows, if installed."]},
   "curation_status":{"version":"1.0-manual-20261020","taxonomy_reviewed":True,"range_reviewed":False,"morphology_reviewed":True,"lookalikes_reviewed":True,"user_approved":True,"provisional":True,"photo_metadata_count":len(images),"photo_files_present":len(images),"field_id_finish_status":"FIELD_READY_PHOTO_GAPS","last_field_id_reviewed":"2026-10-20","photo_arrow_review":"PENDING_USER_IPHONE_QA"},
   "learner_visual_status":{"status":"provisional_learner_ready","mode":"user_directed_first_card","image_count":len(images),"note":"Source-verified publicly licensed real photo bytes. Comparison includes American black nightshade and morelloids; photo count is not a definition of completion."},
   "photo_note":"Commonly distributed Commons files by Harald Hubich, Calimo, Vinayaraj. Each individual image CC BY-SA 3.0; JPEG adaptations with EXIF removed and separate SVG arrows; original file pages linked. Exact Texas provenance not established.",
   "field_id_reference_sources":["https://www.efloras.org/florataxon.aspx?flora_id=1&taxon_id=200020597","https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:30048260-2","https://www.worldfloraonline.org/taxon/wfo-0001029815"]
  }
  save(ROOT/"species.json",j)
  with (ROOT/"image-sources.csv").open("w",encoding="utf-8",newline="") as f:
    keys=["file","role","creator","license","license_url","source_page","media_source_url","sha256","modifications"]
    w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
    for record in images:w.writerow({k:record.get(k,"") for k in keys})
  (ROOT/"SOURCES.txt").write_text("Species and introduced status: Flora of North America Vol 14, https://www.efloras.org/florataxon.aspx?flora_id=1&taxon_id=200020597; POWO accepted name and Eurasian origin.\nPhotos: "+str([(a["creator"],a["source_page"],a["license"]) for a in images])+"\nCC BY-SA 3.0 applies to each adapted photo: authors credited, source/license linked, changes noted, no EXIF/GPS. Source-photo interpretations as documented in species.json; all not local Hays proof.\n",encoding="utf-8")
  manifest["species"].append({"id":"solanum-nigrum","path":str(ROOT/"species.json")})
  manifest["species"].sort(key=lambda x:x["id"])
  save(M,manifest)
  scope=genus["project_scope"]
  scope["species_ids"]=sorted(set(scope["species_ids"]+["solanum-nigrum"]))
  scope["species_count"]=len(scope["species_ids"])
  scope["admission"]=scope.get("admission","")+" User-directed provisional S. nigrum European nonnative comparison 2026-10-20; no native count."
  save(G,genus)
  marker=Path("workflow/field-id-publication/2026-10-20-solanum-nigrum-first-card.json")
  if marker.exists():raise SystemExit("Previous publication marker exists, manual reconciliation needed")
  save(marker,{"date":"2026-10-20","species_id":"solanum-nigrum","status":"FIELD_READY_PHOTO_GAPS",
     "purpose":"Publish source-verified new European black nightshade learner through rights-filtered GitHub Pages workflow; retain introduced/nonnative label, CC BY-SA photo license/attribution.",
     "changed":[str(ROOT/"species.json"),str(ROOT/"images/"),str(G),str(M)],
     "licensed_photo_count":len(images),"all_photo_sources_wikimedia_commons":True,
     "photographer_credits":[x["creator"] for x in images],"license":"CC BY-SA 3.0 share alike applies to each JPEG derivative",
     "publication_quality_checks":"Do not bypass EXIF/QA, rights filter, publication size budget, public-only restriction",
     "remaining":["Photographed macro with millimeter anther ruler","Source-vouchered mature fruit seed/stone cell character","Owner mobile arrow review"],
     "source_holds":holds})
  print("PASS",len(images),"physically verified photos; manifest",len(manifest["species"]),"held",holds)
if __name__=="__main__":main()

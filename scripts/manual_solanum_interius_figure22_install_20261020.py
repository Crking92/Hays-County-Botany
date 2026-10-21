#!/usr/bin/env python3
"""Install a provisional Solanum interius field-identification lesson.
Exact four-panel plate sourced from DOI:10.3897/phytokeys.123.31738.figure22
Photographs: Michael Nee (A–C), Tiina Särkinen (D), CC BY 4.0.
Require full plate pixels and original source license. Preserve native-range HOLD.
"""
from pathlib import Path
from PIL import Image
import json,csv,hashlib

BASE=Path("content/taxa/Solanaceae/Solanum/solanum-interius")
STAGED=Path("workflow/photo-library/candidates/solanum-interius-20261020/figure22-full-photo-plate.jpg")
MANIFEST=Path("data/manifest.json")
GENUS=Path("content/taxa/Solanaceae/Solanum/genus.json")
REPORT=Path("reports/solanum-interius-first-card-20261020.json")
PAGE="https://phytokeys.pensoft.net/article/31738/element/2/122/"
DIRECT="https://phytokeys.pensoft.net/article/31738/download/fig/122/"
CC="https://creativecommons.org/licenses/by/4.0/"
ROOT="content/taxa/Solanaceae/Solanum/"
def save(p,j):
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
  if (BASE/"species.json").is_file():
    existing=json.loads((BASE/"species.json").read_text(encoding="utf-8"))
    if existing.get("id")=="solanum-interius" and existing.get("images"):
      print("SKIP: canonical species with images already exists, don't overwrite other worker")
      return
    raise SystemExit("Existing species content conflict: manual merge")
  m=json.loads(MANIFEST.read_text(encoding="utf-8"))
  g=json.loads(GENUS.read_text(encoding="utf-8"))
  assert not any(x.get("id")=="solanum-interius" for x in m["species"])
  assert "solanum-interius" not in g["project_scope"]["species_ids"]
  research=json.loads(Path("reports/solanum-interius-figure22-source-20261020.json").read_text())
  assert research["species_id"]=="solanum-interius" and research["status"]=="REVIEW_IMAGE_STAGED"
  assert research["resolved"]==PAGE
  assert research["images"][0]["license"]=="CC BY 4.0"
  assert STAGED.is_file()
  with Image.open(STAGED) as plate:
    assert plate.size==(1512,1153),f"Figure plate changed dimensions {plate.size}"
    plate.load()
    full=plate.convert("RGB")
  # Four lettered quadrants of the actual Figure 22 from Knapp et al. 2019.
  specs=[
   dict(part="A",filename="01-habit-figure22a.jpg",box=(0,0,756,569),
    role="Whole plant: branching habit, ovate green leaves and small white flowers",
    creator="Michael Nee",voucher="Nee 61350",
    caption="Actual S. interius habit from M. Nee's research collection. Alternate broadly ovate green leaves, branching green stems and white flowers are visible. Plant photographed outside Hays County; no local range claim.",
    markers=[
      dict(label="Broad green leaf",label_x=3,label_y=18,target_x=50,target_y=55),
      dict(label="Tiny white flower",label_x=62,label_y=87,target_x=41,target_y=80)
    ]),
   dict(part="B",filename="02-flower-branches-figure22b.jpg",box=(763,0,1512,569),
    role="Flowering branches with unequal flower arrangement and mid-length yellow anthers",
    creator="Michael Nee",voucher="Nee 61350",
    caption="The real B panel shows two flowering sections with clustered five-part white corollas. Look for uneven inflorescence branching, plus the projecting yellow anthers. The 1.8–2.5 mm anther character comes from measured taxonomic descriptions, not a scale in this photograph.",
    markers=[
      dict(label="Yellow anthers",label_x=5,label_y=81,target_x=50,target_y=47),
      dict(label="White corolla lobes",label_x=58,label_y=7,target_x=73,target_y=32),
      dict(label="Flower-bearing branch",label_x=66,label_y=82,target_x=76,target_y=53)
    ]),
   dict(part="C",filename="03-developing-fruit-calyx-figure22c.jpg",box=(0,576,756,1153),
    role="Developing fruits: long green rectangular calyx lobes with rounded tips",
    creator="Michael Nee",voucher="Nee 61350",
    caption="Developing GREEN fruit with persistent green calyx, photographed before the berries turn black. Relatively long rectangular-to-oblong lobes have rounded tips; note the calyx lobes surround the berry. Don't mislabel them as petals or claim the green berry is ripe.",
    markers=[
      dict(label="Long green CALYX lobes",label_x=4,label_y=9,target_x=27,target_y=33),
      dict(label="Rounded calyx-lobe tips",label_x=65,label_y=11,target_x=59,target_y=37),
      dict(label="Developing fruit cluster",label_x=63,label_y=85,target_x=50,target_y=42)
    ]),
   dict(part="D",filename="04-ripe-black-fruit-figure22d.jpg",box=(763,576,1512,1153),
    role="MATURE shiny black berries, exposed green calyx lobes and attached fruit pedicels",
    creator="Tiina Särkinen",voucher="RBGE cultivated accession (not Texas field voucher)",
    caption="The paper's D panel contains genuinely MATURE BLACK berries. Green calyx lobes at their BASE are visible on several fruits, along with the curved fruit stalks. Mature-berry position and calyx must be combined with anther length and inflorescence structure; black gloss alone isn't enough to split the close species.",
    markers=[
      dict(label="RIPE black berry",label_x=68,label_y=84,target_x=88,target_y=52),
      dict(label="Green fruit CALYX",label_x=3,label_y=81,target_x=60,target_y=61),
      dict(label="Curving fruit pedicel",label_x=63,label_y=6,target_x=74,target_y=43)
    ])
  ]
  images=[];panels=[]
  for i,spec in enumerate(specs):
    out=BASE/"images"/spec["filename"];out.parent.mkdir(parents=True,exist_ok=True)
    pic=full.crop(spec["box"]);pic.save(out,"JPEG",quality=90,optimize=True,exif=b"")
    assert out.stat().st_size>22000
    with Image.open(out) as p:p.verify()
    dims=list(pic.size)
    item=dict(file="images/"+spec["filename"],role=spec["role"],creator=spec["creator"],license="CC BY 4.0",
       license_url=CC,source_page=PAGE,media_source_url=DIRECT,source_figure="Figure 22"+spec["part"],
       source_specimen=spec["voucher"],original_figure="Knapp et al (2019), PhytoKeys 123, DOI 10.3897/phytokeys.123.31738",
       image_dimensions=dims,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
       modifications="Panel "+spec["part"]+" cropped from published Figure 22, re-encoded as JPEG, EXIF/GPS removed; teaching SVG arrows overlaid separately. Original paper captions/credits retained.",
       visual_role_reviewed=True,public_reuse="yes",study_use="yes")
    images.append(item)
    panels.append(dict(label=str(i+1)+" — "+spec["role"],scientific_name="Solanum interius",
       image_url=ROOT+"solanum-interius/"+item["file"],image_fit="contain",image_role=spec["role"],
       creator=spec["creator"],license="CC BY 4.0",license_url=CC,source_page=PAGE,source_figure=item["source_figure"],
       caption=spec["caption"]+" Photo: "+spec["creator"]+" in Knapp et al. (2019) Fig. 22"+spec["part"]+", CC BY 4.0. This is an attributed photo crop.",
       why_it_matters="Teach only the directly visible structures. Anther and fruit measurements are literature-based; no scale appears in this plate.",
       markers=spec["markers"]))
  comp=[
    dict(label="LOOK-ALIKE — eastern black nightshade developing fruit",scientific_name="Solanum emulans",
       image_url=ROOT+"solanum-emulans/images/06-developing-green-fruit-calyx-figure16d.jpg",
       image_fit="contain",image_role="DIFFERENT species: developing fruit calyx of S. emulans",
       creator="Michael Nee",license="CC BY 4.0",license_url=CC,
       source_page="https://phytokeys.pensoft.net/article/31738/element/2/116/",
       caption="THIS IS S. EMULANS, NOT S. INTERIUS. Both can have green calyces close to fruit, but S. interius typically has longer mid-size anthers, larger berries and more rectangular, rounded-tip calyx lobes.",
       why_it_matters="Avoid identifying by appressed calyx alone; this photograph is deliberately clearly labeled a DIFFERENT species.",markers=[]),
    dict(label="LOOK-ALIKE — divine nightshade mature fruit",scientific_name="Solanum nigrescens",
       image_url=ROOT+"solanum-nigrescens/images/06-single-fruit-calyx-fig03c.jpg",
       image_fit="contain",image_role="DIFFERENT species: small, dark berry with green calyx",
       creator="Jorge Manuel Valdez-Carrasco",license="CC BY 4.0",license_url=CC,
       source_page="https://www.mdpi.com/2223-7747/12/8/1645",
       caption="THIS IS S. NIGRESCENS, NOT S. INTERIUS. Both may have mid-sized anthers, and fruiting calyces close to the berry. Interius is more Great Plains-associated and differs in distinctive uneven clusters, longer rounded-tipped calyx lobes, larger seeds and fewer berry stone cells.",
       why_it_matters="A dark berry with an appressed calyx is NOT sufficient to declare interius.",markers=[])
  ]
  j=dict(
   id="solanum-interius",entry_type="provisional_species",
   family="Solanaceae",genus="Solanum",species="interius",scientific_name="Solanum interius",
   authority="Rydb.",common_name="Plains black nightshade",
   look_here_first="LOOK HERE FIRST · UNARMED green black nightshade with ovate ALTERNATE leaves and WHITE flowers. Most distinctive: an apparently UNEVEN inflorescence (one branch with several flowers, another seeming to carry a single basal flower); anthers medium-length ~1.8–2.5 mm. DEVELOPING fruit has relatively long RECTANGULAR/OBLONG GREEN CALYX lobes with ROUNDED tips. Fully ripe berries commonly 10–14 mm wide and shiny BLACK. This is primarily a GREAT PLAINS species; a similar Hays County plant is not automatically S. interius. Confirm with reproductive detail or hold as Solanum morelloid complex.",
   target_zone_count=0,county_occurrences_target_zone=[],native_target_zone_calculated=False,native_metrics_excluded=True,
   project_inclusion=dict(target_zone_status="PROVISIONAL",
     range_basis="Accepted North American taxon with Texas records in GRIN and 2019 revision, most frequent Great Plains. No verified Hays County occurrence or county native scoring.",
     range_guardrail="Encounter-based comparison species only; native-by-county audit paused."),
   learner_role="PROVISIONAL_LEARNER",
   morphology_keys=dict(
     family_pattern="Solanaceae: leaves alternate, flowers with joined usually 5-part corolla, 5 pollen-producing anthers, berry fruit. Unarmed morelloids distinguished from the larger prickly Solanum.",
     best_field_traits=[
       "Unarmed green herb or short-lived subwoody perennial to around 1 m; base branching; broad ovate, simple alternate leaves, margins entire or shallowly toothed.",
       "White five-lobed star-shaped corolla; projecting yellow anthers roughly 1.8–2.5 mm long, longer than S. emulans (1.5–1.8 mm in 2019 revision).",
       "UNEVEN-LOOKING inflorescence: a cluster of several flowers and a separate solitary-looking basal flower that is actually differently articulated on a pedicel.",
       "Green calyx lobes relatively LONG, rectangular-to-oblong, apices rounded, particularly clear in developing fruit (photograph 3).",
       "Berries generally mature to glossy purplish-black; around 10–14 mm in diameter (larger than emulans ~6–8 mm); black gloss alone not species-diagnostic.",
       "Seeds typically ~1.8–2.0 mm; often only 2–4 hardened stone cells per ripe berry. Compare nigrescens 1.2–1.5 mm seeds and >6 stone cells.",
       "Photos A–C are research field collections Nee 61350, and D is RBGE cultivated material; none is proof of a Hays County occurrence."
     ],
     habit="Branching green or slightly straw-colored herb, annual to somewhat persistent under trees; the 2019 revision emphasizes low-forest/shaded and open sand-hill habitats over the Great Plains. Leaf/plant height alone weakly diagnostic.",
     leaves="Simple alternate green ovate-broadly ovate leaves, commonly about 4.5–11.2 × 2.3–6.8 cm in revision; wavy to shallowly toothed margins; hairs variable. Do not use leaf holes or pale shade as a species ID character.",
     flower="White five-lobed rotate/stellate corollas with yellow anthers approximately 1.8–2.5 mm long. Watch UNEVEN cluster arrangement and the articulation of its solitary-looking basal pedicel (about one-quarter to one-third its length upward according to revision). A hand lens and metric scale are recommended.",
     fruit="Round berries GREEN when immature then BLACK and approximately 10–14 mm at maturity. Calyx lobes are relatively long, rectangular, rounded-tipped; in mature fruit the green calyx persists under berry. Figure 22D depicts genuine mature black berries, whereas C is developing fruits. 2–4 sclerotic granules and larger seeds are advanced confirmatory characters.",
     habitat="The 2019 monograph calls this primarily a Great Plains nightshade, in open sand hills and shaded low forest/under trees; Texas statewide documented, Hays County local applicability unresolved.",
     management="Not a food-identification card. Do not eat berries or leaves; Morelloid nightshade taxonomy is difficult and plants can contain toxic alkaloids. When unsure, photograph flower/anthers, flowering-axis branching and mature fruit/green calyx together.",
     field_terms=dict(
       anther="Yellow pollen-bearing organ. Measure length with 1 mm reference: S. interius ~1.8–2.5 mm, often longer than emulans but overlapping nigrescens.",
       calyx="The green sepals directly under flower/berry, often five; interius has comparatively longer rectangular lobes with rounded tips.",
       pedicel="Individual flower/fruit stalk. The basal flower's articulation point contributes to the distinctive uneven-looking inflorescence.",
       inflorescence="Branching arrangement of a flower cluster, not just a single flower. An uneven branch bearing multiple flowers plus a solitary-appearing basal flower matters in interius.",
       stone_cell="Hardened non-seed granule inside a berry. Typically 2–4 in interius versus >6 in nigrescens; for trained botanical analysis only."),
     crew_field_sequence=[
       "1 · Confirm an UNARMED Solanum with alternate ovate leaves and little WHITE flowers; avoid premature species call.",
       "2 · Photograph the FULL flower cluster from the side: does one branch carry several flowers while another appears to have one basal flower? Seek pedicel articulation.",
       "3 · Macro flower with a metric ruler: measure YELLOW ANTHERS, about 1.8–2.5 mm in interius.",
       "4 · Photograph DEVELOPING fruit head-on: identify LONG, somewhat RECTANGULAR, ROUNDED-tip green CALYX lobes.",
       "5 · Seek MATURE fruit, scale beside berry: ~10–14 mm black shiny berries; check calyx at berry base.",
       "6 · Compare: emulans has shorter anthers (~1.5–1.8 mm), smaller ~6–8 mm fruit, differently shaped calyx. Nigrescens overlaps anther size; use more regular flowers, seed/stone cell, provenance and expert review.",
       "7 · In Hays County, absent clear evidence, label Solanum black-nightshade complex / compare rather than assigning Great Plains interius by glossy black fruit alone."
     ],
     comparison_training="Main key is an UNEVEN inflorescence with distinctive basal pedicel, medium anthers, long rounded-tip calyx, larger black berries. Multiple structures, never one character alone."
   ),
   comparisons=dict(
     field_matrix=[
      dict(taxon="Solanum interius · PLAINS BLACK NIGHTSHADE",flower="Uneven branches; anthers 1.8–2.5 mm",berries="BLACK mature, often 10–14 mm",calyx="Long rectangular lobes with ROUNDED tips",seed_stone_cells="Seeds 1.8–2 mm; 2–4 stone cells",quick_rule="UNEVEN flower cluster + mid-sized anthers + long rounded calyx + larger black berries"),
      dict(taxon="Solanum emulans · EASTERN BLACK NIGHTSHADE",flower="Usually less uneven cluster; anthers ~1.5–1.8 mm in 2019 revision",berries="Usually smaller ~6–8 mm",calyx="Appressed/spreading lobes not typically as rectangular-long and rounded-tip",seed_stone_cells="Seeds ~1.6–1.8 mm; stone cells often more",quick_rule="Shorter anthers and smaller fruit than interius; fruit calyx alone overlaps."),
      dict(taxon="Solanum nigrescens · DIVINE NIGHTSHADE",flower="Anthers overlap 1.8–2.5 mm; flowers more REGULARLY spaced and sometimes branch with more than one flower",berries="Generally smaller or similar dark berries",calyx="Calyx can also hug/spread under berry",seed_stone_cells="Seeds only ~1.2–1.5 mm and >6 stone cells",quick_rule="Anthers overlap: use arrangement and seed/stone cells, and consider range; don't guess."),
      dict(taxon="Solanum americanum · AMERICAN BLACK NIGHTSHADE",flower="Tiny white stars; SHORT yellow anthers ~0.8–1.5 mm",berries="Typically small GLOSSY black",calyx="Very SMALL lobes strongly REFLEXED away from ripe berry",seed_stone_cells="Different stone-cell/seed-size traits",quick_rule="Much shorter anthers + green calyx bent backward at fruit base."),
      dict(taxon="Solanum nigrum · EUROPEAN BLACK NIGHTSHADE",flower="White flowers; variations in anthers/branches",berries="Dark fruit varies in size and sheen",calyx="Variable",seed_stone_cells="No stone cells; needs specimen",quick_rule="Introduced complex; not separable from black berry photo alone.")
     ],
     not_reliable_alone=["Only a glossy black berry: interius and americanum may both be glossy.","Only white five-part flowers: shared across numerous morelloids.","Only leaf shape or low stature: overlaps emulans and nigrescens.","Mature fruit size without a ruler or comparable scale: can mislead.","Inflorescence branching not well photographed: avoid confident species label.","Great Plains distribution is helpful background, NOT an independent morphological confirmation."]
   ),
   images=images,
   visual_comparison=dict(
     instance_id="solanum-interius-20261020-figure22",
     title="Plains black nightshade — UNEVEN flower cluster + LONG rounded CALYX",
     subtitle="Four original exact-species research panels showing whole plant, flowering cluster, developing fruit, ripe BLACK berries, plus two separately labeled different species.",
     memory_rule="UNEVEN branch arrangement, yellow anthers ~1.8–2.5 mm, rectangular rounded calyx lobes, and 10–14 mm black ripe berries. Don’t call it from black berries alone.",
     items=panels+comp,
     overlay_note="All source panels photographed in the Knapp et al. 2019 CC BY 4.0 revision: A–C M. Nee, D T. Särkinen. The original photo plate was visually checked before arrow positions were selected. SVG arrows non-destructive; phone overlay positions require user QA. No Hays county-native rating is inferred."
   ),
   field_photo_quickcheck=dict(
    recognition="Green unarmed morelloid with white flowers, asymmetric inflorescences, anthers 1.8–2.5 mm; green fruit calyx long rounded tips and larger mature black berries.",
    what_to_photograph=["Complete inflorescence from side, including apparent basal solitary flower/pedicel articulation","Flower macro with millimeter scale for 1.8–2.5 mm anther","Developing fruit macro showing long rounded calyx lobes","Mature shiny black berry with centimeter scale for 10–14 mm size","If feasible in supervised botanical lab: seed size and 2–4 stone cells"],
    missing=["Independent, publicly reusable Texas/Hays exact-species field voucher photos; existing figure collection is from research locations/cultivated material","Metric scale photo documenting anther length and berry size from same individual","User iPhone checking arrows on four new main views","Hays County occurrence/range adjudication remains ON HOLD"]),
   curation_status=dict(version="1.0-manual-20261020-firstcard",taxonomy_reviewed=True,range_reviewed=False,morphology_reviewed=True,lookalikes_reviewed=True,user_approved=True,provisional=True,
    photo_metadata_count=4,photo_files_present=4,field_id_finish_status="PASS_IN_PROGRESS",last_field_id_reviewed="2026-10-20",
    source_image_visual_review="PASS_VERIFIED_EXACT_FIGURE22",photo_arrow_review="PENDING_USER_IPHONE_QA"),
   learner_visual_status=dict(status="provisional_learner_ready",mode="user_directed_first_photo_and_morphology_pass",image_count=4,
    note="Four exact species CC BY research photo crops, including first fully mature black berry and rounded calyx photos; annotated arrows pending user phone validation."),
   photo_note="Four research photographs from 2019 Knapp et al., Figure 22, Pensoft CC BY 4.0. Photos A–C Michael Nee (Nee 61350); D Tiina Särkinen (RBGE cultivated). Each cropped to its original panel, EXIF removed, separate SVG arrows with individual source credit.",
   field_id_reference_sources=[
    "https://phytokeys.pensoft.net/article/31738/element/2/122/",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC6554266/",
    "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:239040-2",
    "https://apg.pir.sa.gov.au/gringlobal/taxon/taxonomydetail?id=316838"
   ]
  )
  save(BASE/"species.json",j)
  (BASE/"SOURCES.txt").write_text(
   "Solanum interius Rydb. Accepted name POWO (LSID 239040-2).\nScientific morphological source: Knapp et al. 2019 Morelloid clade revision PhytoKeys 123, DOI 10.3897/phytokeys.123.31738.\nSource image plate: "+PAGE+"\nOriginal figure download: "+DIRECT+"\nFigure 22A, B, C: Michael Nee (Nee 61350). Figure 22D: Tiina Särkinen, RBGE cultivated. CC BY 4.0. Cropped as four teaching panels, EXIF/GPS removed, annotations separate SVG. NONE represent verified Hays County plants.\nStatus: TRUE exact-species mature fruit photo installed; metric anther/berry scale + Hays voucher still needed. User arrow review pending.\n",encoding="utf-8")
  with (BASE/"image-sources.csv").open("w",encoding="utf-8",newline="") as out:
    cols=["file","role","creator","license","license_url","source_page","source_figure","media_source_url","sha256","modifications"]
    w=csv.DictWriter(out,fieldnames=cols);w.writeheader()
    for a in images:w.writerow({k:a.get(k,"") for k in cols})
  m["species"].append(dict(id="solanum-interius",path=str(BASE/"species.json")))
  m["species"].sort(key=lambda a:a["id"])
  save(MANIFEST,m)
  sc=g["project_scope"];sc["species_ids"]=sorted(set(sc["species_ids"]+["solanum-interius"]))
  sc["species_count"]=len(sc["species_ids"])
  sc["admission"]=sc.get("admission","")+" User-approved provisional S. interius field-ID learner 2026-10-20; Hays county proof not yet adjudicated."
  save(GENUS,g)
  save(REPORT,dict(date="2026-10-20",species="Solanum interius",status="PASS_IN_PROGRESS",image_count=4,
    images=[{"file":a["file"],"sha256":a["sha256"],"creator":a["creator"],"license":a["license"],"figure":a["source_figure"]} for a in images],
    anatomy_arrows=sum(len(p["markers"]) for p in panels),comparisons=[x["scientific_name"] for x in comp],
    manifest_total=len(m["species"]),no_county_native_label=True,phone_qa_pending=True))
  print("VERIFIED",len(images),"exact four-part science images; manifest",len(m["species"]))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Promote TWO already source-checked, manually pixel-inspected wild seep-muhly CC BY images.
No downloads and no automatic species determination: staged JPEG binaries already reside in GitHub.
Preserve all other photos, all county/native/taxonomy holds and per-photo rights.
"""
import csv, hashlib, json, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(".")
BASE=ROOT/"content/taxa/Poaceae/Muhlenbergia"
S=BASE/"muhlenbergia-reverchonii/species.json"
G=BASE/"genus.json"
SOURCE_REPORT=ROOT/"reports/muhlenbergia-reverchonii-wild-macro-scout-20261021.json"
RELEASE=ROOT/"workflow/field-id-publication/manual-reverchonii-wild-sam-panicle-20261021.json"
CANDIDATES=[
 (4920088,"open-panicle-sam-4920088.jpg","Wild seep muhly — open branching flowering head",
  "A source-identified wild seep-muhly panicle has widely spreading capillary branches carrying separate small pale spikelets against fingers. The thin branching is visible; individual glume/lemma parts and a measured ligule are NOT resolved.",
  [{"label":"Fine open branch","label_x":4,"label_y":12,"target_x":50,"target_y":28},
   {"label":"Separate small spikelet","label_x":77,"label_y":14,"target_x":57,"target_y":47}]),
 (5077102,"small-spikelets-sam-5077102.jpg","Wild seep muhly — scattered pale spikelets",
  "This separate wild source observation shows individual pale, slender spikelets widely spaced along extremely fine panicle branches, held over fingers. These are visible spikelets, not dissected or measured florets, awns or ligules.",
  [{"label":"Distinct pale spikelet","label_x":78,"label_y":19,"target_x":64,"target_y":36},
   {"label":"Thin branching axis","label_x":7,"label_y":14,"target_x":43,"target_y":34}])
]
def write(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    source=json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    assert source["taxon"]=="Muhlenbergia reverchonii" and source["images_staged"]>=2
    available={}
    for status in source["candidate_status"]:
        for c in status.get("manual_review_candidates") or []:available[c["photo_id"]]=c
    card=json.loads(S.read_text(encoding="utf-8")); genus=json.loads(G.read_text(encoding="utf-8"))
    assert card["scientific_name"]=="Muhlenbergia reverchonii" and genus["name"]=="Muhlenbergia"
    assert genus["project_scope"]["species_count"]==7
    assert genus["project_scope"]["flags"][0].startswith("muhlenbergia-piniflora")
    assert genus["project_scope"]["flags"][1].startswith("muhlenbergia-paniculata")
    # Another manual grass lane may have physically installed these exact photo IDs
    # under different canonical filenames. Their work always wins.
    existing_photo_ids=set()
    for img in card["images"]:
        ident=img.get("inaturalist_photo_id") or img.get("photo_id")
        if ident is not None:
            existing_photo_ids.add(int(ident))
    all_source_ids={photo_id for photo_id,*_ in CANDIDATES}
    already_sources=all_source_ids & existing_photo_ids
    if already_sources==all_source_ids:
        for photo_id in all_source_ids:
            rec=next(x for x in card["images"] if int(x.get("inaturalist_photo_id") or x.get("photo_id") or 0)==photo_id)
            assert rec.get("creator")=="Sam Kieschnick" and rec.get("license")=="CC BY"
            assert (S.parent/rec["file"]).is_file()
        print("Already installed by concurrent grass work: source IDs match, rights and files valid. NOOP.")
        return
    if already_sources:
        raise RuntimeError("Partially installed by concurrent work; refusing duplicate or overwrite: "+str(already_sources))
    if all(any(x.get("file")=="images/"+name for x in card["images"]) for _,name,*_ in CANDIDATES):
        for _,name,*_ in CANDIDATES:assert (S.parent/"images"/name).is_file()
        print("Already installed; no-op");return
    assert not any(any(x.get("file")=="images/"+name for x in card["images"]) for _,name,*_ in CANDIDATES)
    for _,name,*_ in CANDIDATES:assert not (S.parent/"images"/name).exists()
    original_science=json.dumps({k:card.get(k) for k in ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","taxonomic_note","synonyms")},sort_keys=True)
    original_genus_holds=json.dumps(genus["project_scope"],sort_keys=True)
    original_images=json.loads(json.dumps(card["images"]))
    original_items=json.loads(json.dumps(card["visual_comparison"]["items"]))
    newpanels=[]; photo_entries=[]
    for photo_id,filename,label,caption,markers in CANDIDATES:
        record=available[photo_id]
        assert record["license"]=="CC BY" and "Sam Kieschnick" in record["creator"]
        assert record["MATCHED_WFS_THUMBNAIL"] is False
        assert record["source_photo"]==f"https://www.inaturalist.org/photos/{photo_id}"
        assert record["source_observation"].startswith("https://www.inaturalist.org/observations/")
        sourcefile=ROOT/record["path"]
        assert sourcefile.is_file() and sourcefile.stat().st_size>=14000
        with Image.open(sourcefile) as im:
            im.verify()
        with Image.open(sourcefile) as im:
            assert im.format=="JPEG" and min(im.size)>=600
            assert 34853 not in dict(im.getexif()) # no EXIF GPS IFD
        for m in markers:
            assert all(isinstance(m[k],(float,int)) and 0<=m[k]<=100 for k in ("label_x","label_y","target_x","target_y"))
        dest=S.parent/"images"/filename
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(sourcefile,dest)
        entry={
            "file":"images/"+filename,
            "role":label+"; photographic head and spikelet architecture, not diagnostic mature glume/collar",
            "creator":"Sam Kieschnick",
            "license":"CC BY",
            "license_url":"https://creativecommons.org/licenses/by/",
            "license_version_note":"Exact individual photo source reports CC BY; use CC BY attribution and preserve version if supplied by the platform",
            "source_page":record["source_photo"],
            "observation_source":record["source_observation"],
            "media_source_url":record["original_url"],
            "source_type":"iNaturalist named wild observation; exact photo API license checked in one-time guarded intake",
            "photo_id":photo_id,
            "original_source_sha256":record["original_sha256"],
            "archived_image_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "source_determination":"Muhlenbergia reverchonii",
            "photo_review":"Actual archived JPEG manually inspected 2026-10-21; visible flowering branches and discrete spikelets; original source taxon determination not independently re-vouchered.",
            "anatomy_arrows":"Only visible whole branch and individual spikelet shapes, never unresolvable glumes, awns or ligule.",
            "study_use":"Noncommercial public educational field identification",
            "public_reuse":"CC BY: exact photographer Sam Kieschnick and original individual-photo link must remain visible",
            "modifications":"Staged verified JPEG EXIF stripped, unretouched pixels; copied byte-for-byte from guarded photo lab."
        }
        photo_entries.append(entry)
        panel={
            "label":label,
            "scientific_name":"Muhlenbergia reverchonii",
            "image_url":"content/taxa/Poaceae/Muhlenbergia/muhlenbergia-reverchonii/images/"+filename,
            "image_fit":"contain",
            "image_role":"Wild source-identified seep-muhly open flowering architecture, individual small spikelets on fine branches",
            "caption":caption,
            "why_it_matters":"Direct photographed contrast with the narrow dense Lindheimer flowering head; not final ID until ligule/mature floret characters are seen.",
            "creator":"Sam Kieschnick","license":"CC BY",
            "license_url":"https://creativecommons.org/licenses/by/",
            "source_page":record["source_photo"],
            "source_observation":record["source_observation"],
            "photo_status":"2026-10-21 manually visually inspected actual CC BY archived image, individual photo ID and original source match verified; wild status from source observation, independent re-determination pending",
            "markers":markers
        }
        newpanels.append(panel)
    card["images"].extend(photo_entries)
    card["visual_comparison"]["items"] = newpanels + original_items
    card["visual_comparison"]["title"]="Seep muhly — VERIFIED wild open panicle & spikelet portraits vs Lindheimer"
    card["visual_comparison"]["subtitle"]="Two real credited wild CC BY Sam Kieschnick photos physically installed showing open panicle branches and separate spikelets; older fine-leaf photos and clearly labeled OTHER SPECIES Lindheimer comparisons preserved. True ligule still missing."
    card["visual_comparison"]["memory_rule"]="SEEP: fine tight tuft + OPEN delicate branching mature head with distinct tiny spikelets. Contrast with dense Lindheimer head; measure ligule on the same plant before final ID."
    card["visual_comparison"]["overlay_note"]="October 21: reviewed actual full source-licensed staged JPEGs for 4920088 and 5077102. Four new arrows target only visible capillary panicle branches and pale individual spikelets. No anatomy arrows to unseen ligule, glume, lemma or actual measured awn. Photographer Sam Kieschnick CC BY, individual URLs, noncultivar wild original observations retained. Legacy foliage and Lindheimer look-alike images unchanged.";
    card["look_here_first"]="Start with a tight, small, fine-leaved basal tuft. At bloom seek an OPEN airy many-branched panicle with individually visible small spikelets: NOW PHOTOGRAPHED in two credited wild Sam Kieschnick views. Lindheimer muhly normally has a larger coarser bunch and much narrower, densely flowered head. On the same mature plant verify a short membranous ligule and dissected spikelet before final certainty; pink color alone is not diagnostic.";
    card["field_photo_quickcheck"]["steps"]=[
      "Images 1–2 now show two separate wild seep-muhly flowering heads with spreading delicate branches and small distinct spikelets. Note that fingers are rough scale, not millimeter measurement.",
      "Images 3–4 show the source-identified seep's very fine basal leaves; connect the habit with a full same-plant bloom photo in the field.",
      "Images 5–6 are explicitly a DIFFERENT species, Lindheimer muhly, showing much more contracted dense flowering heads and a large coarse bunch.",
      "Photograph an attached fresh sheath junction and short MEMBRANOUS ligule with mm ruler, then individual mature spikelet/glumes/awn under lens before calling final species."
    ]
    card["field_photo_quickcheck"]["warning"]="Real wild seep panicle branching and individual small spikelets NOW photographed and annotated, but neither gives a calibrated floret/glume/awn or attached ligule. Species ID follows individual iNaturalist source; comparisons still require the same-plant ligule and measured spikelet. M. ×involuta hybrid and M. capillaris nursery look-alike not conflated.";
    card["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — now has two real CC BY wild flowering panicle and separate-spikelet photos, plus two legacy foliage photos; measured attached membranous ligule and dissected mature spikelet still missing";
    card["field_id_finish_pass"]["photos_inspected"]="2026-10-21: two native-source flowering JPEGs Sam Kieschnick source photo IDs 4920088 and 5077102 manually inspected at original staged pixels; 4 new broad arrows; prior 2 seep foliage + 2 explicit different-species Lindheimer examples retained.";
    card["field_id_finish_pass"]["what_to_photograph"]=[
      "Same-plant full wild mature flowering bunch, rooted base to open panicle, with proper scale.",
      "Short true membranous ligule at attached mature blade–sheath junction measured in millimeters.",
      "Single mature one-flowered spikelet with isolated glumes, lemma tip and awn length on 1-mm scale.",
      "Matched locally documented M. lindheimeri mature panicle+ligule at same photo scale; possible M. ×involuta require separate independent voucher."
    ]
    card["curation_status"]["source_verified_wild_flower_photo_20261021"]="Two individual-photo licensed CC BY Sam Kieschnick wild flowering views (4920088, 5077102) installed from manually inspected staged JPEGs, four visible-feature arrows; still FIELD_READY_PHOTO_GAPS, native/taxonomy unchanged."
    genus["visual_comparison"]["items"]=genus["visual_comparison"]["items"][:2]+newpanels+genus["visual_comparison"]["items"][2:]
    genus["visual_comparison"]["subtitle"]="11 actual credited species photos, including newly installed wild M. reverchonii OPEN flowering panicle and dispersed spikelets alongside M. lindheimeri DENSE narrow head. Missing measured ligule/individual mature floret macros are clearly flagged."
    genus["visual_comparison"]["overlay_note"]="Two exact iNaturalist photo originals with individually confirmed Sam Kieschnick CC BY attribution staged, pixels inspected, and copied into canonical seep species. Four reliable new panicle/spikelet gross arrows; nine existing credited genus photo panels preserved. Never infer glumes or ligules. Retain piniflora, paniculata and hybrid identity holds, existing natural-range values and other source image rights."
    genus["genus_field_comparison_sets"][0]["photo_status"]="TWO true source-identified wild seep FLOWER views newly installed, including open capillary branches and scattered small spikelets, beside Lindheimer contracted dense head. Need matched measured ligule and verified mature glume/lemma details for final species discrimination.";
    genus["comparison_matrix"]["caution"]="Actual wild seep flowering head is NOW photographed and compared with the already archived compact Lindheimer panicle. However published ligule ranges overlap; never use pink color or overall head shape alone. The hybrid M. ×involuta can be intermediate, M. piniflora source taxon remains on HOLD, and all county-native data and license metadata remain intact.";
    for row in genus["comparison_matrix"]["rows"]:
        if row[0]=="Flowering head":
            row[2]="Open delicate mature panicle: NOW documented by two separate wild CC BY flowering photographs with fine spreading branches and separate spikelets";
            row[3]="Compare new wild seep panicle panels versus dense narrow Lindheimer photo; use same-plant measured ligule and mature floret for confirmation.";
        if row[0]=="Evidence in CURRENT local gallery":
            row[2]="Two SEEDED/flowering open-panicle images (Sam Kieschnick, wild CC BY) plus two original fine foliage images; true ligule unphotographed.";
    genus["visual_needs"]=[x for x in genus["visual_needs"] if not x.startswith("PRIORITY PAIR: a verified NON-CULTIVAR M. reverchonii")]
    genus["visual_needs"].append("Now existing wild CC BY M. reverchonii photos show separate spikelets and open branching but no true measured mature glumes/lemma/awn or same-plant ligule. Obtain macro, not another distant head.")
    genus["curation_status"]["muhly_pair_wild_panicle_20261021"]="Two verified-by-source Sam Kieschnick wild CC BY panicle photos added to seep + genus; 4 new gross arrows, no microscopic ID or hybrid source holds changed.";
    assert json.dumps({k:card.get(k) for k in ("project_inclusion","county_occurrences_target_zone","native_target_zone_calculated","taxonomic_note","synonyms")},sort_keys=True)==original_science
    assert json.dumps(genus["project_scope"],sort_keys=True)==original_genus_holds
    assert card["images"][:len(original_images)]==original_images
    assert card["visual_comparison"]["items"][2:]==original_items
    assert len(genus["visual_comparison"]["items"])==11
    for data in (card,genus):
        for item in data["visual_comparison"]["items"]:
            for marker in item.get("markers",[]):
                assert all(isinstance(marker[k],(int,float)) and 0<=marker[k]<=100 for k in ("label_x","label_y","target_x","target_y"))
            if item["scientific_name"]=="Muhlenbergia reverchonii" and "Sam Kieschnick"==item.get("creator"):
                assert (ROOT/item["image_url"]).is_file()
    write(S,card); write(G,genus)
    csvpath=S.parent/"image-sources.csv"
    with csvpath.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f); columns=reader.fieldnames; rows=list(reader)
    for img in photo_entries:
        vals={"file_name":Path(img["file"]).name,"role":img["role"],"creator":"Sam Kieschnick","license":"CC BY",
              "license_url":img["license_url"],"source_page":img["source_page"],"direct_url":img["media_source_url"],
              "study_use":"noncommercial public botanical education","public_reuse":"yes; exact photographer and source attribution",
              "modifications":"EXIF stripped; archived JPG copied without pixel edits"}
        rows.append({key:vals.get(key,"") for key in columns})
    with csvpath.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n"); writer.writeheader();writer.writerows(rows)
    RELEASE.parent.mkdir(parents=True,exist_ok=True)
    write(RELEASE,{
        "type":"manual_field_id_publication","requested_at":"2026-10-21",
        "title":"Source-verified wild seep muhly flowering head photos",
        "scope":{"species":"Muhlenbergia reverchonii","genus":"Muhlenbergia","species_count_unchanged":7},
        "photo_ids":[4920088,5077102],"creator":"Sam Kieschnick","license":"CC BY",
        "new_photo_bytes_copied_into_canonical":2,"species_new_panels":2,"genus_new_panels":2,"new_verified_gross_arrows":4,
        "source_observation_and_photo_urls_in_species_record":True,
        "photo_binaries_and_json_readback_required":True,
        "range_and_taxonomy_holds_preserved":True,
        "diagnostic_gaps":["attached measured ligule","1-mm scaled individual mature lemma/glume/awn","independently re-vouchered species determination"],
        "publication":"Request existing rights-filtered GitHub Pages workflow; publication not confirmed until successful workflow."
    })
    print("PASS: 2 physically installed Sam Kieschnick CC BY wild seep photo source files; 2 species + 2 genus panels; 4 gross arrows.")
if __name__=="__main__": main()

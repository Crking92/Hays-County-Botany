#!/usr/bin/env python3
"""
Hays Botany unattended research scout.

This script gathers candidate evidence only. It never writes to content/taxa/
or curation-inbox/, never assigns final PASS/FAIL/UNRESOLVED range status,
and never replaces curated photographs.

Outputs:
  research-drafts/<taxon-id>/draft.json
  research-drafts/<taxon-id>/photo-candidates.csv
  research-drafts/<taxon-id>/contact-sheet.jpg
  research-drafts/<taxon-id>/SOURCES.md
  reports/last-scout-run.json

Queue:
  research-queue.json
"""
from __future__ import annotations

import csv
import io
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "research-queue.json"
DRAFTS = ROOT / "research-drafts"
REPORTS = ROOT / "reports"

USER_AGENT = "HaysBotanyScout/1.0 (private field-learning project)"
INAT_API = "https://api.inaturalist.org/v1"
GBIF_API = "https://api.gbif.org/v1"

TARGET_COUNTIES = [
    "Hays", "Bell", "Blanco", "Burnet", "Comal", "Concho", "Crockett",
    "Edwards", "Frio", "Gillespie", "Bandera", "Kimble", "Kinney", "Maverick",
    "McCulloch", "Medina", "Menard", "Real", "San Saba", "Tom Green", "Travis",
    "Uvalde", "Val Verde", "Williamson", "Kerr"
]

PHOTO_COLUMNS = [
    "candidate_rank", "observation_id", "photo_id", "scientific_name",
    "observed_on", "county_lead", "creator", "license", "source_page",
    "thumbnail_url", "direct_image_url", "width", "height",
    "quality_grade", "role", "notes"
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_json(base: str, params: dict | None = None, retries: int = 2):
    url = base
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:
            last = exc
            if attempt < retries:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"GET failed: {url}: {last}")


def get_bytes(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def exact_inat_taxon(scientific_name: str) -> dict | None:
    data = get_json(
        f"{INAT_API}/taxa",
        {"q": scientific_name, "is_active": "true", "per_page": 30}
    )
    wanted = scientific_name.casefold()
    for t in data.get("results", []):
        if (t.get("name") or "").casefold() == wanted:
            return t
    return data.get("results", [None])[0] if data.get("results") else None


def gbif_match(scientific_name: str) -> dict | None:
    try:
        return get_json(f"{GBIF_API}/species/match", {"name": scientific_name})
    except Exception:
        return None


def county_place_id(county: str) -> int | None:
    # iNaturalist place search is used only as a lead generator.
    try:
        data = get_json(
            f"{INAT_API}/places/autocomplete",
            {"q": f"{county} County, Texas", "per_page": 10}
        )
    except Exception:
        return None

    county_cf = county.casefold()
    for place in data.get("results", []):
        name = (place.get("display_name") or place.get("name") or "").casefold()
        if county_cf in name and "texas" in name:
            return place.get("id")
    return None


def county_occurrence_leads(taxon_id: int) -> list[dict]:
    leads = []
    for county in TARGET_COUNTIES:
        pid = county_place_id(county)
        if not pid:
            continue
        try:
            data = get_json(
                f"{INAT_API}/observations",
                {
                    "taxon_id": taxon_id,
                    "place_id": pid,
                    "quality_grade": "research",
                    "captive": "false",
                    "per_page": 1
                }
            )
            total = int(data.get("total_results") or 0)
        except Exception:
            total = 0
        if total:
            leads.append({
                "county": county,
                "inat_place_id": pid,
                "research_grade_observation_count": total,
                "status": "SUPPORTING_OCCURRENCE_LEAD_ONLY"
            })
        time.sleep(0.10)
    return leads


def diagnostic_roles(item: dict) -> list[str]:
    family = (item.get("family") or "").casefold()
    genus = (item.get("genus") or "").casefold()
    if family == "poaceae":
        return [
            "habit / whole plant",
            "inflorescence architecture",
            "spikelet close-up",
            "glumes / lemmas / awns",
            "ligule / collar",
            "leaf sheath / node",
            "leaf blade",
            "fruit / seed if useful",
            "diagnostic look-alike comparison"
        ]
    if genus == "quercus":
        return [
            "habit", "upper leaf", "lower leaf", "twig / bud",
            "bark", "acorn", "cupule", "diagnostic look-alike"
        ]
    if genus == "asclepias":
        return [
            "habit", "leaf arrangement", "umbel", "flower front",
            "corona side", "hood / horn detail", "follicle",
            "diagnostic look-alike"
        ]
    return [
        "habit / whole plant", "leaves / phyllotaxy", "stem / attachment",
        "flower front", "flower side", "reproductive detail",
        "fruit / seed", "diagnostic look-alike comparison"
    ]


def gather_photo_candidates(taxon: dict, max_candidates: int) -> list[dict]:
    taxon_id = taxon["id"]
    data = get_json(
        f"{INAT_API}/observations",
        {
            "taxon_id": taxon_id,
            "place_id": 18,  # Texas; retained as a preference, not range evidence.
            "quality_grade": "research",
            "photos": "true",
            "captive": "false",
            "per_page": 100,
            "order_by": "votes",
            "order": "desc"
        }
    )

    rows = []
    seen_photo_ids = set()
    for obs in data.get("results", []):
        user = obs.get("user") or {}
        creator = user.get("name") or user.get("login") or ""
        observed_on = obs.get("observed_on") or ""
        place_guess = obs.get("place_guess") or ""
        quality = obs.get("quality_grade") or ""
        photos = obs.get("photos") or []

        for photo in photos:
            pid = photo.get("id")
            if not pid or pid in seen_photo_ids:
                continue
            seen_photo_ids.add(pid)

            dims = photo.get("original_dimensions") or {}
            width = int(dims.get("width") or 0)
            height = int(dims.get("height") or 0)
            square = photo.get("url") or ""
            thumb = square.replace("square", "medium")
            direct = square.replace("square", "large")
            license_code = photo.get("license_code") or ""
            attribution = photo.get("attribution") or ""
            if attribution and not creator:
                creator = attribution

            # v1 ranking: favor larger exact-source photos from RG observations.
            score = min(width * height, 20_000_000)
            if quality == "research":
                score += 5_000_000

            rows.append({
                "_score": score,
                "observation_id": obs.get("id"),
                "photo_id": pid,
                "scientific_name": (obs.get("taxon") or {}).get("name") or taxon.get("name") or "",
                "observed_on": observed_on,
                "county_lead": place_guess,
                "creator": creator,
                "license": license_code,
                "source_page": f"https://www.inaturalist.org/observations/{obs.get('id')}",
                "thumbnail_url": thumb,
                "direct_image_url": direct,
                "width": width,
                "height": height,
                "quality_grade": quality,
                "role": "UNASSIGNED — curator must inspect diagnostic structure",
                "notes": "Exact iNaturalist photo candidate; study candidate only until curated."
            })
            if len(rows) >= max_candidates * 3:
                break
        if len(rows) >= max_candidates * 3:
            break

    rows.sort(key=lambda x: x["_score"], reverse=True)
    rows = rows[:max_candidates]
    for i, row in enumerate(rows, start=1):
        row["candidate_rank"] = i
        row.pop("_score", None)
    return rows


def write_photo_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PHOTO_COLUMNS)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in PHOTO_COLUMNS})


def make_contact_sheet(path: Path, rows: list[dict], title: str, limit: int = 24) -> str | None:
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except Exception:
        return None

    chosen = rows[:limit]
    if not chosen:
        return None

    cell_w, cell_h = 260, 240
    image_h = 185
    cols = 4
    rows_n = (len(chosen) + cols - 1) // cols
    header_h = 55
    sheet = Image.new("RGB", (cols * cell_w, header_h + rows_n * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((12, 12), f"{title} — scout photo candidates (NOT CURATED)", fill="black", font=font)
    draw.text((12, 30), "Use photo-candidates.csv for exact provenance and source links.", fill="black", font=font)

    for idx, candidate in enumerate(chosen):
        r, c = divmod(idx, cols)
        x, y = c * cell_w, header_h + r * cell_h
        try:
            raw = get_bytes(candidate["thumbnail_url"])
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            im = ImageOps.contain(im, (cell_w - 12, image_h - 8))
            px = x + (cell_w - im.width) // 2
            py = y + 4 + (image_h - im.height) // 2
            sheet.paste(im, (px, py))
        except Exception:
            draw.rectangle((x + 5, y + 5, x + cell_w - 5, y + image_h - 5), outline="black")
            draw.text((x + 12, y + 80), "image unavailable", fill="black", font=font)

        label = (
            f"#{candidate['candidate_rank']}  obs {candidate['observation_id']}\n"
            f"photo {candidate['photo_id']}  {candidate['width']}x{candidate['height']}\n"
            f"{candidate['license'] or 'license not reported'}"
        )
        draw.multiline_text((x + 8, y + image_h + 4), label, fill="black", font=font, spacing=2)

    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, "JPEG", quality=82, optimize=True)
    return str(path.relative_to(ROOT))


def sources_markdown(item: dict, taxon: dict | None, gbif: dict | None) -> str:
    name = item["scientific_name"]
    inat_id = taxon.get("id") if taxon else None
    gbif_key = None
    if gbif:
        gbif_key = gbif.get("usageKey") or gbif.get("speciesKey")
    lines = [
        f"# Scout sources — {name}",
        "",
        "> Research leads only. These sources do not constitute the project's final taxonomy or native-range decision.",
        "",
        "## Automated public-API leads",
    ]
    if inat_id:
        lines += [
            f"- iNaturalist taxon candidate: https://www.inaturalist.org/taxa/{inat_id}",
            "- iNaturalist observations/photos are supporting occurrence and exact-image leads, not proof of native county range."
        ]
    if gbif_key:
        lines.append(f"- GBIF taxon candidate: https://www.gbif.org/species/{gbif_key}")
    lines += [
        "",
        "## Still required during curation",
        "- Confirm accepted taxonomy/current placement against authoritative botanical sources.",
        "- Apply project range priority: BONAP/NAPA → USDA PLANTS → LBJ/NPSOT → herbarium/flora → occurrence support.",
        "- Record the actual target-zone counties used for PASS/FAIL/UNRESOLVED.",
        "- Inspect every photo candidate and assign it only when it clearly teaches a diagnostic structure.",
        "- Preserve creator/license/source-page metadata for selected exact photographs.",
        ""
    ]
    return "\n".join(lines)


def scout_one(item: dict, default_photo_candidates: int) -> dict:
    taxon_id = item["id"]
    name = item["scientific_name"]
    draft_dir = DRAFTS / taxon_id
    draft_dir.mkdir(parents=True, exist_ok=True)

    errors = []
    taxon = None
    gbif = None
    county_leads = []
    photos = []

    try:
        taxon = exact_inat_taxon(name)
    except Exception as exc:
        errors.append(f"iNaturalist taxon lookup: {exc}")

    try:
        gbif = gbif_match(name)
    except Exception as exc:
        errors.append(f"GBIF taxon lookup: {exc}")

    if taxon and taxon.get("id"):
        try:
            county_leads = county_occurrence_leads(int(taxon["id"]))
        except Exception as exc:
            errors.append(f"county occurrence leads: {exc}")
        try:
            photos = gather_photo_candidates(taxon, default_photo_candidates)
        except Exception as exc:
            errors.append(f"photo candidates: {exc}")

    write_photo_csv(draft_dir / "photo-candidates.csv", photos)
    contact_sheet = make_contact_sheet(
        draft_dir / "contact-sheet.jpg",
        photos,
        name
    )

    draft = {
        "schema_version": 1,
        "draft_status": "SCOUTED_RESEARCH_ONLY",
        "created_at": utc_now(),
        "queue_item": item,
        "guardrail": (
            "This file contains research leads only. Do not install it into canonical content "
            "without human/ChatGPT curation under PROJECT_RULES.md."
        ),
        "taxonomy_candidates": {
            "iNaturalist": taxon,
            "GBIF": gbif
        },
        "target_zone_occurrence_leads": {
            "warning": (
                "These are supporting research-grade iNaturalist occurrence leads only. "
                "They do NOT establish native county range or PASS/FAIL status."
            ),
            "counties_with_leads": county_leads
        },
        "diagnostic_image_roles_needed": diagnostic_roles(item),
        "photo_candidates": {
            "count": len(photos),
            "csv": "photo-candidates.csv",
            "contact_sheet": "contact-sheet.jpg" if contact_sheet else None,
            "selection_status": "UNREVIEWED"
        },
        "curator_checklist": [
            "Confirm accepted taxonomy and important synonyms.",
            "Confirm target-zone native range using project source priority.",
            "Write morphology-first 'Where should I look first?' guidance.",
            "Identify realistic local look-alikes and structural separators.",
            "Inspect photo contact sheet and exact-source CSV.",
            "Select exact diagnostic photos and assign image roles.",
            "Create a normal curation-inbox package only after review."
        ],
        "errors": errors
    }
    write_json(draft_dir / "draft.json", draft)
    (draft_dir / "SOURCES.md").write_text(
        sources_markdown(item, taxon, gbif), encoding="utf-8"
    )

    return {
        "id": taxon_id,
        "scientific_name": name,
        "photo_candidates": len(photos),
        "county_occurrence_leads": len(county_leads),
        "errors": errors
    }


def main() -> int:
    if not QUEUE_PATH.exists():
        raise SystemExit("research-queue.json is missing")

    queue = load_json(QUEUE_PATH)
    settings = queue.get("settings") or {}
    default_max = int(settings.get("max_items_per_run") or 2)
    max_items = int(os.getenv("BOTANY_SCOUT_MAX") or default_max)
    photo_max = int(settings.get("default_photo_candidates") or 36)
    force_id = (os.getenv("BOTANY_SCOUT_FORCE_ID") or "").strip()

    items = queue.get("items") or []
    if force_id:
        selected = [x for x in items if x.get("id") == force_id][:1]
    else:
        selected = [x for x in items if x.get("status") == "queued"]
        selected.sort(key=lambda x: (int(x.get("priority") or 9999), x.get("id") or ""))
        selected = selected[:max_items]

    report = {
        "started_at": utc_now(),
        "selected_count": len(selected),
        "selected_ids": [x.get("id") for x in selected],
        "results": []
    }

    for item in selected:
        result = scout_one(item, photo_max)
        report["results"].append(result)
        if not result["errors"]:
            item["status"] = "scouted"
        else:
            item["status"] = "scouted_with_warnings"
        item["last_scouted_at"] = utc_now()

    queue["last_scout_run_at"] = utc_now()
    write_json(QUEUE_PATH, queue)
    report["finished_at"] = utc_now()
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_json(REPORTS / "last-scout-run.json", report)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

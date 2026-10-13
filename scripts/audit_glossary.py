#!/usr/bin/env python3
"""Structural QA for botanical glossary. Does NOT claim arrows are botanically accurate."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
terms = json.loads((root / "data/learning-layer.json").read_text(encoding="utf-8"))["terms"]
issues = []
annotated = 0
for key, term in terms.items():
    for field in ("term", "plain", "formal", "where", "why"):
        if not str(term.get(field, "")).strip():
            issues.append(f"{key}: missing {field}")
    if not term.get("visual") and not term.get("real_photo"):
        issues.append(f"{key}: no visual")
    photo = term.get("real_photo") or {}
    if photo:
        if not photo.get("alt"):
            issues.append(f"{key}: missing accessible image description")
        if not photo.get("credit"):
            issues.append(f"{key}: missing image credit")
        if not (photo.get("image_url") or photo.get("source_page")):
            issues.append(f"{key}: missing image reference")
        arrows = photo.get("annotations") or []
        if arrows:
            annotated += 1
        for n, arrow in enumerate(arrows, 1):
            if not str(arrow.get("label", "")).strip():
                issues.append(f"{key} arrow {n}: empty label")
            for coord in ("x", "y", "label_x", "label_y"):
                try:
                    value = float(arrow[coord])
                    if not 0 <= value <= 100:
                        raise ValueError()
                except (ValueError, TypeError, KeyError):
                    issues.append(f"{key} arrow {n}: invalid {coord}")
print(f"Glossary: {len(terms)} terms, {annotated} with coordinate overlays, {len(issues)} structural issues")
print("NOTE: Structural validation cannot confirm arrow targets or photographic accuracy.")
for issue in issues:
    print("FAIL:", issue)
raise SystemExit(bool(issues))

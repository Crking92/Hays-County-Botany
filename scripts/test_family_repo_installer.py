#!/usr/bin/env python3
"""Read-only deterministic smoke tests of the approved family installer."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/family_repo_installer.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *[str(x) for x in args]],
        cwd=ROOT, capture_output=True, text=True,
    )


def make_card(taxa, family, genus, slug):
    target = taxa / family / genus / slug
    target.mkdir(parents=True, exist_ok=True)
    (target / "species.json").write_text(json.dumps({
        "id": slug, "family": family, "genus": genus,
        "species": slug.split("-")[-1],
        "scientific_name": genus + " " + slug.split("-")[-1],
        "common_name": "Test",
        "images": [],
    }))
    (target / "SOURCES.txt").write_text("TEST FIXTURE; do not publish.\n")


def main():
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        taxa = base / "taxa"
        make_card(taxa, "Fabaceae", "Senegalia", "senegalia-testus")
        make_card(taxa, "Lamiaceae", "Salvia", "salvia-testus")
        (taxa / "Lamiaceae" / "family.json").write_text('{"family":"Lamiaceae"}\n')
        p = run(base)
        assert p.returncode == 0, p.stderr
        result = json.loads(p.stdout)
        assert result["legacy_hub_botanical_writes"] is False
        assert result["photo_downloads"] == 0
        routes = {x["id"]: (x["repository"], x["branch"]) for x in result["items"]}
        assert routes["senegalia-testus"] == ("Crking92/Hays-Botany-Fabaceae", "staging/fabaceae-metadata")
        assert routes["salvia-testus"] == ("Crking92/Hays-Botany-Lamiales", "staging/original-source-transfer")
        assert len(result["lessons"]) == 1
        assert result["lessons"][0]["repository"] == "Crking92/Hays-Botany-Lamiales"
        # Even --apply cannot write into an absent local collection clone.
        blocked = run(base, "--apply", "--destination-root", base)
        assert blocked.returncode != 0 and "must be cloned" in blocked.stderr, blocked.stderr
        # Unknown botanical family fails closed; no default to original hub.
        make_card(taxa, "Imaginaryaceae", "Imaginarus", "imaginarus-testus")
        unknown = run(base)
        assert unknown.returncode != 0 and "NO legacy hub fallback" in unknown.stderr, unknown.stderr
        # Adding media to an unreviewed install is also fail-closed.
        (taxa / "Imaginaryaceae" / "Imaginarus" / "imaginarus-testus" / "species.json").unlink()
        (taxa / "Fabaceae" / "Senegalia" / "senegalia-testus" / "images").mkdir()
        (taxa / "Fabaceae" / "Senegalia" / "senegalia-testus" / "images" / "x.jpg").write_bytes(b"unverified")
        media = run(base)
        assert media.returncode != 0 and "individual family photo review" in media.stderr, media.stderr
    print("PASS: family-only routes, lessons, no old hub fallback, no unverified media, no incidental file writes.")


if __name__ == "__main__":
    main()

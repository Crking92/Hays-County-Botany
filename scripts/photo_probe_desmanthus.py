#!/usr/bin/env python3
"""One-off bounded audit of licensed photo candidates for two zero-photo Desmanthus taxa."""
import json
import urllib.parse
import urllib.request
import time
from pathlib import Path

USER_AGENT = "HaysBotanyLearnerPhotoAudit/1.0 (educational plant photo provenance audit)"
TARGETS = ["Desmanthus acuminatus", "Desmanthus leptolobus"]
LICENSES = {"cc-by", "cc-by-nc", "cc-by-sa", "cc-by-nc-sa", "cc0", "pd"}
OUTPUT = Path("research-drafts/desmanthus-photo-probe-20261013.json")

def get_json(host, path, params):
    url = host + path + "?" + urllib.parse.urlencode(params)
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=17) as stream:
                return json.load(stream)
        except Exception as exc:
            if i == 2:
                return {"error": str(exc), "url":url}
            time.sleep(1.2*(i+1))

out = {"targets":{}, "note":"PROBE ONLY. No photograph is installed, no taxonomic range claim. Verify photo-specific license and species before using."}
for name in TARGETS:
    q = get_json("https://api.inaturalist.org", "/v1/observations", {
        "taxon_name":name, "photos":"true", "quality_grade":"research", "per_page":"80",
        "order_by":"observed_on", "order":"desc"
    })
    records = []
    for o in q.get("results", []):
        tn = (o.get("taxon") or {}).get("name")
        if tn != name:
            continue
        for p in o.get("photos", []):
            li = (p.get("license_code") or "").lower()
            if li not in LICENSES:
                continue
            original = p.get("url") or ""
            base_url = original.replace("/square.", "/large.").replace("/small.", "/large.").replace("/medium.", "/large.").replace("/thumb.", "/large.")
            records.append({"observation":o.get("id"),"photo_id":p.get("id"),"license":li,
                "attribution":p.get("attribution"),"image_url":base_url,
                "source_page":"https://www.inaturalist.org/photos/"+str(p.get("id")),
                "taxon":tn,"place":o.get("place_guess"),"observed_on":o.get("observed_on")})
    category = "Category:"+name.replace(" ","_")
    cm = get_json("https://commons.wikimedia.org", "/w/api.php", {
        "action":"query","list":"categorymembers","cmtitle":category,"cmtype":"file","cmlimit":"30","format":"json"
    })
    titles = [a.get("title") for a in cm.get("query",{}).get("categorymembers",[]) if a.get("title")]
    out["targets"][name] = {"inat_results":q.get("total_results"),"inat_error":q.get("error"),
        "approved_media":records[:35],"commons_file_titles":titles,"commons_error":cm.get("error")}
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(out, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
print("wrote",OUTPUT, "photo counts", {n:len(v["approved_media"]) for n,v in out["targets"].items()})

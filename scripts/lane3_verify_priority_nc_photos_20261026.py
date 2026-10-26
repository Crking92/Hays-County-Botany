#!/usr/bin/env python3
"""Exact per-image CC BY-NC evidence audit; no files/cards/photos modified."""
import json,urllib.request,urllib.error,pathlib,re,datetime
REPORT=pathlib.Path("reports/lane3-priority-nc-photo-license-confirm-20261026.json")
targets=[
 {"taxon":"Muhlenbergia reverchonii","creator":"Matt (drbh2o)","photo_id":58493566,"observation_id":36950498,"expected":"cc-by-nc"},
 {"taxon":"Tridentopsis mutica","creator":"Joey Santore","photo_id":667323408,"observation_id":365501324,"expected":"cc-by-nc"},
 {"taxon":"Tridentopsis mutica","creator":"Joey Santore","photo_id":667323452,"observation_id":365501324,"expected":"cc-by-nc"},
 {"taxon":"Tridentopsis buckleyana","creator":"jamiemandell","photo_id":380287142,"gbif_occurrence_id":4891719982,"expected":"cc-by-nc"},
]
def getjson(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyRightsAudit/1.0 (open scientific/educational photo metadata only; github.com/Crking92/Hays-County-Botany)","Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=24) as res:
  assert "json" in res.headers.get("Content-Type","")
  data=res.read(3000001)
 assert len(data)<3000001
 return json.loads(data)
memo={
"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"policy":"workflow/PUBLIC_PHOTO_REUSE_POLICY_20261019.md",
"site":"https://crking92.github.io/Hays-County-Botany/",
"scope":"4 original CC BY-NC photos in 3 priority species; no new photo copying or license alteration",
"permissions":"CC BY-NC may be used on truly noncommercial public educational Pages with original creator, exact image-level license, source, changes, review if site ever gains ads/affiliate/commercial use.",
"results":[]
}
cache={}
for row in targets:
 e=dict(row,license_source="ORIGINAL_STORED_CANONICAL_IMAGE_RECORD",status="ORIGINAL_METADATA_RECORDED__LIVE_RECHECK_HOLD")
 e["source_photo_page"]=f"https://www.inaturalist.org/photos/{row['photo_id']}"
 if "observation_id" in row:
  url=f"https://api.inaturalist.org/v1/observations/{row['observation_id']}"
  try:
   if url not in cache: cache[url]=getjson(url)
   data=cache[url]
   obs=(data.get("results") or [])[0]
   photo=next((p for p in obs.get("photos",[]) if int(p.get("id",0))==row["photo_id"]),None)
   if not photo:raise ValueError("Exact photo ID absent on observation")
   lic=str(photo.get("license_code") or "").lower()
   attrib=str(photo.get("attribution") or "")
   e.update(observed_license_code=lic,source_attribution=attrib,original_url=photo.get("url"),
            observation_taxon=(obs.get("taxon") or {}).get("name"))
   if lic!=row["expected"]:raise ValueError("Original photo license changed or mismatched; retain hold")
   if row["creator"]=="Joey Santore" and "Joey Santore" not in attrib:raise ValueError("Photographer mismatch")
   if row["creator"]=="Matt (drbh2o)" and "Matt" not in attrib and "drbh2o" not in attrib:raise ValueError("Photographer attribution mismatch")
   e["status"]="LIVE_PHOTO_LEVEL_CC_BY_NC_CONFIRMED" 
  except Exception as exc:e["live_error"]=str(exc)[:220]
 else:
  url=f"https://api.gbif.org/v1/occurrence/{row['gbif_occurrence_id']}"
  try:
   raw=getjson(url)
   media=[m for m in (raw.get("media") or []) if str(row["photo_id"]) in str(m.get("identifier",""))]
   if not media:raise ValueError("Exact photo ID absent in GBIF occurrence media")
   lic=" ".join(str(m.get("license","")) for m in media)
   e.update(media_license_links=lic,record_taxon=raw.get("scientificName"),
            media_creator=[m.get("rightsHolder") or m.get("creator") for m in media])
   if not ("/by-nc/" in lic.lower() or "by-nc" in lic.lower()):raise ValueError("Exact photo license not demonstrably CC BY-NC")
   e["status"]="LIVE_PHOTO_LEVEL_CC_BY_NC_CONFIRMED"
  except Exception as exc:e["live_error"]=str(exc)[:220]
 e["rights_decision"]="CONDITIONALLY_SITE_ELIGIBLE_ONLY_WHILE_GENUINELY_NONCOMMERCIAL_WITH_CREDIT_AND_SOURCE" if e["status"]=="LIVE_PHOTO_LEVEL_CC_BY_NC_CONFIRMED" else "PRESERVE_ORIGINAL_CREDITED_JPEG_AND_SOURCE; NO AUTOMATIC_HOLD_CLEARING"
 memo["results"].append(e)
memo["verified_live"]=sum(x["status"]=="LIVE_PHOTO_LEVEL_CC_BY_NC_CONFIRMED" for x in memo["results"])
memo["live_unresolved"]=len(memo["results"])-memo["verified_live"]
memo["site_policy_caveat"]="Original project source photos remain in a public Github repository; current educational, NC site intent does not permit commercial redistribution. Existing public_site_hold and scientific ID caveats are separate fields and are not changed by this read-only audit."
REPORT.write_text(json.dumps(memo,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(memo,indent=2))

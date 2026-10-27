#!/usr/bin/env python3
"""Archive 3 CC BY, research-grade, exact TX silver bluestem anatomy photographs.

This upgrades REAL anatomical views but does not label a ruler that isn't present.
The pale inner collar membrane still lacks a calibrated 1 mm scale. No score
inflation; no false attached sessile/pedicelled pair claim.
"""
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Bothriochloa/bothriochloa-torreyana"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/silver-milam-original-anatomy-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-silver-milam-anatomy-verified.json"
OBS=355847446
SOURCE=[
 {"id":648930178,"file":"silver-milam-linda-jo-conn-open-inner-collar-648930178.jpg",
  "label":"TEXAS SILVER — actual opened inner collar and pale transverse lip",
  "role":"Original field photo of opened inner leaf blade-sheath junction, visible short pale transverse rim; no mm ruler",
  "caption":"Linda Jo Conn, Milam County, Texas, April 27, 2026. The leaf sheath is gently opened and a genuine short pale transverse rim can be seen on the inside at the blade junction. This is a real possible membranous ligule feature in the identified plant, but NO 1-mm ruler is visible; do not teach its exact length or microscopic margin from this photo.",
  "why":"Genuinely photographed INSIDE of a connected Texas silver bluestem collar, unlike earlier external leaf-sheath photos.",
  "markers":[{"label":"Pale inner collar rim — unmeasured","label_x":55,"label_y":27,"target_x":52,"target_y":38}]},
 {"id":648929751,"file":"silver-milam-linda-jo-conn-colored-true-node-648929751.jpg",
  "label":"TEXAS SILVER — actual exposed culm node and leaf blade",
  "role":"Real stem node in closeup on same source-identified silver bluestem, with purple-brown band but no mm ruler",
  "caption":"Linda Jo Conn, Milam County, Texas, April 27, 2026. The pale culm on the right has a distinctly darker purple-brown transverse node between elongated internodes; an adjacent green leaf blade is visible on the left. A real stem node is NOT the seam where a blade joins a sheath. This real field photograph has no calibrated millimeter scale and does not prove nodes must always be purple or hairless.",
  "why":"Visible context separates a TRUE culm node from the blade-sheath collar and shows natural node color variation.",
  "markers":[{"label":"True transverse culm node","label_x":15,"label_y":67,"target_x":65,"target_y":60}]},
 {"id":648930211,"file":"silver-milam-linda-jo-conn-outer-blade-sheath-junction-648930211.jpg",
  "label":"TEXAS SILVER — outer blade and wrapping sheath (compare inner rim)",
  "role":"External leaf blade-sheath junction, visible sheath margins and blade, no claim of ligule inside",
  "caption":"Linda Jo Conn, Milam County, Texas, April 27, 2026. Actual outer blade–sheath junction of a documented silver bluestem, shown as an orientation photo beside the opened inner view. The tiny hidden membranous ligule is NOT exposed in this outside-facing image.",
  "why":"Teaches crew the exact difference between the visible OUTER collar and the opened INSIDE membrane; avoid pointing to a sheath as a ligule.",
  "markers":[{"label":"Outer blade–sheath junction","label_x":56,"label_y":37,"target_x":40,"target_y":52}]}
]
def main():
    d=json.loads(CARD.read_text(encoding="utf-8"))
    assert d["id"]=="bothriochloa-torreyana" and d["native_target_zone_calculated"] is False
    assert d["silver_six_role_photo_score_20261027"]["total"]==4.5
    s=requests.Session();s.headers['User-Agent']='HaysBotanyVisualLearner/1.0 Milam photo original licensed archiver'
    resp=s.get(f'https://api.inaturalist.org/v1/observations/{OBS}',timeout=45)
    resp.raise_for_status();o=resp.json()['results'][0]
    assert o['id']==OBS and o.get('quality_grade')=='research' and o['taxon']['id']==1452295
    assert o.get('user',{}).get('login')=='connlindajo' and 'TX' in str(o.get('place_guess'))
    entries=[]
    for spec in SOURCE:
      try:
        p=next(x for x in o['photos'] if x['id']==spec['id'])
        assert p.get('license_code')=='cc-by'
        assert 'Linda Jo Conn' in str(p.get('attribution'))
        url=p['url'].replace('/square.','/large.').replace('/medium.','/large.')
        raw=s.get(url,timeout=40);raw.raise_for_status()
        assert len(raw.content)<10_000_000 and len(raw.content)>30000
        with Image.open(io.BytesIO(raw.content)) as img:
          im=ImageOps.exif_transpose(img).convert('RGB');im.load()
        assert min(im.size)>=768 and max(im.size)<=3000
        dest=ROOT/REL/'images'/spec['file'];dest.parent.mkdir(parents=True,exist_ok=True)
        im.save(dest,'JPEG',quality=91,subsampling=0,optimize=True)
        with Image.open(dest) as ck:
          assert not ck.getexif() and ck.size==im.size
          ck.verify()
        digest=hashlib.sha256(dest.read_bytes()).hexdigest()
        urlpage=f'https://www.inaturalist.org/photos/{spec["id"]}'
        rel='images/'+spec['file']
        lic='CC BY 4.0 (individual iNaturalist photo cc-by; retain source credit)'
        record={'file':rel,'role':spec['role'],'creator':'Linda Jo Conn','license':lic,
          'license_url':'https://creativecommons.org/licenses/by/4.0/','source_page':urlpage,
          'source_photo_id':spec['id'],'source_observation_id':OBS,
          'source_locality':o.get('place_guess'),'observed_on':o.get('observed_on'),
          'public_reuse':'yes, exact CC BY photo with author, source, license and modifications credited',
          'study_use':'yes','archive_sha256':digest,'image_dimensions':list(im.size),
          'photo_status':'PHYSICALLY ARCHIVED, source species research grade. Actual visibly arrowed anatomy only; no 1 mm measurement established.',
          'modifications':'JPEG re-encoded without EXIF/GPS; learner arrows are separate overlay and source original not misrepresented'}
        panel={'label':spec['label'],'scientific_name':'Bothriochloa torreyana',
          'image_url':REL+'/'+rel,'image_fit':'contain','image_role':spec['role'],
          'caption':spec['caption'],'why_it_matters':spec['why'],
          'creator':'Linda Jo Conn','license':lic,'license_url':'https://creativecommons.org/licenses/by/4.0/',
          'source_page':urlpage,'source_photo_id':spec['id'],'markers':spec['markers'],
          'photo_status':'Source species-identified real Texas anatomy; no mm ruler, no guessed microanatomy.'}
        if not any(x.get('source_photo_id')==spec['id'] for x in d['images']):d['images'].append(record)
        if not any(x.get('source_photo_id')==spec['id'] for x in d['visual_comparison']['items']):d['visual_comparison']['items'].append(panel)
        entries.append({'photo_id':spec['id'],'status':'ARCHIVED','file':str(dest.relative_to(ROOT)),
          'dimensions':list(im.size),'sha256':digest,'markers':len(spec['markers'])})
      except Exception as e:
        entries.append({'photo_id':spec['id'],'status':'HOLD','reason':str(e)[:250]})
    installed=[x for x in entries if x['status']=='ARCHIVED']
    report={'taxon':'Bothriochloa torreyana','observation':OBS,'taxon_grade':'research',
      'photos':entries,'rights':'each exact source CC BY','score_before':4.5,'score_after':4.5,
      'note':'Open inner collar and node anatomy improved, but neither is mm-calibrated; measured complete pair absent.'}
    REPORT.parent.mkdir(exist_ok=True,parents=True)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    if installed:
      d['curation_status']['photo_metadata_count']=len(d['images'])
      d['curation_status']['photo_files_present']=len(d['images'])
      d['curation_status']['visual_finish']='FIELD_READY_PHOTO_GAPS — real Texas opened inner collar and true culm node archived; neither has 1 mm calibration. Calibrated sessile/pedicelled pair missing.'
      d['silver_milam_ccby_field_anatomy_20261027']={'source_obs':OBS,'source_locality':o.get('place_guess'),
        'photo_ids':[x['photo_id'] for x in installed],'new_real_anatomy_arrows':sum(x['markers'] for x in installed),
        'no_mm_ruler':True,'confirmed_six_role_score':4.5,'status':'FIELD_READY_PHOTO_GAPS'}
      d['visual_comparison']['subtitle']='Actual Texas photographed heads, exposed culm nodes, opened inner collar, attached roots and silvery reproductive hairs. New Milam anatomy shows the unmeasured inside rim and actual node. A photographed 1-mm-calibrated free ligule and an intact measured sessile/pedicelled spikelet pair are still missing.'
      d['photo_note']='Source-verified real silver bluestem anatomy includes CC BY Milam County inner collar, true stem node and external leaf-sheath junction. No photographs here establish precise ligule length or intact scaled paired-spikelet anatomy; see individual captions.'
      CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
      MARKER.parent.mkdir(parents=True,exist_ok=True)
      MARKER.write_text(json.dumps({'taxon':'Bothriochloa torreyana','stage':'FIELD_READY_PHOTO_GAPS',
        'installed_photo_ids':[x['photo_id'] for x in installed],
        'measured_photo_roles_completed':False,'six_role_pct':75,
        'photo_rights':'individual CC BY with creator and license preserved'},indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert len(installed)==len(SOURCE),'one or more source originals held, preserve exact reason'
if __name__=='__main__': main()

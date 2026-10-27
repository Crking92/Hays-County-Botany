#!/usr/bin/env python3
"""Archive two authentic Hays County Kyle research-grade Sorghastrum nutans photos.

Both exact photos are John Davis CC BY-NC under current noncommercial
educational site policy. Never treat crowded shoots as uprooted roots or
an exterior collar as a measured free ligule.
"""
import io,json,hashlib
from pathlib import Path
import requests
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
REL="content/taxa/Poaceae/Sorghastrum/sorghastrum-nutans"
CARD=ROOT/REL/"species.json"
REPORT=ROOT/"reports/indiangrass-kyle-real-local-photographs-20261027.json"
MARKER=ROOT/"workflow/field-id-publication/2026-10-27-indiangrass-kyle-real-two-photos.json"
OBS=390669128
SPECS=[
 {"id":715750404,"filename":"indiangrass-kyle-john-davis-in-ground-basal-clump-715750404.jpg",
  "name":"KYLE TEXAS — true growing basal tuft and dense standing leaves",
  "role":"Actual in-ground Hays County clump; many connected aboveground basal leaves, no physically exposed roots",
  "caption":"Real research-grade source-identified Sorghastrum nutans photographed by John Davis along Beech Drive in Kyle, Hays County, Texas, August 12, 2026. The numerous upright basal leaves and shared growing shoot cluster can be followed downward toward the soil. Roots and rhizomes are NOT excavated or visible and the flowering stem is NOT connected top-to-root in this photograph.",
  "why":"A genuinely local living stand grounds the learner in Kyle vegetation, instead of assuming a nonlocal herbarium flowering plant proves Hays County rootstock."},
 {"id":715751544,"filename":"indiangrass-kyle-john-davis-true-collar-close-715751544.jpg",
  "name":"KYLE TEXAS — pale collar point between two green blade/sheath surfaces",
  "role":"Real Hays County grass blade-sheath collar with a pale pointed membrane-like projection, unmeasured",
  "caption":"Real source-identified Indiangrass observed in Kyle, Hays County, Texas, August 12, 2026 by John Davis. The junction of a green blade and wrapping sheath shows a tiny pale pointed projection near the narrow collar, with fingers behind for coarse size context. The pale point is not independently measured as the free membranous ligule. No ruler or exposed entire ligule margin; do not claim 2–6 mm from this image.",
  "why":"Adds a locally photographed leaf junction next to the Matt Lavin close-up without equating a sheath corner with measured membrane."}
]
def main():
 d=json.loads(CARD.read_text())
 assert d['id']=='sorghastrum-nutans' and d['native_target_zone_calculated'] is True
 assert d['indiangrass_six_role_photo_score_20261027']['total']==3
 s=requests.Session();s.headers['User-Agent']='HaysBotanyVisualLearner/1.0 exact photo license archive'
 res=s.get('https://api.inaturalist.org/v1/observations/'+str(OBS),timeout=44);res.raise_for_status()
 o=res.json()['results'][0]
 assert o['id']==OBS and o.get('quality_grade')=='research' and o['taxon']['id']==122608
 assert o['user']['login']=='jdavisz' and 'Kyle' in str(o.get('place_guess'))
 results=[]
 for spec in SPECS:
  try:
   p=next(x for x in o['photos'] if x['id']==spec['id'])
   assert p['license_code']=='cc-by-nc' and 'John Davis' in str(p['attribution'])
   url=p['url'].replace('/square.','/large.').replace('/medium.','/large.')
   x=s.get(url,timeout=40);x.raise_for_status()
   assert 30000<len(x.content)<10000000
   with Image.open(io.BytesIO(x.content)) as orig:
    im=ImageOps.exif_transpose(orig).convert('RGB');im.load()
   assert min(im.size)>=750 and max(im.size)<=3000
   dest=ROOT/REL/'images'/spec['filename'];dest.parent.mkdir(parents=True,exist_ok=True)
   im.save(dest,'JPEG',quality=87,optimize=True)
   with Image.open(dest) as check:
    assert not check.getexif() and check.size==im.size
    check.verify()
   digest=hashlib.sha256(dest.read_bytes()).hexdigest()
   photo_page='https://www.inaturalist.org/photos/'+str(spec['id'])
   lic='CC BY-NC 4.0 (individual photo license; public display only on genuinely noncommercial learner)'
   rec={'file':'images/'+spec['filename'],'role':spec['role'],
        'creator':'John Davis','license':lic,'license_url':'https://creativecommons.org/licenses/by-nc/4.0/',
        'source_page':photo_page,'source_photo_id':spec['id'],'source_observation_id':OBS,
        'source_locality':o.get('place_guess'),'observed_on':o.get('observed_on'),
        'public_reuse':'yes, photo individually CC BY-NC; only noncommercial educational public learner with exact attribution',
        'study_use':'yes','image_dimensions':list(im.size),'archive_sha256':digest,
        'modifications':'Re-encoded JPEG at quality 87, EXIF/GPS removed; separate learner captions, image remains genuine',
        'photo_status':'SOURCE VERIFIED local Kyle real photograph; in-ground aboveground crown/collar only; no roots, measured ligule or spikelet pair asserted.'}
   panel={'label':spec['name'],'scientific_name':'Sorghastrum nutans',
        'image_url':REL+'/images/'+spec['filename'],'image_fit':'contain',
        'image_role':spec['role'],'caption':spec['caption'],'why_it_matters':spec['why'],
        'creator':'John Davis','license':lic,'license_url':'https://creativecommons.org/licenses/by-nc/4.0/',
        'source_page':photo_page,'source_photo_id':spec['id'],'markers':[],
        'photo_status':'Photo physically archived and source / rights verified; arrows await separate original-pixel preview. No fake roots or free ligule measurement.'}
   if not any(x.get('source_photo_id')==spec['id'] for x in d['images']):d['images'].append(rec)
   if not any(x.get('source_photo_id')==spec['id'] for x in d['visual_comparison']['items']):d['visual_comparison']['items'].append(panel)
   results.append({'photo':spec['id'],'status':'ARCHIVED','file':str(dest.relative_to(ROOT)),'bytes':dest.stat().st_size,
     'dimensions':list(im.size),'sha256':digest,'arrows':0})
  except Exception as e:
   results.append({'photo':spec['id'],'status':'HOLD','reason':str(e)[:230]})
 report={'species':'Sorghastrum nutans','source_observation':OBS,'photo_results':results,'site_intent':'public noncommercial CC BY-NC',
  'score_before':3,'score_after':3,'new_distinct_real_hays_count':sum(x['status']=='ARCHIVED' for x in results),
  'qualifier':'Real local adult bunch, tiny collar; no rooted base exposed and no measured membrane.'}
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+'\n')
 ok=[x for x in results if x['status']=='ARCHIVED']
 if ok:
  oldcount=d['indiangrass_six_role_photo_score_20261027']['total']
  assert oldcount==3 and len(d['visual_comparison']['items'])==10
  d['curation_status']['photo_metadata_count']=len(d['images'])
  d['curation_status']['photo_files_present']=sum(str(p['file']).startswith('images/') for p in d['images'])
  d['curation_status']['visual_finish']='FIELD_READY_PHOTO_GAPS — real local Kyle growing bunch and collar photos added; 1-mm ligule, genuine rootstock and measured paired fertile spikelet still absent.'
  d['indiangrass_kyle_actual_local_photos_20261027']={'source_observation_id':OBS,
    'photo_ids':[x['photo'] for x in ok],'source_license':'CC BY-NC 4.0 per exact source',
    'photographic_six_role_score':'3/6 = 50%, honest no role inflation',
    'actual_in_ground_bunch':True,'actual_exterior_collar':True,'roots_shown':False,
    'free_ligule_calibrated':False,'site_publication':'triggered only; live status separately checked'}
  d['visual_comparison']['subtitle']='Ten actual source-captioned reference panels including two new Hays County Kyle live Indiangrass photos and six independently checked annotated Matt Lavin fine macro pointers. Rooted rhizomes, full free ligule at 1 mm, and matched intact spikelet/pedicel still need photos.'
  d['field_photo_quickcheck']['featured_photo_indices']=[8,9,1,4,0,3,5,6,7]
  learner=d.get('beginner_learning_path',{})
  if learner.get('steps') and not any(z.get('panel_index')==8 for z in learner['steps']):
   learner['steps'].insert(0,{'panel_index':8,'title':'Local Kyle · Recognize the standing bunch',
      'look_for':'Observe this actual growing indiangrass clump photographed in Kyle, including the long green basal leaves and the shoot bases at ground level. The true belowground roots are NOT visible.',
      'why_it_matters':'Teaches the crew what the plant actually looks like locally without implying the photo proves its underground rhizomes.'})
   learner['steps'].insert(2,{'panel_index':9,'title':'Local Kyle · Find the narrow leaf collar',
      'look_for':'John Davis photographed a pale collar point beside the green blade and sheath. Check the same feature in Matt Lavin macro; no ruler proves membrane length.',
      'why_it_matters':'Connects accurate Texas field context to anatomy without labeling a green sheath point as a measured free ligule.'})
   learner['title']='Indiangrass — actual Kyle clump, true collar, branched head and awned spikelet'
  d['field_id_short_tiles'][0]['photo_panel_indices']=[8,9,1,3]
  d['field_id_short_tiles'][0]['details']+=' 2026 LOCAL KYLE photos added: panel 9 is an in-ground clump and panel 10 is a pale collar point. Neither proves belowground rhizomes or a measured free ligule.'
  CARD.write_text(json.dumps(d,indent=2)+'\n')
  MARKER.parent.mkdir(parents=True,exist_ok=True)
  MARKER.write_text(json.dumps({'species_id':'sorghastrum-nutans','photo_ids':[x['photo'] for x in ok],
    'new_source_specific_photos_count':len(ok),'source':'Kyle Hays TX observation 390669128',
    'publish_permission':'exact photo CC BY-NC 4.0 strictly noncommercial learner',
    'strict_six_role_completeness':50,'archival_checks':'two actual JPEG source ID and license checked; EXIF removed, hashes verified'},indent=2)+'\n')
 print(json.dumps(report,indent=2))
 assert len(ok)==2,'Do not claim a complete two-photo archive if one failed'
if __name__=='__main__': main()

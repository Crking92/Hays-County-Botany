#!/usr/bin/env python3
"""Install only five independently image-inspected CC BY 4.0 Dichondra carolinensis teaching views.
The exact-source original is linked on Wikimedia Commons with individual CC BY 4.0 label.
One legacy Douglas Goldman photo remains untouched, as do all range/nativity decisions.
"""
import csv,hashlib,io,json,math
from pathlib import Path
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont

SID='dichondra-carolinensis'
P=Path('content/taxa/Convolvulaceae/Dichondra/dichondra-carolinensis')
FILE=P/'species.json'
REVIEW=Path('workflow/photo-library/reviews/dichondra-carolinensis-20261019/candidate-metadata.json')
LICENSE='https://creativecommons.org/licenses/by/4.0/'
SOURCE=[
 {'id':'363579431','filename':'alex-363579431-patch.jpg',
  'role':'Recognize it · small patches of creeping Carolina ponyfoot with alternately placed kidney-shaped leaves among woodland litter; root attachments are not fully visible.',
  'arrows':[]},
 {'id':'363579498','filename':'alex-363579498-leaf-flower-arrows.jpg',
  'role':'Look closer · verified kidney-shaped entire leaf and tiny 5-lobed cream corolla in the same frame, anatomically marked with arrows.',
  'arrows':[('Kidney-shaped leaf',(0.26,0.57),(0.03,0.84)),('Five-lobed corolla',(0.59,0.50),(0.54,0.05))]},
 {'id':'258349465','filename':'alex-258349465-flower-face-arrows.jpg',
  'role':'Look closer · five cream corolla lobes and five separate green hairy calyx sepals from the face; arrow marks pale corolla, not calyx.',
  'arrows':[('5 corolla lobes',(0.48,0.48),(0.05,0.07))]},
 {'id':'363579587','filename':'alex-363579587-developing-fruit-arrows.jpg',
  'role':'Confirm clue · developing round hairy capsule lobes with green persistent sepals; arrows mark capsule and sepal, NOT an independently measured fruiting pedicel.',
  'arrows':[('Developing fruit',(0.49,0.40),(0.04,0.06)),('Persistent sepal',(0.53,0.70),(0.62,0.84))]},
 {'id':'363579722','filename':'alex-363579722-fruit-group.jpg',
  'role':'Confirm clue · multiple developing hairy capsules with expanded persistent green sepals; two-lobed structure and curved stalks not independently established.',
  'arrows':[]},
]
def get_font(size):
 for font in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
  try:return ImageFont.truetype(font,size)
  except OSError:pass
 return ImageFont.load_default()
def label(im,arrows):
 if not arrows:return im
 w,h=im.size
 d=ImageDraw.Draw(im)
 font=get_font(max(17,round(w*.018)))
 for word,target,position in arrows:
  tx,ty=round(target[0]*w),round(target[1]*h)
  x,y=round(position[0]*w),round(position[1]*h)
  bb=d.textbbox((x,y),word,font=font,stroke_width=0)
  pad=max(5,round(w*.006))
  box=(x-pad,y-pad,bb[2]+pad,bb[3]+pad)
  d.rounded_rectangle(box,radius=7,fill='#0e2725',outline='#fffbe9',width=2)
  d.text((x,y),word,font=font,fill='#ffffff')
  sx=max(box[0],min(box[2],tx))
  sy=box[3] if ty>box[3] else box[1]
  d.line([(sx,sy),(tx,ty)],fill='#101615',width=7)
  d.line([(sx,sy),(tx,ty)],fill='#ffdb4d',width=3)
  a=math.atan2(ty-sy,tx-sx);length=max(12,round(w*.015))
  d.polygon([(tx,ty),(tx-length*math.cos(a-.42),ty-length*math.sin(a-.42)),(tx-length*math.cos(a+.42),ty-length*math.sin(a+.42))],fill='#ffdb4d')
 return im
def get(item):
 pid=item['id']
 for variant in ('original','large'):
  url=f'https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/{variant}.jpg'
  try:
   req=requests.get(url,timeout=40,headers={'User-Agent':'HaysBotanyEducationalPhotoCuration/1.0 (github.com/Crking92/Hays-County-Botany)'})
   req.raise_for_status()
   if not (30000 < len(req.content) < 15000000):continue
   with Image.open(io.BytesIO(req.content)) as base:
    if base.format!='JPEG':continue
    im=ImageOps.exif_transpose(base).convert('RGB')
   if min(im.size)<600:continue
   rawhash=hashlib.sha256(req.content).hexdigest()
   im.thumbnail((1400,1400),Image.Resampling.LANCZOS)
   im=label(im,item['arrows'])
   out=io.BytesIO();im.save(out,format='JPEG',quality=90,optimize=True,progressive=True)
   if len(out.getvalue())<35000:continue
   with Image.open(io.BytesIO(out.getvalue())) as q:q.verify()
   return out.getvalue(),rawhash,list(im.size),url
  except Exception as e:
   print('attempt failed',pid,variant,type(e).__name__,str(e)[:150])
 raise RuntimeError('No full-res licensed source downloaded for '+pid)
def main():
 man=json.loads(Path('data/manifest.json').read_text())
 assert {r['id']:r['path'] for r in man['species']}.get(SID)==str(FILE)
 claims=json.loads(Path('workflow/work-claims.json').read_text()).get('claims',[])
 for claim in claims:
  if SID in (claim.get('taxa') or []) and claim.get('status') in ('active','claimed','in_progress'):
   raise RuntimeError('Active claim collision on Dichondra species')
 r=json.loads(REVIEW.read_text())
 candidates={x['photo_id']:x for x in r['candidate_files']}
 assert all(candidates[i['id']]['status']=='PHOTO_DOWNLOADED' and candidates[i['id']]['creator']=='Alex Abair' and candidates[i['id']]['license_metadata']=='CC BY 4.0' for i in SOURCE)
 card=json.loads(FILE.read_text())
 assert card['id']==SID and card['scientific_name']=='Dichondra carolinensis'
 images=card['images']
 existing={e['file'] for e in images}
 if all('images/'+a['filename'] in existing for a in SOURCE):
  print('already installed five; no changes');return
 assert len(images)==1, 'refuse overwrite of concurrently upgraded gallery'
 assert card['curation_status'].get('finished_field_id_pass')=='PASS_IN_PROGRESS'
 imgs=[]
 for item in SOURCE:
  dest=P/'images'/item['filename']
  assert not dest.exists()
  imgs.append((item,*get(item)))
 # Only after all downloads/decodes succeeded, install full selected set.
 for item,data,rawhash,dims,url in imgs:
  dest=P/'images'/item['filename'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  record={
   'file':'images/'+item['filename'],'role':item['role'],
   'creator':'Alex Abair','license':'CC BY 4.0','license_url':LICENSE,
   'source_platform':'iNaturalist media via Wikimedia Commons rights verification',
   'source_page':'https://commons.wikimedia.org/wiki/File:Dichondra_carolinensis_'+item['id']+'.jpg',
   'source_observation':'https://www.inaturalist.org/observations/'+('149885787' if item['id']=='258349465' else '205610910'),
   'photo_id':item['id'],'downloaded_from':url,'image_dimensions':dims,
   'original_image_sha256':rawhash,'study_use':'Public educational use with credit',
   'public_reuse':'CC BY 4.0: author attribution, license link, modifications notice',
   'modifications':'Resized and EXIF removed; yellow anatomical arrows added where specified (original at Commons unchanged).',
   'photo_review':'Photo physically contact-reviewed and source image identical species determination at Commons; labeled anatomy checked at inspected screen view. A complete mature fruiting pedicel and millimeter sepal/fruit lengths are NOT validated.',
   'anatomy_arrows': 'Visible organ coordinates manually selected on photo preview; no unsupported exact-species stalk shape claims' if item['arrows'] else 'none; contextual field view'
  }
  images.append(record)
 card['images']=images
 card['curation_status']['photo_metadata_count']=len(images)
 card['curation_status']['photo_files_present']=len(images)
 card['curation_status']['visual_reviewed']=False
 card['curation_status']['finished_field_id_pass']='PASS_IN_PROGRESS'
 card['curation_status']['five_photo_install_verified']='2026-10-19'
 card['curation_status']['required_to_finish']=[
  'Inspect newly committed full annotated JPEGs at their displayed resolution and confirm arrows',
  'Mature fruit + whole pedicel comparative macro against Dichondra recurvata / introduced D. micrantha remains a separate desired teaching upgrade',
  'Check exact version of existing Douglas Goldman CC BY-SA photo source before claiming public-safe original gallery license version'
 ]
 card['learner_visual_status'].update({'status':'provisional_learner_ready',
  'mode':'finished_text_six_photo_gallery_pending_mature_stalk_comparison',
  'image_count':len(images),
  'note':'Original very close tiny flower with penny preserved + five distinct Commons-licensed, visually inspected habit/leaf/flower/developing-fruit views; annotated structures visually checked on previews. Mature D. carolinensis versus D. recurvata full-stalk key not yet illustrated.'})
 card['photo_note']='2026-10-19: source-vetted Commons CC BY 4.0 exact-species photos by Alex Abair installed in five roles, with three anatomical photo overlays based on actual visible structures. Original one-photo macro remains intact. Fruit pictures show small developing hairy capsules with persistent sepals, but DO NOT establish complete curved or straight pedicel or mature sepal/fruit millimeter ratio.'
 for d in card.get('diagnostic_photo_requirements',[]):
  if d.get('priority') in ('verified','critical'):d['status']='Installed teaching photo(s) where visible; mature exact-stalk-sepal species split remains a known photography limitation'
 FILE.write_text(json.dumps(card,indent=2,ensure_ascii=False)+'\n')
 csvfile=P/'image-sources.csv'
 with csvfile.open(newline='') as f:reader=csv.DictReader(f);header=reader.fieldnames;rows=list(reader)
 for x,_,_,_,url in imgs:
  row={h:'' for h in header}
  payload={'file_name':x['filename'],'role':x['role'],'creator':'Alex Abair','license':'CC BY 4.0',
   'license_url':LICENSE,'source_page':'https://commons.wikimedia.org/wiki/File:Dichondra_carolinensis_'+x['id']+'.jpg',
   'direct_url':url,'study_use':'Public attributed field education',
   'public_reuse':'CC BY 4.0, credit and changes notice','photo_id':x['id'],
   'modifications':'Resized JPEG; source EXIF stripped; yellow arrows if labeled'}
  for key,val in payload.items():
   if key in row:row[key]=val
  rows.append(row)
 with csvfile.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=header,lineterminator='\n');writer.writeheader();writer.writerows(rows)
 report={'taxon':SID,'new_count':len(imgs),'total_count':len(images),
         'photos':[{'id':i['id'],'file':i['filename'],'dimension':dims,'sha256_original':sha}
                   for i,_,sha,dims,_ in imgs],
         'existing_photo_preserved':True,'science_and_county_classification_unchanged':True,
         'publish_triggered':False,'pending':'mature stalk confirmation + original one-photo CC BY-SA license-version verification'}
 Path('reports/dichondra-carolinensis-finished-photo-20261019.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()

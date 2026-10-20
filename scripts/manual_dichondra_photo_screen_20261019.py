#!/usr/bin/env python3
"""Temporary visual contact sheet of license-documented exact-species Dichondra photos.
NOT a species card installer. Preserve all photo source credits and do not claim source IDs are verified by pixels.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests, io, json, hashlib
OUT=Path('workflow/photo-library/reviews/dichondra-carolinensis-20261019')
OUT.mkdir(parents=True,exist_ok=True)
ROWS=[
 ('258349465','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/149885787'),
 ('258349470','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/149885787'),
 ('363579431','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/205610910'),
 ('363579447','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/205610910'),
 ('363579498','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/205610910'),
 ('363579587','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/205610910'),
 ('363579722','Alex Abair','CC BY 4.0','https://www.inaturalist.org/observations/205610910'),
 ('37182598','T. J. Butler','CC0 1.0','https://www.inaturalist.org/observations/24048950'),
]
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
canvas=Image.new('RGB',(1320,1440),'#eff2ed')
draw=ImageDraw.Draw(canvas)
report=[]
for n,(pid,creator,license,observation) in enumerate(ROWS):
  col=n%2; row=n//2
  data=None;reason=None
  for variant in ('large','original'):
    url=f'https://inaturalist-open-data.s3.amazonaws.com/photos/{pid}/{variant}.jpg'
    try:
      resp=requests.get(url,timeout=22,headers={'User-Agent':'HaysBotanyDiagnosticReview/1.0 (educational-license-review)'})
      resp.raise_for_status()
      if len(resp.content)<12000:raise ValueError('unexpected tiny photo')
      with Image.open(io.BytesIO(resp.content)) as loaded:
        loaded.load(); im=ImageOps.exif_transpose(loaded).convert('RGB')
      data=im;break
    except Exception as e:reason=str(e)
  if data is None:
    report.append({'photo_id':pid,'status':'DOWNLOAD_FAILED','error':reason})
    draw.text((col*660+25,row*360+35),pid+' DOWNLOAD FAILED',font=FONT,fill='#331a1a')
    continue
  data.thumbnail((630,313),Image.Resampling.LANCZOS)
  x=col*660+15+(630-data.width)//2
  y=row*360+22+(313-data.height)//2
  canvas.paste(data,(x,y))
  draw.text((col*660+20,row*360+338),f'{pid} | {creator} | {license}',font=FONT,fill='#183c29')
  small=data.copy()
  small.save(OUT/f'{pid}.jpg',quality=86,optimize=True)
  report.append({'photo_id':pid,'status':'PHOTO_DOWNLOADED','creator':creator,'license_metadata':license,
  'observation':observation,'source_page':'https://commons.wikimedia.org/wiki/File:Dichondra_carolinensis_'+pid+'.jpg' if pid!='37182598' else 'https://commons.wikimedia.org/wiki/File:Dichondra_carolinensis.jpg',
  'source_image':url,'dimensions':list(im.size),'preview_path':str(OUT/f'{pid}.jpg'),
  'sha256_preview':hashlib.sha256((OUT/f'{pid}.jpg').read_bytes()).hexdigest(),
  'botanical_image_verification':'PENDING human visual inspection of photo'})
canvas.save(OUT/'contact.jpg',quality=91,optimize=True)
(OUT/'candidate-metadata.json').write_text(json.dumps({'taxon':'Dichondra carolinensis',
  'purpose':'Review candidate photos without canonical promotion. All original photos photo-source metadata must be verified again before installation.',
  'candidate_files':report},indent=2)+'\n')
print(json.dumps({'photo_successes':sum(r['status']=='PHOTO_DOWNLOADED' for r in report),
  'photo_failures':[r for r in report if r['status']!='PHOTO_DOWNLOADED'],
  'contact_sheet':str(OUT/'contact.jpg')},indent=2))

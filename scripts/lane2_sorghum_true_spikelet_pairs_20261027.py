import base64,hashlib,io,json,os,time,urllib.request,urllib.error
from PIL import Image,ImageOps
R=os.environ['GITHUB_REPOSITORY'];T=os.environ['GITHUB_TOKEN'];A='https://api.github.com/repos/'+R
P='content/taxa/Poaceae/Sorghum/sorghum-bicolor/'; N='matt-lavin-sorghum-terminal-spikelet-pairs-4055518933.jpg';F=P+'images/'+N
C=P+'species.json'; S='reports/lane2-six-role-photo-score-20261027.json';SRC=P+'image-sources.csv'
REP='reports/lane2-sorghum-bicolor-licensed-spikelet-pairs-20261027.json'
PAGE='https://commons.wikimedia.org/wiki/File:Sorghum_bicolor_(4055518933).jpg'
URL='https://upload.wikimedia.org/wikipedia/commons/8/8b/Sorghum_bicolor_%284055518933%29.jpg'
def gh(method,path,obj=None):
    req=urllib.request.Request(A+path,data=None if obj is None else json.dumps(obj,ensure_ascii=False).encode(),method=method,headers={'Authorization':'Bearer '+T,'Accept':'application/vnd.github+json','Content-Type':'application/json','User-Agent':'HaysBotany-Lane2-SpikeletPhoto'})
    with urllib.request.urlopen(req,timeout=45) as f:return json.load(f)
def read(p):return base64.b64decode(gh('GET','/contents/'+p+'?ref=main')['content']).decode()
def blob(x,binary=False):return gh('POST','/git/blobs',{'content':base64.b64encode(x).decode() if binary else x,'encoding':'base64' if binary else 'utf-8'})['sha']
req=urllib.request.Request(URL,headers={'User-Agent':'HaysBotany-Learner-OpenCreativeCommons/1.0'})
with urllib.request.urlopen(req,timeout=40) as f:raw=f.read(500000)
if not raw.startswith(b'\xff\xd8\xff') or len(raw)>499999:raise ValueError('Source not valid bounded JPEG')
with Image.open(io.BytesIO(raw)) as im:
    if im.format!='JPEG' or im.size!=(1076,688):raise ValueError('Source shape unexpectedly changed: '+str(im.size))
    output=io.BytesIO();ImageOps.exif_transpose(im).convert('RGB').save(output,format='JPEG',quality=92,optimize=True,subsampling=0)
data=output.getvalue();sha=hashlib.sha256(data).hexdigest();image_blob=blob(data,True)
rights={'creator':'Matt Lavin','license':'CC BY-SA 2.0 Generic','license_url':'https://creativecommons.org/licenses/by-sa/2.0/','source_page':PAGE,'source_image':URL,'public_reuse':'yes with photographer credit, license, ShareAlike','modifications':'Source photograph re-encoded to scrub EXIF/GPS without crop; separate SVG on-screen arrows','image_sha256':sha}
for attempt in range(7):
    head=gh('GET','/git/ref/heads/main')['object']['sha'];tree=gh('GET','/git/commits/'+head)['tree']['sha']
    card=json.loads(read(C));scores=json.loads(read(S));sources=read(SRC)
    if any(x.get('file')=='images/'+N for x in card['images']):print('ALREADY_PRESENT');break
    row=next(x for x in scores['records'] if x['canonical_id']=='sorghum-bicolor')
    if row['after_total']!=5 or row['roles']['reproductive_closeup']!=0.5:raise ValueError('Changed source baseline, hold review')
    card['images'].append({'file':'images/'+N,'role':'EXACT real reproductive macro with intact sorghum spikelet groups. Attached terminal spikes show multiple narrow pedicellate units; no millimeter scale, glume veins not asserted.',**rights})
    panel={'label':'ACTUAL SPIKELET GROUPS · terminal paired/triplet architecture','scientific_name':'Sorghum bicolor','image_url':F,'image_fit':'contain','image_role':'Photo of true spikelet structures, not whole seedhead','caption':'Real Matt Lavin Sorghum bicolor macro. The source description identifies spikelet pairs and a terminal set with two pedicellate spikelets. Observe slim pale terminal spikelets beside rounded hairy units. The photo does NOT show individually measured glume veins or a scale bar.','why_it_matters':'Moves from whole panicle and flower close-up to clearly photographed intact spikelet arrangement used in Sorghum discrimination.','markers':[{'label':'Narrow terminal spikelets','label_x':58,'label_y':8,'target_x':73,'target_y':24},{'label':'Rounded hairy spikelet exterior','label_x':43,'label_y':80,'target_x':61,'target_y':66}],**rights}
    gallery=card['visual_comparison']['items'];ix=next((i for i,x in enumerate(gallery) if x.get('scientific_name')=='Sorghum halepense'),len(gallery));gallery.insert(ix,panel)
    card['photo_note']=card.get('photo_note','')+'\n2026-10-27 Lane 2: original 1076x688 Matt Lavin CC BY-SA 2.0 real Sorghum bicolor terminal spikelet group archived, 2 anatomically conservative visible arrows. Attaches true reproductive closeup; not glume vein or true ruler proof.'
    row['roles']['reproductive_closeup']=1;row['after_total']=5.5;row['after_percentage']=92
    row['gaps_warning']='True sorghum terminal spikelet group macro now pictured with separate seedling roots; adult attached underground crown still not verified. No glume vein measurement.'
    v=[float(x['after_total']) for x in scores['records']];sm=scores['summary'];sm['mean_after_percent']=round(sum(v)/len(v)/6*100,1);sm['distribution']={f'{n:.1f}/6':v.count(n) for n in sorted(set(v))}
    sm['new_exact_species_jpegs_archived_this_pass']=int(sm.get('new_exact_species_jpegs_archived_this_pass',0))+1;sm['new_gross_structure_overlay_arrows_this_pass']=int(sm.get('new_gross_structure_overlay_arrows_this_pass',0))+2
    scores['final_photo_upgrade_source']=REP
    sources=sources.rstrip('\n')+'\n'+','.join([N,'"Sorghum bicolor terminal real spikelet groups; pedicellate spikelets per source"','"Matt Lavin"','"CC BY-SA 2.0"',PAGE,URL,'educational','"yes-license-credit-sharealike"'])+'\n'
    report={'date':'2026-10-27','species':'Sorghum bicolor','status':'FIELD_READY_PHOTO_GAPS','new_real_JPEGs':1,'arrows_added':2,'source_page':PAGE,'license':'Matt Lavin CC BY-SA 2.0','local_path':F,'sha256':sha,'archived_bytes':len(data),'source_dimensions':[1076,688],'before_roles':5,'after_roles':5.5,'after_percent':92,'remaining':['actual connected adult crown/roots','calibrated glume veins / lemma dissection'],'pages':'not verified'}
    files=[{'path':F,'mode':'100644','type':'blob','sha':image_blob}]
    for name,obj in [(C,json.dumps(card,indent=2,ensure_ascii=False)+'\n'),(S,json.dumps(scores,indent=2,ensure_ascii=False)+'\n'),(SRC,sources),(REP,json.dumps(report,indent=2,ensure_ascii=False)+'\n')]: files.append({'path':name,'mode':'100644','type':'blob','sha':blob(obj)})
    newtree=gh('POST','/git/trees',{'base_tree':tree,'tree':files})['sha']
    commit=gh('POST','/git/commits',{'message':'Lane 2: photograph authentic sorghum paired terminal spikelets licensed CC BY-SA [skip ci]','tree':newtree,'parents':[head]})['sha']
    try:gh('PATCH','/git/refs/heads/main',{'sha':commit,'force':False});print('COMMITTED',commit,'photo',F);break
    except urllib.error.HTTPError as ex:
        if ex.code!=422 or attempt==6:raise
        time.sleep(2)
else:raise RuntimeError('Could not install after concurrent changes')

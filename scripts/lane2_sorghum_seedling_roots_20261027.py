import base64,hashlib,io,json,os,time,urllib.request,urllib.error
from PIL import Image,ImageOps
R=os.environ['GITHUB_REPOSITORY']; T=os.environ['GITHUB_TOKEN']; A='https://api.github.com/repos/'+R
P='content/taxa/Poaceae/Sorghum/sorghum-bicolor/'
N='miquel-pujol-sorghum-two-seedlings-roots-2008.jpg'; F=P+'images/'+N
C=P+'species.json'; S='reports/lane2-six-role-photo-score-20261027.json'; SRC=P+'image-sources.csv'
REP='reports/lane2-sorghum-bicolor-seedling-roots-20261027.json'
PAGE='https://commons.wikimedia.org/wiki/File:LPCC-927-Pl%C3%A0ntules_de_sorgo_amb_arrels_advent%C3%ADcies.jpg'
URL='https://upload.wikimedia.org/wikipedia/commons/d/d1/LPCC-927-Pl%C3%A0ntules_de_sorgo_amb_arrels_advent%C3%ADcies.jpg'
def gh(m,path,j=None):
    req=urllib.request.Request(A+path,data=None if j is None else json.dumps(j,ensure_ascii=False).encode(),method=m,headers={'Authorization':'Bearer '+T,'Accept':'application/vnd.github+json','Content-Type':'application/json','User-Agent':'HaysBotany-Lane2-RootPhoto'})
    with urllib.request.urlopen(req,timeout=45) as f: return json.load(f)
def get(path): return base64.b64decode(gh('GET','/contents/'+path+'?ref=main')['content']).decode()
def blob(data,binary=False):
    return gh('POST','/git/blobs',{'content':base64.b64encode(data).decode() if binary else data,'encoding':'base64' if binary else 'utf-8'})['sha']
raw=urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'HaysBotany-Educational-Reuse/1.0'}),timeout=45).read(600000)
if not raw.startswith(b'\xff\xd8\xff') or len(raw)>599999: raise ValueError('Unexpected JPEG source')
with Image.open(io.BytesIO(raw)) as src:
    if src.format!='JPEG' or src.size!=(981,1359): raise ValueError('Source pixels changed: '+str(src.size))
    out=io.BytesIO(); ImageOps.exif_transpose(src).convert('RGB').save(out,format='JPEG',quality=92,optimize=True,subsampling=0)
data=out.getvalue(); sha256=hashlib.sha256(data).hexdigest(); photo=blob(data,True)
rights={'creator':'Miquel Pujol Palol','license':'CC BY-SA 3.0 Unported','license_url':'https://creativecommons.org/licenses/by-sa/3.0/','source_page':PAGE,'source_image':URL,'public_reuse':'yes, with attribution and ShareAlike','modifications':'Original JPEG recompressed RGB with EXIF removed; existing in-image Catalan text preserved; new separate SVG arrows','image_sha256':sha256}
for attempt in range(7):
    head=gh('GET','/git/ref/heads/main')['object']['sha']; tree=gh('GET','/git/commits/'+head)['tree']['sha']
    c=json.loads(get(C)); scores=json.loads(get(S)); sources=get(SRC)
    if any(x.get('file')=='images/'+N for x in c['images']): print('ALREADY_INSTALLED',F); break
    row=next(x for x in scores['records'] if x['canonical_id']=='sorghum-bicolor')
    if row['after_total']!=4.5 or row['roles']['rooted_base_growth_mechanism']!=0: raise ValueError('Score changed; hold manual review')
    c['images'].append({'file':'images/'+N,'role':'Actual two-week-old Sorghum bicolor seedlings with exposed adventitious roots; NOT mature crown',**rights})
    p={'label':'ACTUAL SEEDLING ROOTS · adventitious roots (not mature crown)','scientific_name':'Sorghum bicolor','image_url':F,'image_fit':'contain','image_role':'Photographed seedlings with attached adventitious roots only','caption':'Two-week-old sorghum seedlings with visible roots. Original Catalan text arrels adventícies = adventitious roots. Do not mistake this for mature crown anatomy or for Johnsongrass rhizomes.','why_it_matters':'Shows true attached seedling roots; adult root system remains unresolved.','markers':[{'label':'Living seedling culm base','label_x':55,'label_y':36,'target_x':56,'target_y':52},{'label':'Visible adventitious roots','label_x':60,'label_y':85,'target_x':68,'target_y':71}],**rights}
    cards=c['visual_comparison']['items']; ix=next((i for i,x in enumerate(cards) if x.get('scientific_name')=='Sorghum halepense'),len(cards)); cards.insert(ix,p)
    c['photo_note']=c.get('photo_note','')+'\n2026-10-27: Miquel Pujol Palol CC BY-SA 3.0 real 2-week sorghum seedlings archived; true seedling adventitious roots shown, adult crown still unphotographed. Two gross overlay arrows.'
    row['roles']['rooted_base_growth_mechanism']=0.5; row['after_total']=5; row['after_percentage']=83
    row['gaps_warning']='Actual seedling roots pictured. Mature crop crown and measured attached fertile/pedicelled spikelets remain unphotographed.'
    sm=scores['summary']; vals=[float(x['after_total']) for x in scores['records']]; sm['mean_after_percent']=round(sum(vals)/len(vals)/6*100,1)
    sm['distribution']={f'{v:.1f}/6':vals.count(v) for v in sorted(set(vals))}; sm['new_exact_species_jpegs_archived_this_pass']=int(sm.get('new_exact_species_jpegs_archived_this_pass',0))+1; sm['new_gross_structure_overlay_arrows_this_pass']=int(sm.get('new_gross_structure_overlay_arrows_this_pass',0))+2
    scores['final_photo_upgrade_source']=REP
    sources=sources.rstrip('\n')+'\n'+','.join([N,'"Actual attached sorghum seedling adventitious roots, not mature"','"Miquel Pujol Palol"','"CC BY-SA 3.0"',PAGE,URL,'educational','"attribution-and-sharealike-required"'])+'\n'
    report={'date':'2026-10-27','species':'Sorghum bicolor','status':'FIELD_READY_PHOTO_GAPS','local_photo':F,'image_sha256':sha256,'image_size_bytes':len(data),'source_image_dimensions':[981,1359],'source_page':PAGE,'license':'CC BY-SA 3.0','before_score':4.5,'after_score':5,'after_percent':83,'arrows_added':2,'remaining_gaps':['mature root crown','attached scaled fertile/pedicelled reproductive pairs'],'public_pages':'not verified'}
    files=[{'path':F,'mode':'100644','type':'blob','sha':photo}]
    for path,obj in [(C,json.dumps(c,ensure_ascii=False,indent=2)+'\n'),(S,json.dumps(scores,ensure_ascii=False,indent=2)+'\n'),(SRC,sources),(REP,json.dumps(report,indent=2)+'\n')]: files.append({'path':path,'mode':'100644','type':'blob','sha':blob(obj)})
    newtree=gh('POST','/git/trees',{'base_tree':tree,'tree':files})['sha']
    commit=gh('POST','/git/commits',{'message':'Lane 2: real licensed Sorghum bicolor seedling roots and honest partial score [skip ci]','tree':newtree,'parents':[head]})['sha']
    try: gh('PATCH','/git/refs/heads/main',{'sha':commit,'force':False}); print('COMMITTED',commit,'PHOTO',F,'SHA256',sha256); break
    except urllib.error.HTTPError as e:
        if e.code!=422 or attempt==6: raise
        print('REBASE RETRY',attempt);time.sleep(3)
else: raise RuntimeError('Root photo not installed')

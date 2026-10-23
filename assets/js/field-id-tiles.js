/* Hays Botany compact Field ID. All facts/photos come from filtered public plant records. */
(function(){
'use strict';
const state={records:[],rank:'families',family:'',genus:'',query:'',limit:60,selected:null,cache:new Map(),loading:true};
const root=document.getElementById('fieldApp');
const dialog=document.getElementById('fieldDetail');
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const low=v=>String(v||'').toLocaleLowerCase();
const memberName=item=>item.common_name||item.scientific_name||item.id||'Unnamed species';
const latinName=item=>item.scientific_name||String(item.id||'').replace(/-/g,' ');
const safePath=path=>{
 if(typeof path!=='string'||/^(?:https?:|\/)/i.test(path)||path.includes('..')||path.includes('\\'))return '';
 if(!/^(?:content\/taxa\/[a-z0-9_/-]+(?:\.(?:jpg|jpeg|png|webp)|\/species\.json))$/i.test(path))return '';
 return './'+path.split('/').map(encodeURIComponent).join('/');
};
const photo=(item,kind)=>{
 const path=safePath(item.thumbnail);
 const credit=[item.thumbnail_creator,item.thumbnail_license].filter(Boolean).join(' · ');
 return path?'<div class="tile-image"><img loading="lazy" decoding="async" src="'+esc(path)+'" alt="'+esc(memberName(item))+' — example '+esc(kind)+' member" onerror="this.closest(\'.tile-image\').classList.add(\'photo-missing\');this.remove()">'+
  (credit?'<span class="tile-photo-credit">'+esc(credit)+'</span>':'')+'</div>':
  '<div class="tile-image no-photo" aria-hidden="true"><span>✳</span></div>';
};
const sorted=(a,b)=>a.localeCompare(b);
function groups(rank){
 const lookup=new Map();
 for(const p of state.records){
  const f=String(p.family||''),g=String(p.genus||'');
  if(!f||(rank==='genera'&&!g))continue;
  if(state.family&&f!==state.family)continue;
  if(state.genus&&g!==state.genus)continue;
  const key=rank==='families'?f:f+'|||'+g;
  if(!lookup.has(key))lookup.set(key,{name:rank==='families'?f:g,family:f,genus:rank==='genera'?g:'',count:0,example:p});
  const group=lookup.get(key);group.count++;
  if(!group.example.thumbnail&&p.thumbnail)group.example=p;
 }
 return [...lookup.values()].sort((a,b)=>sorted(a.name,b.name)||sorted(a.family,b.family));
}
function filtered(){
 const q=low(state.query.trim());
 if(state.rank==='species'){
  return state.records.filter(p=>(!state.family||p.family===state.family)&&
   (!state.genus||p.genus===state.genus)&&
   (!q||low([p.common_name,p.scientific_name,p.family,p.genus,p.cue].join(' ')).includes(q)))
   .sort((a,b)=>sorted(memberName(a),memberName(b)));
 }
 return groups(state.rank).filter(g=>!q||low(g.name+' '+g.family).includes(q));
}
function tile(item){
 if(state.rank==='families')return '<button class="field-tile" data-family="'+esc(item.family)+'">'+
  photo(item.example,'family')+'<div class="tile-body"><span class="rank-label">Family</span>'+
  '<strong>'+esc(item.name)+'</strong><span class="tile-sub">'+item.count+' species in library · example: '+esc(memberName(item.example))+'</span>'+
  '<span class="tile-action">See genera →</span></div></button>';
 if(state.rank==='genera')return '<button class="field-tile" data-genus="'+esc(item.genus)+'" data-parent-family="'+esc(item.family)+'">'+
  photo(item.example,'genus')+'<div class="tile-body"><span class="rank-label">'+esc(item.family)+' · Genus</span>'+
  '<strong><i>'+esc(item.name)+'</i></strong><span class="tile-sub">'+item.count+' species · example: '+esc(memberName(item.example))+'</span>'+
  '<span class="tile-action">See species →</span></div></button>';
 return '<button class="field-tile" data-species="'+esc(item.id)+'" aria-label="Open '+esc(memberName(item))+' identification card">'+
  photo(item,'species')+'<div class="tile-body"><span class="rank-label">'+esc(item.family)+'</span>'+
  '<strong>'+esc(memberName(item))+'</strong><span class="latin">'+esc(latinName(item))+'</span>'+
  '<span class="tile-cue">'+esc(item.cue||'Tap for field recognition clues and photos.')+'</span>'+
  '<span class="tile-action">Open field ID →</span></div></button>';
}
function countLabel(){
 return state.records.length+' species · '+groupsAll('families').length+' families · '+groupsAll('genera').length+' genera';
}
function groupsAll(rank){
 const seen=new Set();for(const p of state.records){if(!p.family)continue;seen.add(rank==='families'?p.family:p.family+'||'+p.genus);}
 return [...seen];
}
function render(){
 const results=state.loading?[]:filtered();
 const title=state.genus?state.genus:state.family?state.family:
  state.rank==='families'?'Find the family.':state.rank==='genera'?'Pick a genus.':'Identify a species.';
 const summary=state.genus?'Tap a species to open a compact field ID with photos, cues and look-alikes.':
  state.family?'Choose a genus, then a species to see the ID details.':
  'Find your plant in a few taps. Open a tile only when you want more detail.';
 const level=['families','genera','species'];
 const tabs=level.map(r=>'<button type="button" class="rank-tab" data-rank="'+r+'" aria-pressed="'+String(state.rank===r)+'">'+
  r[0].toUpperCase()+r.slice(1)+'</button>').join('');
 const crumbs='<div class="crumbline"><button type="button" data-root-browse>All families</button>'+
  (state.family?'<span>›</span><button type="button" data-family="'+esc(state.family)+'">'+esc(state.family)+'</button>':'')+
  (state.genus?'<span>›</span><span><i>'+esc(state.genus)+'</i></span>':'')+'</div>';
 const cards=results.slice(0,state.limit).map(tile).join('');
 root.innerHTML='<div class="field-intro"><p class="eyebrow">Quick field reference</p><h1>'+esc(title)+'</h1>'+
 '<p>'+esc(summary)+'</p></div>'+crumbs+
 '<section class="browse-tools"><div class="rank-tabs" role="group" aria-label="Browse by family, genus or species">'+tabs+'</div>'+
 '<label for="fieldSearch">Search the plant library</label>'+
 '<input id="fieldSearch" type="search" placeholder="Search common names, botanical names, or families…" value="'+esc(state.query)+'" autocomplete="off">'+
 '<p id="resultCount" class="result-count" role="status">'+(state.loading?'Loading the photo-ready plant library…':
 results.length+' '+(state.rank==='species'?'species':state.rank==='families'?'families':'genera')+' found · '+countLabel())+'</p></section>'+
 '<section class="field-grid" id="fieldResults" aria-label="Plant tiles">'+
 (state.loading?'<div class="loading-tile">Loading tiles and photos…</div>':cards||'<p>No matching entries. Try a different search.</p>')+
 '</section>'+(results.length>state.limit?'<button type="button" class="show-more" data-more>Show more ('+
 (results.length-state.limit)+' remaining)</button>':'')+
 '<div class="field-footer">Want the complete technical tools? <a href="./field-id-classic.html">Advanced Field ID and Compare ↗</a> · '+
 '<a href="./index.html">Full illustrated Learner ↗</a></div>';
 const search=document.getElementById('fieldSearch');
 if(search)search.addEventListener('input',e=>{
  state.query=e.target.value;state.limit=60;renderResultsOnly();
 });
}
function renderResultsOnly(){
 const list=filtered();
 const grid=document.getElementById('fieldResults');
 if(grid)grid.innerHTML=list.slice(0,state.limit).map(tile).join('')||'<p>No matching entries. Try a different search.</p>';
 const count=document.getElementById('resultCount');
 if(count)count.textContent=list.length+' '+(state.rank==='species'?'species':state.rank==='families'?'families':'genera')+' found · '+countLabel();
 const old=document.querySelector('[data-more]');
 if(old)old.remove();
 if(list.length>state.limit){
  grid.insertAdjacentHTML('afterend','<button type="button" class="show-more" data-more>Show more ('+(list.length-state.limit)+' remaining)</button>');
 }
}
function change(rank,family,genus){
 state.rank=rank;state.family=family||'';state.genus=genus||'';state.query='';state.limit=60;
 render();document.getElementById('fieldApp').scrollIntoView({block:'start',behavior:'instant'});
}
function firstText(value,max){
 return String(value||'').replace(/\s+/g,' ').slice(0,max);
}
function cues(sp){
 const mor=sp.morphology_keys||{},steps=mor.crew_20_second_sequence||mor.best_field_traits||[];
 if(Array.isArray(steps)&&steps.length)return steps.slice(0,5).filter(x=>typeof x==='string').map(x=>'<li>'+esc(x)+'</li>').join('');
 return '<li>'+esc(sp.look_here_first||'Look at the leaf attachment and flowering structures. Confirm against a verified photo.')+'</li>';
}
function fullMorph(sp){
 const morphology=sp.morphology_keys||{};
 const entries=Object.entries(morphology).filter(([key,v])=>
  key!=='crew_20_second_sequence'&&key!=='best_field_traits'&&
  (typeof v==='string'||Array.isArray(v))).slice(0,24);
 return entries.map(([key,v])=>
  '<div class="note-field"><b>'+esc(key.replace(/_/g,' '))+'</b><p>'+esc(Array.isArray(v)?v.join(' · '):v)+'</p></div>').join('');
}
function lookalikes(sp){
 const cp=sp.comparisons||{};
 const confused=Array.isArray(cp.confused_with)?cp.confused_with.slice(0,8):[];
 return (confused.length?'<p class="lookalike-names"><b>Look-alikes:</b> '+confused.map(esc).join(' · ')+'</p>':'')+
  (cp.key_distinctions?'<p>'+esc(cp.key_distinctions)+'</p>':'')+
  (cp.taxonomy_caution?'<p class="caution"><b>Taxonomy caution:</b> '+esc(cp.taxonomy_caution)+'</p>':'');
}
function photosFor(sp,path){
 const list=Array.isArray(sp.images)?sp.images.slice(0,10):[];
 const parent=path.slice(0,path.lastIndexOf('/')+1);
 const parts=list.filter(x=>x&&typeof x.file==='string'&&
  !x.file.includes('..')&&!x.file.startsWith('/')&&!x.file.includes('\\')).map(item=>{
  const path=safePath(parent+item.file);
  if(!path)return '';
  const link=/^https:\/\//.test(item.source_page||'')?'<a href="'+esc(item.source_page)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':'';
  return '<figure class="detail-photo"><img src="'+esc(path)+'" loading="lazy" alt="'+esc(item.role||sp.scientific_name)+'">'+
   '<figcaption><span>'+esc(item.role||'Plant reference')+'</span>'+
   '<small>'+esc(item.creator||'Source credited in canonical record')+' · '+esc(item.license||'')+'</small>'+
   link+'</figcaption></figure>';
 }).filter(Boolean);
 return parts.length?'<div class="detail-gallery" aria-label="Licensed species photographs">'+parts.join('')+'</div>':
  '<p class="no-image">No public-approved photo has been selected for this card yet.</p>';
}
function renderDetail(sp,entry){
 dialog.innerHTML='<div class="dialog-inner">'+
 '<div class="detail-head"><div><p class="eyebrow">'+esc(sp.family||entry.family)+' / '+esc(sp.genus||entry.genus)+'</p>'+
 '<h2 id="fieldDetailTitle">'+esc(sp.common_name||entry.common_name||sp.scientific_name)+'</h2>'+
 '<p class="detail-latin"><i>'+esc(sp.scientific_name||entry.scientific_name)+'</i></p></div>'+
 '<button class="close" type="button" data-close aria-label="Close field card">×</button></div>'+
 photosFor(sp,entry.path)+
 '<div class="detail-section"><h3>Look here first</h3><p>'+esc(sp.look_here_first||entry.cue||'Start with mature leaves and any reproductive structures.')+'</p></div>'+
 '<div class="detail-section"><h3>Field ID checklist</h3><ul>'+cues(sp)+'</ul></div>'+
 '<details class="detail-expand"><summary>Look-alikes and cautions</summary>'+
 (lookalikes(sp)||'<p>No verified comparison text has been entered yet.</p>')+'</details>'+
 '<details class="detail-expand"><summary>More botanical details</summary>'+
 (fullMorph(sp)||'<p>Additional morphological notes have not been added yet.</p>')+'</details>'+
 '<div class="dialog-foot"><button type="button" class="close-secondary" data-close>Back to tiles</button>'+
 '<a href="./index.html" class="open-learner">Browse full Learner ↗</a></div></div>';
 dialog.showModal();
 dialog.querySelector('[data-close]').focus();
}
async function openSpecies(id,trigger){
 const entry=state.records.find(p=>p.id===id);
 if(!entry)return;
 state.selected=entry.id;
 dialog.innerHTML='<div class="loading-dialog"><button type="button" data-close aria-label="Close">×</button>'+
 '<p>Loading '+esc(memberName(entry))+' ID details…</p></div>';
 dialog.showModal();
 try{
  let payload=state.cache.get(id);
  if(!payload){
   const r=await fetch(safePath(entry.path),{cache:'no-store'});
   if(!r.ok)throw Error('Species file unavailable');
   payload=await r.json();state.cache.set(id,payload);
  }
  if(state.selected===id&&dialog.open)renderDetail(payload,entry);
 }catch(err){
  dialog.innerHTML='<div class="loading-dialog"><button data-close>× Close</button>'+
   '<p>Could not load this plant record. Try again when online.</p></div>';
 }
}
document.addEventListener('click',event=>{
 const target=event.target.closest('button');
 if(!target)return;
 if(target.hasAttribute('data-family')){change('genera',target.dataset.family,'');return;}
 if(target.hasAttribute('data-genus')){change('species',target.dataset.parentFamily,target.dataset.genus);return;}
 if(target.hasAttribute('data-root-browse')){change('families','','');return;}
 if(target.dataset.rank){change(target.dataset.rank,'','');return;}
 if(target.dataset.species){openSpecies(target.dataset.species,target);return;}
 if(target.hasAttribute('data-more')){state.limit+=60;renderResultsOnly();return;}
 if(target.hasAttribute('data-close')){dialog.close();return;}
});
dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
dialog.addEventListener('close',()=>{state.selected=null;});
async function init(){
 render();
 try{
  let json;
  try{
   const r=await fetch('./data/field-id-index.json',{cache:'no-store'});
   if(!r.ok)throw Error('Index missing');
   json=await r.json();
  }catch(err){
   // Development / old offline snapshot fallback has no stored thumbnail index.
   const r=await fetch('./data/learner-search-index.json',{cache:'no-store'});
   if(!r.ok)throw Error('Plant index unavailable');
   const names=await r.json();
   const mr=await fetch('./data/manifest.json',{cache:'no-store'});
   if(!mr.ok)throw Error('Manifest unavailable');
   const manifest=await mr.json();
   const map=new Map((names.species||[]).map(x=>[x.id,x]));
   json={species:(manifest.species||[]).map(e=>({...map.get(e.id),id:e.id,path:e.path,thumbnail:'',photo_count:0}))};
  }
  if(!Array.isArray(json.species))throw Error('Invalid plant index');
  state.records=json.species.filter(x=>x&&x.id&&x.path);
  state.loading=false;render();
 }catch(err){state.loading=false;root.innerHTML='<section class="error-tile"><h2>Plant library unavailable</h2><p>Could not load the published tiles. Check your connection and refresh.</p></section>';}
}
init();
})();

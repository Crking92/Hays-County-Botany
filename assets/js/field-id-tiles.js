/* Hays Botany compact Field ID. All facts/photos come from filtered public plant records. */
(function(){
'use strict';
const state={records:[],rank:'families',family:'',genus:'',query:'',limit:60,selected:null,cache:new Map(),groupCache:new Map(),loading:true};
const root=document.getElementById('fieldApp');
const dialog=document.getElementById('fieldDetail');
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const low=v=>String(v||'').toLocaleLowerCase();
const memberName=item=>item.common_name||item.scientific_name||item.id||'Unnamed species';
const latinName=item=>item.scientific_name||String(item.id||'').replace(/-/g,' ');
const safePath=path=>{
 if(typeof path!=='string'||/^(?:https?:|\/)/i.test(path)||path.includes('..')||path.includes('\\'))return '';
 if(!/^content\/taxa\//i.test(path)||!/\.(?:json|jpg|jpeg|png|webp)$/i.test(path))return '';
 const segments=path.split('/');
 if(segments.length<4||segments.some(v=>!v||v==='.'||v==='..'||/[?#&<>\x00-\x1f]/.test(v)))return '';
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
const textItems=(v,max=12)=>Array.isArray(v)?v.filter(x=>typeof x==='string').slice(0,max):
 typeof v==='string'?[v]:[];
function listHTML(items){
 return items.length?'<ul>'+items.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':'';
}
function groupCue(record,rank){
 const d=rank==='families'?record.family_diagnostics||{}:record.recognition||{};
 const main=rank==='families'?(d.where_to_look_first||d.field_tip||record.look_here_first):
  (record.look_here_first||d.where_to_look_first||d.look_here_first);
 const priority=rank==='genera'?textItems(d.priority,3):[];
 if(!main&&!priority.length)return '';
 return '<div class="group-tip lessonpart"><strong>Look here first · '+(rank==='families'?'Family':'Genus')+'</strong>'+
  (main?'<p>'+esc(main)+'</p>':'')+listHTML(priority)+'</div>';
}
async function loadGroupCue(){
 const rank=state.family&&!state.genus?'families':state.genus?'genera':null;
 if(!rank)return;
 const path=rank==='families'?'content/taxa/'+state.family+'/family.json':
  'content/taxa/'+state.family+'/'+state.genus+'/genus.json';
 const el=document.getElementById('fieldGroupClue');
 if(!el)return;
 try{
  let data=state.groupCache.get(path);
  if(!data){
   const r=await fetch(safePath(path),{cache:'no-store'});
   if(!r.ok)return;
   data=await r.json();state.groupCache.set(path,data);
  }
  const target=document.getElementById('fieldGroupClue');
  if(!target||target.dataset.source!==path)return;
  target.innerHTML=groupCue(data,rank);
  if(window.HaysGlossary)window.HaysGlossary.enhance(target);
 }catch(err){console.info('Group field hint unavailable',path);}
}

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
 // Search common/scientific species names even while browsing families
 // and genera. This lets a crew member find the correct group from the top.
 const matches=new Set(state.records.filter(p=>
  !q||low([p.common_name,p.scientific_name,p.family,p.genus,p.cue].join(' ')).includes(q)
 ).map(p=>state.rank==='families'?p.family:p.family+'|||'+p.genus));
 return groups(state.rank).filter(g=>
  !q||low(g.name+' '+g.family).includes(q)||
  matches.has(state.rank==='families'?g.family:g.family+'|||'+g.genus));
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
 (state.family?'<div id="fieldGroupClue" data-source="'+esc(state.genus?'content/taxa/'+state.family+'/'+state.genus+'/genus.json':'content/taxa/'+state.family+'/family.json')+'"></div>':'')+
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
 render();loadGroupCue();document.getElementById('fieldApp').scrollIntoView({block:'start',behavior:'auto'});
}
function firstText(value,max){
 return String(value||'').replace(/\s+/g,' ').slice(0,max);
}
function cueSteps(sp){
 const mor=sp.morphology_keys||{},fin=sp.field_id_finish_pass||{},photo=sp.field_photo_quickcheck||{};
 // Curated beginner cards must show the actual five plain-English field steps.
 // Specialist evidence remains in the expanded morphology and confirmation notes.
 const preferred=sp.beginner_learning_path&&Array.isArray(photo.steps)?
   [photo.steps,mor.crew_20_second_sequence,fin.crew_field_sequence,mor.best_field_traits]:
   [mor.crew_20_second_sequence,fin.crew_field_sequence,photo.steps,mor.best_field_traits];
 for(const candidate of preferred){
  const safe=Array.isArray(candidate)?candidate.map(v=>typeof v==='string'?v:v&&typeof v==='object'&&typeof v.text==='string'?v.text:v&&typeof v==='object'&&typeof v.cue==='string'?v.cue:null).filter(Boolean):[];
  if(safe.length)return safe;
 }
 return [sp.look_here_first||'Check leaf attachment and flowering structures against confirmed photographs.'];
}
function cues(sp){
 return listHTML(cueSteps(sp).slice(0,5));
}
function fullMorph(sp){
 const morphology=sp.morphology_keys||{};
 const entries=Object.entries(morphology).filter(([key,v])=>
  key!=='crew_20_second_sequence'&&key!=='best_field_traits'&&
  (typeof v==='string'||Array.isArray(v)));
 return entries.map(([key,v])=>{
  const safe=typeof v==='string'?[v]:v.filter(x=>typeof x==='string').slice(0,12);
  if(!safe.length)return '';
  return '<div class="note-field"><b>'+esc(key.replace(/_/g,' '))+'</b>'+
   (safe.length===1?'<p>'+esc(safe[0])+'</p>':listHTML(safe))+'</div>';
 }).filter(Boolean).join('');
}
function comparisonMatrix(sp){
 const comp=sp.comparisons||{};
 const rows=Array.isArray(comp.field_matrix)?comp.field_matrix.slice(0,10):[];
 const clean=rows.map(row=>{
  if(!row||typeof row!=='object')return '';
  const label=row.taxon||row.lookalike||row.with||row.species||row.name||'Comparison';
  const parts=[
   ['Look at',row.where_to_look||row.focus||row.look_here_first],
   ['Identification',row.usual_pattern||row.rule||row.cue||row.other],
   ['This plant',row.little_bluestem||row.frogfruit],
   ['Limitations',row.limitation||row.caution]
  ].filter(([,value])=>typeof value==='string'&&value.trim());
  return '<article class="comparison-mini"><b>'+esc(label)+'</b>'+
   parts.map(([label,v])=>'<p><strong>'+esc(label)+':</strong> '+esc(v)+'</p>').join('')+'</article>';
 }).filter(Boolean).join('');
 const paired=comp.detailed_pair&&typeof comp.detailed_pair==='object'?comp.detailed_pair:{};
 const rules=textItems(paired.quick_split,5);
 const warnings=textItems(comp.do_not_trust_alone||comp.not_reliable_alone,8);
 return (rules.length?'<h4>Fast local comparison</h4>'+listHTML(rules):'')+
  (clean?'<h4>Comparison details</h4><div class="comparison-list">'+clean+'</div>':'')+
  (warnings.length?'<h4>Do not rely on these alone</h4>'+listHTML(warnings):'');
}
function lookalikes(sp){
 const cp=sp.comparisons||{};
 const confused=Array.isArray(cp.confused_with)?cp.confused_with.slice(0,12):[];
 return (confused.length?'<p class="lookalike-names"><b>Look-alikes:</b> '+confused.map(esc).join(' · ')+'</p>':'')+
  (typeof cp.key_distinctions==='string'?'<p>'+esc(cp.key_distinctions)+'</p>':'')+
  (typeof cp.taxonomy_caution==='string'?'<p class="caution"><b>Taxonomy caution:</b> '+esc(cp.taxonomy_caution)+'</p>':'')+
  comparisonMatrix(sp);
}
function confirmation(sp){
 const morph=sp.morphology_keys||{};
 const checks=sp.field_photo_quickcheck||{};
 const fin=sp.field_id_finish_pass||{};
 const notes=[
  ['Important caution',checks.warning],
  ['Stop at genus when uncertain',morph.when_to_stop_at_genus],
  ['Advanced confirmation',morph.advanced_confirmation],
  ['What to photograph',sp.what_to_photograph_for_confirmation||morph.what_to_photograph_for_confirmation],
  ['Identification guardrails',fin.science_guardrails]
 ];
 return notes.map(([label,v])=>{
  const items=textItems(v,8);
  return items.length?'<div class="note-field"><b>'+esc(label)+'</b>'+
   (items.length===1?'<p>'+esc(items[0])+'</p>':listHTML(items))+'</div>':'';
 }).filter(Boolean).join('');
}
function visualCoverage(sp){
 const visual=sp.learner_visual_status||{},curation=sp.curation_status||{},fin=sp.field_id_finish_pass||{};
 const flag=[visual.status,curation.visual_finish,fin.status,fin.stage].filter(x=>typeof x==='string').join(' ');
 const gaps=textItems(fin.true_photo_gaps,5);
 const incomplete=/PHOTO.GAPS|PENDING|PROVISIONAL|IN_PROGRESS|HOLD|UNFINISHED/i.test(flag);
 if(!incomplete&&!gaps.length)return '';
 return '<div class="photo-coverage-caution"><b>Photo lesson still being improved</b>'+
  '<p>Use several matching structures before confirming an identification. Existing photographs may not show every required diagnostic feature.</p>'+
  (gaps.length?'<details><summary>Photographs still needed</summary>'+listHTML(gaps)+'</details>':'')+
  '</div>';
}
/* Four source-credited teaching photos appear before the advanced gallery.
   Canonical panel/image identifiers remain stable and no new arrows are guessed. */
function panelBelongsTo(sp,panel){
 const name=String(panel&&panel.scientific_name||'');
 return name===sp.scientific_name ||
  name.startsWith(sp.scientific_name+' subsp. ') ||
  name.startsWith(sp.scientific_name+' (');
}
function savedStarterArrows(panel,id){
 const markers=Array.isArray(panel.markers)?panel.markers.filter(m=>m&&
  typeof m.label==='string'&&m.label.trim()&&
  ['label_x','label_y','target_x','target_y'].every(k=>
    Number.isFinite(Number(m[k]))&&Number(m[k])>=0&&Number(m[k])<=100)):[];
 if(!markers.length)return '';
 const markerId='fieldStarterArrow'+id.replace(/[^a-z0-9]/gi,'');
 return '<div class="detail-photo-overlay" aria-label="Identification arrows">'+
 '<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'+
 '<defs><marker id="'+markerId+'" markerWidth="3.4" markerHeight="3.4" refX="2.5" refY="1.7" orient="auto">'+
 '<path d="M0 0 L3.4 1.7 L0 3.4 Z" fill="#f7e6a0"/></marker></defs>'+
 markers.map(m=>'<line x1="'+Number(m.label_x)+'" y1="'+Number(m.label_y)+
 '" x2="'+Number(m.target_x)+'" y2="'+Number(m.target_y)+
 '" marker-end="url(#'+markerId+')"/>').join('')+'</svg>'+
 markers.map(m=>'<span class="detail-arrow-label" style="left:'+Number(m.label_x)+
 '%;top:'+Number(m.label_y)+'%">'+esc(m.label)+'</span>').join('')+'</div>';
}
function fieldBeginnerPath(sp,path){
 const lesson=sp.beginner_learning_path;
 const panels=sp.visual_comparison?.items;
 if(!lesson||!Array.isArray(lesson.steps)||!Array.isArray(panels))return '';
 const parent=path.slice(0,path.lastIndexOf('/')+1);
 const cards=lesson.steps.slice(0,4).map((step,index)=>{
  const p=panels[step.panel_index];
  if(!p||!panelBelongsTo(sp,p)||!String(p.image_url||'').startsWith(parent))return '';
  const media=(sp.images||[]).find(img=>parent+img.file===p.image_url);
  if(!media||!media.creator||!media.license)return '';
  const src=safePath(p.image_url);
  if(!src)return '';
  const source=/^https:\/\//.test(media.source_page||'')?
   '<a href="'+esc(media.source_page)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':'';
  return '<article class="field-starter-card"><figure><div class="detail-photo-image">'+
   '<img src="'+esc(src)+'" loading="'+(index===0?'eager':'lazy')+'" alt="'+
   esc(step.title+': '+step.look_for)+'">'+
   savedStarterArrows(p,sp.id+index)+'</div><figcaption>'+
   '<small>'+esc(media.creator)+' · '+esc(media.license)+'</small> '+source+
   '</figcaption></figure><div class="field-starter-copy"><h4>'+esc(step.title)+'</h4>'+
   '<p>'+esc(step.look_for)+'</p><p class="field-starter-why"><b>Why it matters:</b> '+
   esc(step.why_it_matters)+'</p></div></article>';
 }).filter(Boolean);
 if(!cards.length)return '';
 return '<section class="field-reed-starter" aria-label="Four step photo identification lesson">'+
 '<p class="eyebrow">Beginner field ID · actual plant photographs</p>'+
 '<h3>'+esc(lesson.title||'Start with these photos')+'</h3>'+
 '<p class="field-starter-intro">'+esc(lesson.intro||'Follow each view in order.')+'</p>'+
 '<p class="field-starter-memory"><b>Remember:</b> '+esc(lesson.memory_rule||'Compare several structures.')+'</p>'+
 '<div class="field-starter-grid">'+cards.join('')+'</div>'+
 (lesson.safety_note?'<p class="field-starter-safety"><b>Stop and check:</b> '+
 esc(lesson.safety_note)+'</p>':'')+'</section>';
}
/* Concrete look-alike choices, not an empty generic accordion.
   All choices resolve to published species records; never create a synthetic taxon. */
const reedChoices={
 'arundo-donax':['phragmites-australis','zizaniopsis-miliacea'],
 'phragmites-australis':['arundo-donax','zizaniopsis-miliacea'],
 'zizaniopsis-miliacea':['arundo-donax','phragmites-australis']
};
const reedComparisonCues={
 'arundo-donax':{
  label:'Giant reed · Arundo donax',
  clues:['Thick, jointed, cane-like stems with broad, wrapping leaf bases.',
         'Large branching plume with multi-flowered spikelets.',
         'Silky reproductive hairs associated mainly with the lemma/floret bases.'],
  caution:'Do not decide from overall height or a fluffy plume alone; check leaf collar and spikelet details.'
 },
 'phragmites-australis':{
  label:'Common reed · Phragmites australis',
  clues:['Tall wetland reed with a branching, often feathery flowering head.',
         'Silky hairs along the spikelet axis between the florets (rachilla).',
         'Native North American, Gulf Coast and introduced Eurasian lineages can look similar.'],
  caution:'Species ID is not proof of an introduced lineage. Leave lineage unresolved when evidence is insufficient.'
 },
 'zizaniopsis-miliacea':{
  label:'Giant cutgrass · Zizaniopsis miliacea',
  clues:['Coarse marsh grass with broad, finely saw-edged blades.',
         'Typically a long, papery membranous ligule (about 6–20 mm).',
         'Separate male and female one-flowered spikelets on branches of the flowering head.'],
  caution:'Do not guess the sex of the spikelets from the silhouette alone; confirm anthers and stigmas.'
 }
};

/* Evidence-level technical appendix. Population-level statistics are not
   single-plant identification thresholds; source papers remain linked. */
function fieldAdvancedReedNotes(sp){
 if(sp.id==='arundo-donax'){
  const key=sp.field_id_finish_pass?.diagnostic_species_finalization_20261023?.measurable_field_key||{};
  const rows=Object.entries(key).filter(([,v])=>typeof v==='string').map(([k,v])=>
   '<div class="note-field"><b>'+esc(k.replace(/_/g,' '))+'</b><p>'+esc(v)+'</p></div>');
  if(!rows.length)return '';
  return '<details class="detail-expand field-expert-notes"><summary>Advanced Arundo anatomy: measurements, lemma hairs and rachilla</summary>'+
    '<p>Use mature organs on the same documented plant, a ruler and a hand lens; ranges are published descriptions, not measured from these photos.</p>'+
    rows.join('')+'</details>';
 }
 if(sp.id==='phragmites-australis'){
  const original=sp.three_lineage_photo_lesson_20261026?.study_means_genetic_lineages_2004;
  const measurements=original?.means_mm;
  if(!measurements)return '';
  const labels=[['americanus','Native americanus'],['introduced','Introduced Eurasian'],['gulf','Gulf Coast berlandieri']];
  const measures=[['ligule','Ligule'],['lower_glume','Lower glume'],['upper_glume','Upper glume']];
  const row=([id,label])=>'<tr><th>'+esc(label)+'</th>'+measures.map(([k])=>{
    const v=measurements[k]?.[id];
    return '<td>'+(v?esc(v.mean+' ± '+v.se+' (n='+v.n+')'):'Not reported')+'</td>';
   }).join('')+'</tr>';
  const src=String(original.public_pdf||'');
  return '<details class="detail-expand field-expert-notes"><summary>Advanced lineage evidence: measured ligules and glumes</summary>'+
   '<p><b>Genetically grouped published population means ± standard error, in millimeters.</b> These distributions overlap; this table is NOT a key for classifying a single Texas stand or deciding treatment.</p>'+
   '<div class="field-expert-table-wrap"><table><thead><tr><th>Lineage</th>'+
   measures.map(([,label])=>'<th>'+esc(label)+' (mm)</th>').join('')+'</tr></thead><tbody>'+
   labels.map(row).join('')+'</tbody></table></div>'+
   (src.startsWith('https://')?'<p><a href="'+esc(src)+'" target="_blank" rel="noopener noreferrer">Original genetically grouped measurements ↗</a></p>':'')+
   '<p><b>Critical trap:</b> Do not measure the longer basal sterile-floret lemma as an upper glume. For Gulf coast and introduced reeds, consider older culm surface, age-matched sheath clasping, independent specimens and genetic testing when needed.</p></details>';
 }
 if(sp.id==='zizaniopsis-miliacea'){
  const key=sp.field_id_finish_pass?.measured_reproductive_key_20261023;
  const rows=Array.isArray(key?.measured_diagnostic_key)?key.measured_diagnostic_key:[];
  return rows.length?'<details class="detail-expand field-expert-notes"><summary>Advanced cutgrass reproductive key and measurement limits</summary><ul>'+
   rows.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul><p><b>Research hold:</b> true long ligule and anther/stigma-confirmed male/female spikelet photographs are still missing. Never infer their sex solely from panicle position.</p></details>':'';
 }
 return '';
}
function fieldReedCompare(sp){
 const picks=reedChoices[sp.id];
 if(!Array.isArray(picks))return '';
 const available=picks.map(id=>state.records.find(r=>r.id===id)).filter(Boolean);
 if(!available.length)return '';
 const buttons=available.map(r=>
  '<button type="button" class="field-compare-option" data-compare-species="'+esc(r.id)+
  '" aria-controls="fieldReedComparisonResult" aria-pressed="false">'+
  '<strong>'+esc(r.common_name||r.scientific_name)+'</strong><small><i>'+esc(r.scientific_name)+'</i></small>'+
  '<span>Compare photos and clues →</span></button>').join('');
 const lineage=sp.id==='phragmites-australis'&&Array.isArray(sp.comparisons?.lineage_matrix)?
  '<details class="field-compare-lineages"><summary>Compare the three Phragmites lineages (advanced)</summary>'+
  '<p>These overlap. A field photograph by itself cannot establish a Texas reed as invasive.</p>'+
  sp.comparisons.lineage_matrix.slice(0,3).map(x=>
   '<article><h4>'+esc(x.lineage)+'</h4><p><b>Older sheaths:</b> '+esc(x.sheath)+
   '</p><p><b>Stem:</b> '+esc(x.stem)+'</p><p><b>Limits:</b> '+esc(x.caution)+'</p></article>').join('')+
  '</details>':'';
 return '<section class="field-compare-picker" aria-label="Compare look-alike reeds">'+
  '<div class="field-compare-heading"><h3>Compare look-alikes</h3>'+
  '<p>Pick a plant to see it next to this one. Look at the leaf junction and flowering structures, not just the plume.</p></div>'+
  '<div class="field-compare-options" role="group" aria-label="Which look-alike?">'+buttons+'</div>'+
  '<div id="fieldReedComparisonResult" class="field-compare-result" aria-live="polite">'+
  '<p class="field-compare-empty">Choose a look-alike above to see side-by-side photographs and distinguishing clues.</p></div>'+
  lineage+'</section>';
}
async function compareReeds(otherId){
 const currentId=state.selected;
 const own=state.records.find(x=>x.id===currentId);
 const other=state.records.find(x=>x.id===otherId);
 if(!own||!other||!reedChoices[currentId]?.includes(otherId))return;
 const target=dialog.querySelector('#fieldReedComparisonResult');
 if(!target)return;
 target.innerHTML='<p>Loading source-reviewed photos and field clues…</p>';
 try{
  const get=async entry=>{
   let sp=state.cache.get(entry.id);
   if(!sp){const r=await fetch(safePath(entry.path),{cache:'no-store'});if(!r.ok)throw Error('Plant record not available');
    sp=await r.json();state.cache.set(entry.id,sp);}
   return sp;
  };
  const pair=await Promise.all([get(own),get(other)]);
  if(state.selected!==currentId||!dialog.open)return;
  const photoCard=(sp,entry)=>{
   const first=sp.beginner_learning_path?.hero_photo_file||sp.images?.[0]?.file;
   const item=(sp.images||[]).find(x=>x.file===first);
   const parent=entry.path.slice(0,entry.path.lastIndexOf('/')+1);
   const image=item?safePath(parent+item.file):'';
   const source=item&&/^https:\/\//.test(item.source_page||'')?
     '<a href="'+esc(item.source_page)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':'';
   const clues=reedComparisonCues[sp.id];
   return '<article class="field-compare-side"><h4>'+esc(clues.label)+'</h4>'+
    (image?'<img loading="lazy" src="'+esc(image)+'" alt="'+esc(clues.label)+' actual photographed growth form">':'')+
    '<p class="field-compare-credit">'+esc(item?.creator||'')+' · '+esc(item?.license||'')+' '+source+'</p>'+
    '<ul>'+clues.clues.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>'+
    '<p class="field-compare-caution"><b>Be careful:</b> '+esc(clues.caution)+'</p></article>';
  };
  const updated=dialog.querySelector('#fieldReedComparisonResult');
  if(!updated)return;
  updated.innerHTML='<div class="field-compare-sides">'+photoCard(pair[0],own)+photoCard(pair[1],other)+'</div>'+
  '<button type="button" class="open-learner field-compare-open" data-species="'+esc(otherId)+'">Open full '+
   esc(other.common_name||other.scientific_name)+' Field ID →</button>';
  dialog.querySelectorAll('[data-compare-species]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.compareSpecies===otherId)));
 }catch(err){
  const updated=dialog.querySelector('#fieldReedComparisonResult');
  if(updated)updated.innerHTML='<p>Could not load that species. Try another comparison or open its field card.</p>';
 }
}
function photosFor(sp,path){
 const list=Array.isArray(sp.images)?sp.images.slice(0,36):[];
 const parent=path.slice(0,path.lastIndexOf('/')+1);
 const panels=Array.isArray(sp.visual_comparison?.items)?sp.visual_comparison.items:[];
 const parts=list.filter(x=>x&&typeof x.file==='string'&&
  !x.file.includes('..')&&!x.file.startsWith('/')&&!x.file.includes('\\')).map(item=>{
  const canonical=parent+item.file;
  const photoPath=safePath(canonical);
  if(!photoPath)return '';
  // Match only this species' exact archived photo; never transfer arrows from look-alikes.
  const panel=panels.find(p=>p&&panelBelongsTo(sp,p)&&
   typeof p.image_url==='string'&&p.image_url===canonical);
  const valid=panel&&Array.isArray(panel.markers)?panel.markers.filter(m=>m&&
   typeof m.label==='string'&&m.label.trim()&&
   ['label_x','label_y','target_x','target_y'].every(k=>Number.isFinite(Number(m[k]))&&Number(m[k])>=0&&Number(m[k])<=100)):[];
  const arrow=valid.length?'<div class="detail-photo-overlay" aria-label="Identification arrows">'+
   '<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><marker id="field-arrowhead" markerWidth="3.4" markerHeight="3.4" refX="2.5" refY="1.7" orient="auto"><path d="M0 0 L3.4 1.7 L0 3.4 Z" fill="#f7e6a0"/></marker></defs>'+
   valid.map(m=>'<line x1="'+Number(m.label_x)+'" y1="'+Number(m.label_y)+'" x2="'+Number(m.target_x)+'" y2="'+Number(m.target_y)+'" marker-end="url(#field-arrowhead)"/>').join('')+'</svg>'+
   valid.map(m=>'<span class="detail-arrow-label" style="left:'+Number(m.label_x)+'%;top:'+Number(m.label_y)+'%">'+esc(m.label)+'</span>').join('')+'</div>':'';
  const link=/^https:\/\//.test(item.source_page||'')?'<a href="'+esc(item.source_page)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':'';
  return '<figure class="detail-photo"><div class="detail-photo-image"><img src="'+esc(photoPath)+'" loading="lazy" alt="'+esc(item.role||sp.scientific_name)+'">'+arrow+'</div>'+
   '<figcaption><span>'+esc(item.role||'Plant reference')+'</span>'+
   '<small>'+esc(item.creator||'Source credited in canonical record')+' · '+esc(item.license||'')+'</small>'+
   (valid.length?'<small class="detail-arrow-count">'+valid.length+' saved identification arrow'+(valid.length===1?'':'s')+'</small>':'')+
   link+'</figcaption></figure>';
 }).filter(Boolean);
 return parts.length?'<div class="detail-gallery" aria-label="Licensed species photographs">'+parts.join('')+'</div>':
  '<p class="no-image">No public-approved photo has been selected for this card yet.</p>';
}
function renderDetail(sp,entry){
 const beginner=!!(sp.beginner_learning_path&&Array.isArray(sp.beginner_learning_path.steps));
 const inat=window.HaysINatGallery?window.HaysINatGallery.section(sp):'';
 const number=Array.isArray(sp.images)?sp.images.length:0;
 const counter='<p class="photo-count">Publicly eligible photographs: '+number+
 (number>36?' (first 36 shown below)':'')+'</p>';
 const fullGallery=beginner?
  '<details class="detail-expand field-reed-gallery"><summary>See all '+number+
  ' archived photos and saved arrows</summary>'+counter+photosFor(sp,entry.path)+'</details>':
  counter+photosFor(sp,entry.path);
 const extended=beginner?
  '<details class="detail-expand field-reed-explore"><summary>More iNaturalist observation photos</summary>'+
  inat+'</details>':inat;
 dialog.innerHTML='<div class="dialog-inner">'+
 '<div class="detail-head"><div><p class="eyebrow">'+esc(sp.family||entry.family)+' / '+esc(sp.genus||entry.genus)+'</p>'+
 '<h2 id="fieldDetailTitle">'+esc(sp.common_name||entry.common_name||sp.scientific_name)+'</h2>'+
 '<p class="detail-latin"><i>'+esc(sp.scientific_name||entry.scientific_name)+'</i></p></div>'+
 '<button class="close" type="button" data-close aria-label="Close field card">×</button></div>'+
 (beginner?
  '<div class="detail-section field-beginner-first"><h3>First look</h3><p>'+
    esc(sp.look_here_first||entry.cue||'Start with overall growth and flowers.')+'</p></div>'+
  fieldBeginnerPath(sp,entry.path)+
  '<div class="detail-section field-fast-check"><h3>Five checks before you identify it</h3>'+
  '<ol>'+cueSteps(sp).slice(0,5).map(s=>'<li>'+esc(s)+'</li>').join('')+'</ol></div>'+
  fieldReedCompare(sp)+fieldAdvancedReedNotes(sp)+fullGallery+extended+
  '<details class="detail-expand"><summary>What evidence is still missing?</summary>'+
  (visualCoverage(sp)||'<p>Check the scientific photo limitations in the full lesson.</p>')+
  '</details>'
  :extended+fullGallery+visualCoverage(sp)+
  '<div class="detail-section lessonpart"><h3>Look here first</h3><p>'+
  esc(sp.look_here_first||entry.cue||'Start with the whole plant.')+'</p></div>'+
  '<div class="detail-section lessonpart"><h3>Field ID checklist</h3><ul>'+cues(sp)+'</ul></div>')+
 (!beginner?fieldReedCompare(sp)+fieldAdvancedReedNotes(sp):'')+
 '<p class="glossary-hint">Tap highlighted botanical terms for their meaning and anatomy photos.</p>'+
 '<details class="detail-expand lessonpart"><summary>Look-alikes and cautions</summary>'+
 (lookalikes(sp)||'<p>No verified comparison text has been entered yet.</p>')+'</details>'+
 '<details class="detail-expand lessonpart"><summary>Confirmation, cautions and what to photograph</summary>'+
 (confirmation(sp)||'<p>No additional confirmation notes have been recorded for this species yet.</p>')+'</details>'+
 '<details class="detail-expand lessonpart"><summary>More botanical details</summary>'+
 (fullMorph(sp)||'<p>Additional morphological notes have not been added yet.</p>')+'</details>'+
 '<div class="dialog-foot"><button type="button" class="close-secondary" data-close>Back to tiles</button>'+
 '<a href="./index.html?view=glossary" class="open-learner">Illustrated glossary ↗</a>'+
 '<a href="./index.html?species='+encodeURIComponent(entry.id)+'" class="open-learner">Full species lesson ↗</a></div></div>';
 if(!dialog.open)dialog.showModal();
 else dialog.scrollTop=0;
 if(window.HaysGlossary)window.HaysGlossary.enhance(dialog);
 dialog.querySelector('[data-close]').focus();
}
async function openSpecies(id,trigger){
 const entry=state.records.find(p=>p.id===id);
 if(!entry)return;
 state.selected=entry.id;
 dialog.innerHTML='<div class="loading-dialog"><button type="button" data-close aria-label="Close">×</button>'+
 '<p>Loading '+esc(memberName(entry))+' ID details…</p></div>';
 if(!dialog.open)dialog.showModal();
 else dialog.scrollTop=0;
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
 if(target.dataset.compareSpecies){compareReeds(target.dataset.compareSpecies);return;}
 if(target.dataset.species){openSpecies(target.dataset.species,target);return;}
 if(target.hasAttribute('data-more')){state.limit+=60;renderResultsOnly();return;}
 if(target.hasAttribute('data-close')){dialog.close();return;}
});
dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
dialog.addEventListener('close',()=>{state.selected=null;});
async function loadFieldGlossary(){
 if(!window.HaysGlossary)return;
 try{
  const r=await fetch('./data/learning-layer.json',{cache:'no-store'});
  if(!r.ok)throw Error('Glossary data unavailable');
  const j=await r.json();
  if(j&&j.terms)window.HaysGlossary.setTerms(j.terms);
  else window.HaysGlossary.setError('No botanical definitions found');
 }catch(e){window.HaysGlossary.setError('Glossary unavailable: '+e.message);}
 if(dialog.open&&window.HaysGlossary)window.HaysGlossary.enhance(dialog);
}
async function init(){
 render();
 loadFieldGlossary();
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
  // A verified quiz answer may deep-link back into its actual Field ID card.
  const deepId=new URLSearchParams(window.location.search).get('species');
  if(deepId&&state.records.some(r=>r.id===deepId))openSpecies(deepId);
 }catch(err){state.loading=false;root.innerHTML='<section class="error-tile"><h2>Plant library unavailable</h2><p>Could not load the published tiles. Check your connection and refresh.</p></section>';}
}
init();
})();

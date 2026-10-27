/* Compact crew Quiz: public, rights-filtered species photographs and canonical 147-term glossary only. */
(function(){
'use strict';
const root=document.getElementById('quizApp');
const state={mode:null,photos:[],terms:[],filter:'',current:null,answered:false,selected:'',correct:0,wrong:0,skipped:0,seen:{photo:new Set(),term:new Set(),reed:new Set()},reed:[],loadPhoto:false,loadTerms:false,loadReed:false,photoError:'',termError:'',reedError:''};
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const name=v=>String(v.common_name||v.scientific_name||'').trim();
const clean=v=>String(v||'').trim().toLowerCase();
const shuffle=values=>{const a=[...values];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;};
function safePhotoPath(path){
 if(typeof path!=='string'||!path.startsWith('content/taxa/')||!/\.(?:jpg|jpeg|png|webp)$/i.test(path)||
 path.includes('..')||/[?#\\<>\u0000-\u001f]/.test(path)||path.startsWith('/'))return '';
 const p=path.split('/');
 if(p.some(x=>!x||x==='.'||x==='..'))return '';
 return './'+p.map(encodeURIComponent).join('/');
}
function safeSpeciesPath(path){
 if(typeof path!=='string'||!/^content\/taxa\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+\/species\.json$/.test(path))return '';
 return './'+path.split('/').map(encodeURIComponent).join('/');
}
function photoLabel(entry){
 return [entry.thumbnail_creator,entry.thumbnail_license].map(v=>String(v||'').trim()).filter(Boolean).join(' · ');
}
function photoSource(entry){
 const source=String(entry.thumbnail_source||'');
 return /^https:\/\//i.test(source)?'<a href="'+esc(source)+'" target="_blank" rel="noopener noreferrer">Original photograph ↗</a>':'';
}
const modeReady=mode=>mode==='photo'?state.photos.length>=4:mode==='reed'?state.reed.length>=4:state.terms.length>=4;
function photoPool(){
 let pool=state.photos.filter(p=>!state.filter||p.family===state.filter);
 return pool;
}
function pickUnseen(pool,mode){
 let options=pool.filter(x=>!state.seen[mode].has(x.id));
 if(!options.length){state.seen[mode].clear();options=pool;}
 const selected=options[Math.floor(Math.random()*options.length)];
 if(selected)state.seen[mode].add(selected.id);
 return selected;
}
function photoOptions(answer){
 const taken=new Set([clean(name(answer))]);
 const results=[answer];
 const relatives=state.photos.filter(x=>x.id!==answer.id);
 const groups=[
  relatives.filter(x=>x.genus===answer.genus&&x.family===answer.family),
  relatives.filter(x=>x.family===answer.family),
  relatives
 ];
 for(const group of groups){
  for(const p of shuffle(group)){
   const label=clean(name(p));
   if(label&& !taken.has(label)){results.push(p);taken.add(label);}
   if(results.length===4)break;
  }
  if(results.length===4)break;
 }
 return shuffle(results);
}
function termOptions(answer){
 const taken=new Set([clean(answer.label)]);
 const choices=[answer];
 for(const p of shuffle(state.terms.filter(x=>x.id!==answer.id))){
  if(!taken.has(clean(p.label))){choices.push(p);taken.add(clean(p.label));}
  if(choices.length===4)break;
 }
 return shuffle(choices);
}
function nextQuestion(){
 const mode=state.mode;
 if(!mode||!modeReady(mode)){state.current=null;state.answered=false;render();return;}
 const pool=mode==='photo'?photoPool():mode==='reed'?state.reed:state.terms;
 if(!pool.length){state.current=null;state.answered=false;render();return;}
 const answer=pickUnseen(pool,mode);
 if(!answer){state.current=null;render();return;}
 state.current=mode==='reed'?{...answer,choices:shuffle(answer.choices)}:{mode,answer,choices:mode==='photo'?photoOptions(answer):termOptions(answer)};
 state.answered=false;state.selected='';render();
 const title=root.querySelector('.quiz-question');if(title)title.focus();
}
function selected(choice){
 if(state.answered||!state.current)return;
 state.selected=choice||'';
 state.answered=true;
 if(!choice){state.skipped++;}
 else if(choice===state.current.answer.id){state.correct++;}
 else state.wrong++;
 render();
 const panel=root.querySelector('#quizFeedback');if(panel)panel.focus();
}
function stats(){
 const attempts=state.correct+state.wrong;
 return '<div class="quiz-stats"><span><b>'+attempts+'</b> answered</span><span><b>'+state.correct+'</b> correct</span>'+
  '<span><b>'+state.skipped+'</b> skipped</span></div>';
}
function choices(){
 const q=state.current;
 if(!q)return '';
 return '<div class="quiz-choice-grid" aria-label="Select your identification">'+q.choices.map((x,i)=>{
  const active=state.answered;
  const right=x.id===q.answer.id;
  const wrong=state.selected===x.id&&!right;
  const klass=active?(right?' is-correct':wrong?' is-wrong':' is-dimmed'):'';
  return '<button class="quiz-choice'+klass+'" type="button" data-answer="'+esc(x.id)+'"'+(active?' disabled':'')+'>'+
   '<span class="quiz-choice-index">'+String.fromCharCode(65+i)+'</span>'+
   '<span class="quiz-choice-name">'+esc(x.label||name(x))+'</span>'+
   (active&&right?'<span aria-hidden="true">✓</span>':active&&wrong?'<span aria-hidden="true">×</span>':'')+'</button>';
 }).join('')+'</div>';
}
function answerDetails(){
 const q=state.current,a=q.answer;
 let msg=!state.selected?'Answer shown for study.':state.selected===a.id?'You identified it correctly.':'Compare the correct answer with your selection.';
 let details='';
 if(q.mode==='reed'){
  const picked=q.choices.find(x=>x.id===state.selected);
  details='<div class="quiz-reveal-facts"><p class="eyebrow">Why this answer fits</p>'+
   '<h3>'+esc(a.label)+'</h3>'+
   (picked?'<p class="quiz-explanation"><b>Your choice:</b> '+esc(picked.feedback)+'</p>':'')+
   '<p>'+esc(q.explanation||'Compare several structures before confirming the plant.')+'</p>'+
   (q.photo?.thumbnail_source?'<a href="'+esc(q.photo.thumbnail_source)+
    '" target="_blank" rel="noopener noreferrer">Original photograph ↗</a>':'')+
   '<p class="quiz-study-links"><a href="./field-id.html?species='+encodeURIComponent(q.study)+
    '">Review this plant in Field ID ↗</a> · '+
   '<a href="./index.html?species='+encodeURIComponent(q.study)+
    '">Open the full Learner ↗</a></p></div>';
 }else if(q.mode==='photo'){
  details='<div class="quiz-reveal-facts"><p class="eyebrow">Correct identification</p><h3>'+
   esc(a.common_name||a.scientific_name)+'</h3><p><i>'+esc(a.scientific_name)+'</i> · '+esc(a.family)+'</p>'+
   (a.cue?'<p class="quiz-cue"><b>Look here first:</b> '+esc(a.cue)+'</p>':'')+
   photoSource(a)+'<div class="quiz-study-links"><a href="./field-id.html?species='+encodeURIComponent(a.id)+'">Open Field ID ↗</a> · '+
   '<a href="./index.html?species='+encodeURIComponent(a.id)+'">Study the full species lesson ↗</a></div></div>';
 }else{
  const t=a.source;
  details='<div class="quiz-reveal-facts"><p class="eyebrow">Botanical definition</p><h3>'+esc(t.term)+'</h3>'+
   (t.pronunciation?'<p><b>Pronunciation:</b> '+esc(t.pronunciation)+'</p>':'')+
   (t.where?'<p><b>Where to look:</b> '+esc(t.where)+'</p>':'')+
   (t.why?'<p><b>Why it matters:</b> '+esc(t.why)+'</p>':'')+
   (window.HaysGlossaryMedia?window.HaysGlossaryMedia.photoMarkup(a.id,t,true):'')+
   '<a href="./index.html?view=glossary">Open illustrated glossary ↗</a></div>';
 }
 return '<section id="quizFeedback" tabindex="-1" role="status" class="quiz-feedback"><div class="quiz-feedback-top">'+
 '<b>'+esc(msg)+'</b></div>'+details+'</section>';
}
function quizCard(){
 if(!state.current){
  return '<section class="quiz-panel"><h2>'+(
   state.mode==='photo'?'No photo questions available.':state.mode==='reed'?'Reed comparison questions unavailable.':'No term questions available.')+
   '</h2><p>Choose a different family or return to the practice choices.</p>'+
   '<button class="quiz-button" data-home>Choose a quiz</button></section>';
 }
 const q=state.current;
 const img=q.mode==='photo'?safePhotoPath(q.answer.thumbnail):q.mode==='reed'?safePhotoPath(q.photo?.thumbnail):'';
 const photo=img?'<div class="quiz-photo-stage"><img src="'+esc(img)+'" alt="Source-identified field photograph for this question" decoding="async" loading="eager"></div>'+
  '<div class="quiz-photo-attribution">'+esc(photoLabel(q.mode==='reed'?q.photo:q.answer))+'</div>':'';
 const prompt=q.mode==='photo'?'Which plant is pictured?':q.mode==='reed'?q.question:'Which botanical term matches this description?';
 const content=(q.mode==='photo'||q.mode==='reed')?photo:'<blockquote class="quiz-term-prompt">'+esc(q.answer.source.plain)+'</blockquote>';
 return '<div class="quiz-practice">'+
  '<div class="quiz-back"><button data-home class="quiz-link">← Choose practice</button><span>'+esc(q.mode==='photo'?'Photo identification':q.mode==='reed'?'Reed look-alikes':'Botanical terminology')+'</span></div>'+
  stats()+
  (q.mode==='photo'?familySelector():'')+
  '<section class="quiz-panel"><div class="quiz-kicker">Identify before revealing</div>'+
  '<h2 class="quiz-question" tabindex="-1">'+esc(prompt)+'</h2>'+content+choices()+
  (state.answered?answerDetails():'<p class="quiz-hint">Choose an answer, or reveal it to study the plant.</p>')+
  '<div class="quiz-actions">'+(state.answered?
   '<button class="quiz-button" data-next>Next question →</button>':
   '<button class="quiz-outline" data-skip>Reveal answer</button>')+
  '</div></section></div>';
}
function familySelector(){
 const counts=new Map();
 for(const p of state.photos)counts.set(p.family,(counts.get(p.family)||0)+1);
 const names=[...counts.keys()].filter(Boolean).sort((a,b)=>a.localeCompare(b));
 return '<div class="quiz-family-select"><label for="quizFamily">Practice a plant family</label>'+
 '<select id="quizFamily"><option value="">All families ('+state.photos.length+' photos)</option>'+
 names.map(n=>'<option value="'+esc(n)+'"'+(n===state.filter?' selected':'')+'>'+
  esc(n)+' ('+counts.get(n)+')</option>').join('')+'</select></div>';
}
function home(){
 const havePhotos=modeReady('photo'),haveTerms=modeReady('term'),haveReeds=modeReady('reed');
 return '<section class="quiz-hero"><p class="eyebrow">Crew learning • practice mode</p><h1>Quiz yourself.</h1>'+
 '<p>Short, photo-led practice using the same botanical library as Field ID. Tap a tile to begin, then reveal an answer and move to the next plant.</p></section>'+
 '<div class="quiz-mode-grid">'+
 '<button type="button" class="quiz-mode-tile" data-mode="photo"'+(!havePhotos?' disabled':'')+'>'+
  '<div class="quiz-mode-icon" aria-hidden="true">✳</div><div><span class="quiz-mode-caption">Visual ID</span>'+
  '<h2>Identify the plant</h2><p>Licensed photos, four choices, instant explanations.</p>'+
  '<span class="quiz-mode-action">'+(state.loadPhoto?'Loading photo library…':havePhotos?state.photos.length+' photo-ready species →': 'Photo library unavailable')+'</span></div></button>'+
 '<button type="button" class="quiz-mode-tile" data-mode="term"'+(!haveTerms?' disabled':'')+'>'+
  '<div class="quiz-mode-icon" aria-hidden="true">≋</div><div><span class="quiz-mode-caption">Botanical language</span>'+
  '<h2>Learn the terms</h2><p>Practice plant structures and see the existing glossary photos after each answer.</p>'+
  '<span class="quiz-mode-action">'+(state.loadTerms?'Loading terms…':haveTerms?state.terms.length+' terms →':'Glossary unavailable')+'</span></div></button>'+
 '<button type="button" class="quiz-mode-tile quiz-reed-mode" data-mode="reed"'+(!haveReeds?' disabled':'')+'>'+
  '<div class="quiz-mode-icon" aria-hidden="true">〰</div><div><span class="quiz-mode-caption">Look-alike learning</span>'+
  '<h2>Reed field challenge</h2><p>Compare giant reed, common reed and giant cutgrass through sourced photos and diagnostic structures. Learn why Phragmites lineage needs caution.</p>'+
  '<span class="quiz-mode-action">'+(state.loadReed?'Loading reed lessons…':haveReeds?state.reed.length+' guided questions →':'Reed lesson unavailable')+'</span></div></button>'+
 '</div>'+stats()+
 ((state.photoError||state.termError||state.reedError)?'<p class="quiz-load-note" role="status">'+esc([state.photoError,state.termError,state.reedError].filter(Boolean).join(' · '))+'</p>':'')+
 '<div class="quiz-footer">Prefer the original quiz workflow? <a href="./quiz-classic.html">Classic Quiz ↗</a>'+
 ' · <a href="./field-id.html">Field ID ↗</a></div>';
}
function render(){
 if(!root)return;
 root.innerHTML=state.mode?quizCard():home();
 if(window.HaysGlossaryMedia&&state.answered&&state.mode==='term')window.HaysGlossaryMedia.hydrate(root);
}
function setMode(mode){
 if(!['photo','term','reed'].includes(mode)||!modeReady(mode))return;
 state.mode=mode;state.filter='';nextQuestion();
}
root.addEventListener('click',e=>{
 const el=e.target.closest('button');if(!el)return;
 if(el.hasAttribute('data-home')){state.mode=null;state.current=null;state.answered=false;render();return;}
 if(el.dataset.mode){setMode(el.dataset.mode);return;}
 if(el.hasAttribute('data-answer')){selected(el.dataset.answer);return;}
 if(el.hasAttribute('data-skip')){selected('');return;}
 if(el.hasAttribute('data-next')){nextQuestion();}
});
root.addEventListener('change',e=>{
 if(e.target.id==='quizFamily'){state.filter=e.target.value;state.seen.photo.clear();nextQuestion();}
});
async function init(){
 state.loadPhoto=true;state.loadTerms=true;state.loadReed=true;render();
 const tasks=await Promise.allSettled([
  fetch('./data/field-id-index.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Photo index unavailable');return r.json();}),
  fetch('./data/learning-layer.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Glossary unavailable');return r.json();})
 ]);
 if(tasks[0].status==='fulfilled'&&Array.isArray(tasks[0].value.species)){
  const unique=new Set();
  state.photos=tasks[0].value.species.filter(p=>{
   if(!p||!p.id||!p.thumbnail||!safePhotoPath(p.thumbnail)||!name(p))return false;
   const label=clean(name(p));
   if(unique.has(label))return false;
   unique.add(label);return true;
  }).map(p=>({...p,label:name(p)}));
 }else state.photoError='Photo practice needs the published Field ID photo index.';
 if(tasks[1].status==='fulfilled'&&tasks[1].value.terms){
  state.terms=Object.entries(tasks[1].value.terms).filter(([id,t])=>
    t&&typeof t.term==='string'&&t.term.trim()&&typeof t.plain==='string'&&t.plain.trim()&&
    !clean(t.plain).includes(clean(t.term))
  ).map(([id,t])=>({id,label:t.term,source:t}));
 }else state.termError='Term practice needs the published glossary.';
 if(tasks[0].status==='fulfilled'&&Array.isArray(tasks[0].value.species)&&window.HaysReedQuiz){
  const needed=window.HaysReedQuiz.requiredSpecies||[];
  try{
   const entries=needed.map(id=>tasks[0].value.species.find(p=>p.id===id));
   if(entries.some(x=>!x||!safeSpeciesPath(x.path)))throw Error('Required reed species missing from published library');
   const species=await Promise.all(entries.map(async x=>{
     const r=await fetch(safeSpeciesPath(x.path),{cache:'no-store'});
     if(!r.ok)throw Error('Reed source record unavailable');
     return r.json();
   }));
   const lookup=Object.fromEntries(species.map(d=>[d.id,d]));
   state.reed=window.HaysReedQuiz.build(lookup);
   if(state.reed.length<4)throw Error('Insufficient credited reed photos in published site');
  }catch(e){state.reed=[];state.reedError='Reed quiz photos unavailable in this release.';}
 }else state.reedError='Reed quiz requires the current published Field ID library.';
 state.loadPhoto=false;state.loadTerms=false;state.loadReed=false;render();
}
init();
})();

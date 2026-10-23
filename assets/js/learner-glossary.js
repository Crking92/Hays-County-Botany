/* Canonical learning-layer terms, not duplicate botanical definitions. */
(function(){
'use strict';
let terms=new Map(), aliases=new Map(), matcher=null, popup=null, focused=null, error='';
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v||'').toLowerCase().trim().replace(/[\s-]+/g,' ');
function setTerms(dict){
 terms=new Map();aliases=new Map();error='';
 for(const [key,item] of Object.entries(dict||{})){
  if(!item||!item.term||!item.plain)continue;
  terms.set(key,item);
  for(const raw of [item.term,...(Array.isArray(item.aliases)?item.aliases:[])]){
   const val=String(raw||'').trim();
   if(!/^[a-z][a-z -]*$/i.test(val)||val.length<4||val.length>55)continue;
   const name=norm(val);if(!aliases.has(name))aliases.set(name,key);
  }
 }
 const parts=[...aliases.keys()].sort((a,b)=>b.length-a.length).map(v=>v.split(' ').map(word=>word.replace(/[^a-z0-9]/g,c=>'\\'+c)).join('[\\s-]+'));
 matcher=parts.length?new RegExp('\\b(?:'+parts.join('|')+')\\b','gi'):null;
}
function setError(e){error=String(e||'Glossary could not load');}
function ensurePopup(){
 if(popup)return popup;
 popup=document.createElement('div');popup.className='term-dialog-backdrop';popup.hidden=true;
 popup.innerHTML='<section class="term-dialog" role="dialog" aria-modal="true" aria-labelledby="termDialogTitle" tabindex="-1">'+
 '<button class="term-dialog-close" type="button" data-glossary-close aria-label="Close definition">×</button><div id="termDialogContents"></div></section>';
 document.body.appendChild(popup);return popup;
}
function show(key,from){
 const v=terms.get(key);if(!v)return;
 focused=from||document.activeElement;
 const overlay=ensurePopup();
 const detail=(field,title)=>v[field]?'<div class="term-dialog-field"><h3>'+title+'</h3><p>'+esc(v[field])+'</p></div>':'';
 overlay.querySelector('#termDialogContents').innerHTML=
  '<div class="stepbar">Botanical glossary</div><h2 id="termDialogTitle">'+esc(v.term)+'</h2>'+
  (v.pronunciation?'<p class="term-say">Say it: '+esc(v.pronunciation)+'</p>':'')+
  '<p class="term-plain">'+esc(v.plain)+'</p>'+ (window.HaysGlossaryMedia?window.HaysGlossaryMedia.photoMarkup(key,v,true):'')+detail('where','Where to look')+
  detail('why','Why it matters for identification')+detail('formal','Botanical definition')+
  (Array.isArray(v.aliases)&&v.aliases.length?'<p class="term-aliases"><b>Also called:</b> '+v.aliases.map(esc).join(', ')+'</p>':'')+
  '<button class="button secondary" type="button" data-glossary-close>Back to lesson</button>';
 if(window.HaysGlossaryMedia)window.HaysGlossaryMedia.hydrate(overlay);
 overlay.hidden=false;document.body.classList.add('term-dialog-open');
 overlay.querySelector('button').focus();
}
function close(){
 if(!popup||popup.hidden)return;
 popup.hidden=true;document.body.classList.remove('term-dialog-open');
 if(focused&&focused.isConnected&&focused.focus)focused.focus();
 focused=null;
}
function page(){
 const sorted=[...terms].sort((a,b)=>a[1].term.localeCompare(b[1].term));
 const cards=sorted.map(([key,v])=>
  '<button type="button" class="glossary-card" data-glossary-term="'+esc(key)+'" data-glossary-search="'+esc(norm([v.term,...(v.aliases||[]),v.plain].join(' ')))+'">'+
  (window.HaysGlossaryMedia?window.HaysGlossaryMedia.photoMarkup(key,v,false):'')+
  '<strong>'+esc(v.term)+'</strong><span>'+esc(v.plain)+'</span></button>').join('');
 return '<div class="crumb"><button data-view="home">Learner home</button> › Glossary</div>'+
  '<section class="hero"><div class="kicker">Learn the language of plants</div><h1>Botanical glossary.</h1>'+
  '<p>Learn what each structure means, where to find it and why it helps with identification. Tap linked terms in species lessons to see these definitions without leaving the page.</p></section>'+
  '<section class="panel glossary-page"><label for="glossarySearch"><b>Find a botanical term</b></label>'+
  '<input class="search" type="search" id="glossarySearch" placeholder="Try ligule, phyllary, cyathium, or node…" autocomplete="off">'+
  '<p class="mini" id="glossaryCount" role="status" aria-live="polite">'+(sorted.length?sorted.length+' terms from your existing glossary':esc(error||'Loading glossary…'))+'</p>'+
  '<div class="glossary-grid" id="glossaryCards">'+(cards||'<p class="info">No glossary terms are available yet.</p>')+'</div></section>';
}
function filter(value){
 const list=document.getElementById('glossaryCards');if(!list)return;
 let shown=0;const q=norm(value);
 list.querySelectorAll('[data-glossary-term]').forEach(el=>{
  const ok=!q||el.dataset.glossarySearch.includes(q);el.hidden=!ok;if(ok)shown++;
 });
 const count=document.getElementById('glossaryCount');
 if(count)count.textContent=shown+' of '+terms.size+' terms'+(q?' matching your search':'');
}
function enhance(root){
 if(!root||!matcher)return;
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{
  acceptNode(node){
   const el=node.parentElement;
   if(!el||!node.nodeValue||!/[A-Za-z]{4}/.test(node.nodeValue))return NodeFilter.FILTER_REJECT;
   if(!el.closest('.lessonpart,.lessonhead,.overview,.course,.panel'))return NodeFilter.FILTER_REJECT;
   if(el.closest('.glossary-page,a,button,pre,code,summary,input,select,textarea,svg,.overlay,.figcap,.photostrip,.result,[data-glossary-term]'))return NodeFilter.FILTER_REJECT;
   return NodeFilter.FILTER_ACCEPT;
  }
 });
 const candidates=[];while(walker.nextNode())candidates.push(walker.currentNode);
 const scoped=new WeakMap();let count=0;
 for(const node of candidates){
  if(count>=160)break;
  const parent=node.parentElement;
  const section=parent&&parent.closest('.lessonpart,.lessonhead,.overview,.course,.panel');
  if(!section)continue;
  let used=scoped.get(section);if(!used){used=new Set();scoped.set(section,used);}
  const raw=node.nodeValue;matcher.lastIndex=0;
  const matches=[...raw.matchAll(matcher)];
  if(!matches.length)continue;
  const frag=document.createDocumentFragment();
  let offset=0,changed=false;
  for(const hit of matches){
   const key=aliases.get(norm(hit[0]));
   if(!key||used.has(key)||hit.index<offset||count>=160)continue;
   frag.appendChild(document.createTextNode(raw.slice(offset,hit.index)));
   const button=document.createElement('button');button.type='button';
   button.className='glossary-term-link';button.dataset.glossaryTerm=key;
   button.title='Define '+terms.get(key).term;
   button.setAttribute('aria-label','Define '+hit[0]);button.textContent=hit[0];
   frag.appendChild(button);offset=hit.index+hit[0].length;
   used.add(key);changed=true;count++;
  }
  if(changed){frag.appendChild(document.createTextNode(raw.slice(offset)));parent.replaceChild(frag,node);}
 }
}
document.addEventListener('click',event=>{
 if(event.target.closest('[data-glossary-close]')){close();return;}
 const link=event.target.closest('[data-glossary-term]');
 if(link){show(link.dataset.glossaryTerm,link);return;}
 if(popup&&!popup.hidden&&event.target===popup)close();
});
document.addEventListener('input',event=>{if(event.target.id==='glossarySearch')filter(event.target.value);});
document.addEventListener('keydown',event=>{
 if(!popup||popup.hidden)return;
 if(event.key==='Escape'){event.preventDefault();close();return;}
 if(event.key==='Tab'){
  const buttons=popup.querySelectorAll('button,a[href]');if(!buttons.length)return;
  const first=buttons[0],last=buttons[buttons.length-1];
  if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
  else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
 }
});
window.HaysGlossary={setTerms,setError,page,enhance,show,close};
})();

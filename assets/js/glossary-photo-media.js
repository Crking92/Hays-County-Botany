/* Restore illustrations and vetted photo references from canonical learning-layer terms.
 * This module never changes taxonomy, photographs, annotations or photo source records.
 * Do not display unknown/ND/copyrighted Commons media without checking its license.
 */
(function(){
'use strict';
const html=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const approvedCredit=text=>/\bCC\s*(?:0|BY(?:-SA)?)\b|public[\s-]*domain|PD[\s-]*mark/i.test(String(text||''))&&!/\b(?:NC|ND|all rights reserved)\b/i.test(String(text||''));
const imageCache=new Map();
const sourceFile=link=>{
 if(typeof link!=='string'||!/^https:\/\/commons\.wikimedia\.org\/wiki\/File:/i.test(link))return '';
 try {return decodeURIComponent(link.split('/wiki/File:')[1].split('#')[0].split('?')[0]).replace(/_/g,' ');}
 catch(e){return '';}
};
const sourceLink=p=>{
 const u=p&&p.source_page;
 return sourceFile(u)?u:'';
};
const fileURL=(file,width)=>{
 if(!file)return '';
 // Commons Special:FilePath resolves the photographed file, not the File: page.
 return 'https://commons.wikimedia.org/wiki/Special:FilePath/'+encodeURIComponent(file.replace(/ /g,'_'))+'?width='+width;
};
const localURL=p=>{
 const url=p&&p.image_url;
 if(typeof url!=='string'||url.includes('..')||/[?#]/.test(url))return '';
 if(/^assets\/diagrams\/[a-z0-9_-]+\.svg$/i.test(url))return './'+url;
 if(/^content\/taxa\/[a-z0-9_/-]+\.(?:jpg|jpeg|png|webp)$/i.test(url))return './'+url;
 return '';
};
function licensing(p){
 if(!p)return false;
 if(localURL(p)&&p.media_type==='diagram'&&/Hays Botany learner diagram/i.test(p.credit||''))return true;
 return approvedCredit(p.credit);
}
function photoMarkup(key,item,detail){
 const p=item&&item.real_photo||{};
 const diagram=item&&item.visual;
 let file='',credit=p.credit||'';
 const external=sourceLink(p);
 let src=localURL(p);
 if(!src&&external&&licensing(p))src=fileURL(sourceFile(external),detail?940:420);
 // Prefer the existing purpose-made learner visual where an original photo
 // has no independently approved image URL.
 if(!src&&typeof diagram==='string'&&/^assets\/diagrams\/[a-z0-9_-]+\.svg$/i.test(diagram))src='./'+diagram;
 const wrapper=detail?'glossary-media glossary-media-detail':'glossary-media glossary-media-tile';
 const image=src?'<img class="glossary-media-img" src="'+html(src)+'" alt="'+html(p.alt||p.label||item.term)+'" loading="'+(detail?'eager':'lazy')+'" decoding="async">':
  '<span class="glossary-photo-placeholder">Image source available</span>';
 const link=external?'<a href="'+html(external)+'" target="_blank" rel="noopener noreferrer">Original photo ↗</a>':'';
 const annotations=detail&&Array.isArray(p.annotations)?p.annotations.filter(a=>a&&
  ['x','y','label_x','label_y'].every(v=>Number.isFinite(Number(a[v]))&&Number(a[v])>=0&&Number(a[v])<=100)&&
  typeof a.label==='string'&&a.label.length<=80):[];
 const lines=annotations.length?'<svg class="glossary-photo-arrows" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'+
  '<defs><marker id="glossaryArrowTip" markerWidth="5" markerHeight="5" refX="3" refY="2" orient="auto"><path d="M0 0 L4 2 L0 4 Z" fill="#f4c55c"/></marker></defs>'+
  annotations.map(a=>'<line x1="'+Number(a.label_x)+'" y1="'+Number(a.label_y)+'" x2="'+Number(a.x)+'" y2="'+Number(a.y)+'" marker-end="url(#glossaryArrowTip)"/>').join('')+'</svg>'+
  annotations.map(a=>'<span class="glossary-photo-arrowlabel" style="left:'+Number(a.label_x)+'%;top:'+Number(a.label_y)+'%">'+html(a.label)+'</span>').join(''):'';
 return '<figure class="'+wrapper+'" data-glossary-photo-key="'+html(key)+'"'+(!src&&external?' data-glossary-resolve="'+html(external)+'"':'')+'>'+
  '<div class="glossary-photo-stage">'+image+
  (detail?'<div class="glossary-photo-pointer-layer" data-glossary-pointers hidden>'+lines+'</div>':'')+
  '</div>'+
  (detail?'<figcaption class="glossary-photo-caption">'+
   '<strong>'+html(p.label||item.term+' reference')+'</strong>'+
   (p.focus?'<p>'+html(p.focus)+'</p>':'')+
   (credit?'<small>'+html(credit)+'</small>':'')+
   (link?'<div class="glossary-source-link">'+link+'</div>':'')+
   (annotations.length?'<button type="button" class="button secondary glossary-pointers-toggle" data-glossary-pointers-toggle aria-expanded="false">Show draft anatomy arrows</button><small class="glossary-photo-review-note">Existing arrow positions are supplied by the glossary record and still need individual photo-by-photo visual verification.</small>':'')+
   '</figcaption>':'')+'</figure>';
}
async function verifyUnknown(source){
 const file=sourceFile(source);
 if(!file)return '';
 const query='https://commons.wikimedia.org/w/api.php?'+new URLSearchParams({
  action:'query',prop:'imageinfo',iiprop:'url|extmetadata',iiurlwidth:'900',
  titles:'File:'+file,format:'json',formatversion:'2',origin:'*'}).toString();
 const res=await fetch(query,{mode:'cors'});
 if(!res.ok)throw Error('Commons unavailable');
 const json=await res.json();
 const info=json&&json.query&&json.query.pages&&json.query.pages[0]&&json.query.pages[0].imageinfo&&json.query.pages[0].imageinfo[0];
 const metadata=info&&info.extmetadata||{};
 const license=String(metadata.LicenseShortName&&metadata.LicenseShortName.value||'').trim();
 const url=String(metadata.LicenseUrl&&metadata.LicenseUrl.value||'');
 // Derivative images may use Commons only when the file's actual license allows reuse.
 const approved=/^CC(?:0| BY(?:-SA)?)(?:[ \d.]|$)/i.test(license)||
   /public domain|pd-old|pd-self|pd-usa/i.test(license)||
   /^https:\/\/creativecommons\.org\/(?:licenses\/by(?:-sa)?\/|publicdomain\/zero\/|publicdomain\/mark\/)/i.test(url);
 if(!approved||/BY-NC|BY-ND|GFDL|all rights reserved/i.test(license))return '';
 const remote=String(info&&info.thumburl||info&&info.url||'');
 if(!/^https:\/\//i.test(remote))return '';
 const u=new URL(remote);
 if(!/(?:^|\.)wikimedia\.org$/.test(u.hostname))return '';
 return remote;
}
async function resolve(figure){
 const source=figure.getAttribute('data-glossary-resolve');
 if(!source)return;
 figure.removeAttribute('data-glossary-resolve');
 let result=imageCache.get(source);
 if(!result){
  result=verifyUnknown(source).catch(()=> '');
  imageCache.set(source,result);
 }
 const src=await result;
 if(!figure.isConnected||!src)return;
 const stage=figure.querySelector('.glossary-photo-stage');
 if(!stage)return;
 let img=stage.querySelector('img');
 if(!img){img=document.createElement('img');img.className='glossary-media-img';img.alt='Botanical glossary reference photo';img.loading='lazy';stage.replaceChildren(img);}
 img.src=src;
}
function hydrate(root){
 if(!root)return;
 const targets=Array.from(root.querySelectorAll('[data-glossary-resolve]'));
 if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
   for(const entry of entries)if(entry.isIntersecting){observer.unobserve(entry.target);resolve(entry.target);}
  },{rootMargin:'350px'});
  for(const item of targets)observer.observe(item);
 }else{
  targets.slice(0,25).forEach(resolve);
 }
 root.querySelectorAll('.glossary-media-img').forEach(img=>{
  img.addEventListener('error',()=>{
   const figure=img.closest('.glossary-media');
   if(!figure||!img.isConnected)return;
   img.replaceWith(Object.assign(document.createElement('span'),{
    className:'glossary-photo-placeholder',textContent:'Photo not available — open original source'
   }));
  },{once:true});
 });
}
document.addEventListener('click',event=>{
 const b=event.target.closest('[data-glossary-pointers-toggle]');
 if(!b)return;
 const figure=b.closest('.glossary-media');
 if(!figure)return;
 const layer=figure.querySelector('[data-glossary-pointers]');
 if(!layer)return;
 const open=layer.hidden;
 layer.hidden=!open;
 b.setAttribute('aria-expanded',String(open));
 b.textContent=open?'Hide draft anatomy arrows':'Show draft anatomy arrows';
});
window.HaysGlossaryMedia={photoMarkup,hydrate,licensing,sourceFile,verifyUnknown};
})();

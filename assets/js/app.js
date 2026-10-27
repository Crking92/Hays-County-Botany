const state = {
  project: null,
  learning: null,
  manifestSpecies: [],
  species: [],
  speciesById: new Map(),
  familyCache: new Map(),
  lessonIndex: {families: [], genera: []},
  genusCache: new Map(),
  difficulty: readLocal("hays-botany-difficulty") || "terms",
  quizMode: readLocal("hays-botany-quiz") === "true",
  quizRevealed: false,
  view: "home",
  selectedSpeciesId: null,
  selectedFamily: null,
  selectedGenusFamily: null,
  selectedGenus: null,
  compareA: null,
  compareB: null,
  browseFamily: "",
  browseGenus: "",
  photoIndex: {},
  glossaryQuery: "",
  termDrillId: null,
  termDrillRevealed: false,
  termDrillPool: null,
  approvals: null,
  approvalRevision: null,
  approvalsWriteEnabled: false,
  approvalsError: "",
  approvalsFilter: "action",
  approvalsBusy: null,
  approvalArtifacts: {},
  approvalDraftCache: new Map(),
  approvalPhotoCache: new Map()
};

const els = {
  app: document.getElementById("app"),
  modal: document.getElementById("modalRoot"),
  search: document.getElementById("globalSearch"),
  results: document.getElementById("searchResults"),
  clear: document.getElementById("clearSearch"),
  quiz: document.getElementById("quizToggle")
};

function readLocal(key){ try { return localStorage.getItem(key); } catch(e) { return null; } }
function writeLocal(key,value){ try { localStorage.setItem(key,value); } catch(e) {} }
function esc(value){
  return String(value == null ? "" : value).replace(/[&<>"']/g,function(ch){
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[ch];
  });
}
function titleCase(value){
  return String(value || "").replaceAll("_"," ").replace(/\b\w/g,function(c){ return c.toUpperCase(); });
}
function norm(value){ return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g," ").trim(); }

async function loadJSON(path){
  const r = await fetch(path,{cache:"no-store"});
  if(!r.ok) throw new Error(r.status + " " + path);
  return r.json();
}
function scientificName(sp){
  if(sp.scientific_name) return sp.scientific_name;
  const bits=[sp.genus,sp.species].filter(Boolean);
  if(sp.subspecies) bits.push("subsp.",sp.subspecies);
  if(sp.variety) bits.push("var.",sp.variety);
  return bits.join(" ") || sp.accepted_name || sp.id || "Unnamed taxon";
}
function commonName(sp){ return sp.common_name || sp.common_group || ""; }
function speciesBase(sp){
  const entry=state.manifestSpecies.find(function(x){ return x.id===sp.id; });
  return entry && entry.path ? entry.path.replace(/\/species\.json$/,"") : "";
}
function imagesFor(sp){ return (Array.isArray(sp.images)?sp.images:[]).filter(function(x){ return x && x.file; }); }
/* Installed images remain canonical and unchanged. Optional licensed EXACT-SPECIES
   public external references can also be swiped in the gallery; this does not
   alter canonical image IDs or anchors used throughout family/genus lessons. */
function galleryImagesFor(sp){
  const installed=imagesFor(sp);
  const extras=Array.isArray(sp.gallery_external_refs)?sp.gallery_external_refs:[];
  return installed.concat(extras.filter(function(img){
    return img && img.gallery_species_id===sp.id &&
      typeof img.file==="string" &&
      /^https:\/\/(?:upload|thumb)\.wikimedia\.org\/wikipedia\/commons\//i.test(img.file) &&
      /^https:\/\/commons\.wikimedia\.org\/wiki\/File:/i.test(img.source_page||"") &&
      /^(?:CC BY(?:-SA)?|CC0) [0-9]/i.test(img.license||"") &&
      img.public_reuse==="yes" && !!img.creator && !!img.license_url;
  }));
}
function imagePath(sp,img){
  if(!img || !img.file) return "";
  if(/^https?:\/\//i.test(img.file)) return img.file;
  if(img.file.startsWith("content/")) return encodeURI(img.file);
  return encodeURI(speciesBase(sp)+"/"+img.file);
}
function defaultPhotoIndex(sp){
  const imgs=imagesFor(sp);
  const verified=imgs.findIndex(function(img){ return !/^https?:\/\//i.test(img.file) && Array.isArray(img.image_dimensions) && img.source_platform==="iNaturalist" && img.study_use==="yes"; });
  return verified>=0 ? verified : 0;
}
/* Image priority applies to presentation only. Canonical images[] indices remain stable
   because family lessons bind to original anchor_image_index positions. */
function galleryPhotoScore(img){
  const role=String([img.role,img.view,img.image_role].filter(Boolean).join(" ")).toLowerCase();
  const vetted=Boolean(img.visual_role_reviewed || img.diagnostic_role_verified || img.annotation_verified);
  if(vetted && (/diagnostic|leaf|venation|petiole|phyllar|involucre|bud|acorn|ligule|fruit|flower|corona|pollinia|macro|structure/.test(role))) return 120;
  if(/diagnostic/.test(role)) return 95;
  if(/verified .*(leaf|flower|macro|fruit|vegetative|phyllar)/.test(role)) return 78;
  if(/(leaf|petiole|venation|phyllar|involucre|corona|gynostegium|ligule|acorn|bud|bark|pappus|fruit|seed|macro|detail)/.test(role)&&!/^(same-observation|curated taxon)/.test(role)) return 53;
  if(/whole plant|habit|field view/.test(role)) return 16;
  return 0;
}
function galleryPhotoOrder(sp){
  const imgs=galleryImagesFor(sp), fallback=defaultPhotoIndex(sp);
  // For carefully curated beginner lessons, show a recognizable whole-plant
  // photo FIRST. The diagnostic macros follow; canonical image indices stay put.
  const firstFile=sp && sp.beginner_learning_path && sp.beginner_learning_path.hero_photo_file;
  const hero=typeof firstFile==="string" ? imgs.findIndex(function(img){return img.file===firstFile;}) : -1;
  return imgs.map(function(img,index){
    return {index,score:galleryPhotoScore(img)+(index===fallback?1:0)};
  }).sort(function(a,b){
    if(hero>=0 && a.index===hero)return -1;
    if(hero>=0 && b.index===hero)return 1;
    return b.score-a.score || a.index-b.index;
  }).map(function(x){return x.index;});
}
function firstImage(sp){ return imagesFor(sp)[defaultPhotoIndex(sp)] || null; }
function thumb(sp,cls){
  const img=firstImage(sp);
  if(img) return '<img class="'+cls+'" src="'+imagePath(sp,img)+'" alt="'+esc(scientificName(sp))+'" loading="lazy">';
  return '<div class="'+cls+' thumb-empty" aria-hidden="true">✣</div>';
}
function familyLessonExists(name){ return state.lessonIndex.families.includes(name); }
function genusLessonExists(family,genus){ return state.lessonIndex.genera.some(function(x){ return x.family===family && x.genus===genus; }); }
function familyProfile(name){ return state.learning && state.learning.family_profiles ? state.learning.family_profiles[name] : null; }
function callout(sp){ return state.learning && state.learning.species_callouts ? state.learning.species_callouts[sp.id] : null; }

function formatValue(value){
  if(Array.isArray(value)) return value.map(formatValue).join(" · ");
  if(value && typeof value==="object"){
    return Object.entries(value).map(function(pair){ return titleCase(pair[0])+": "+formatValue(pair[1]); }).join(" | ");
  }
  return String(value == null ? "" : value);
}
function countyList(sp){
  let counties=[];
  if(Array.isArray(sp.county_occurrences_target_zone)) counties=sp.county_occurrences_target_zone;
  else if(Array.isArray(sp.target_zone_range && sp.target_zone_range.confirmed_target_zone_counties)) counties=sp.target_zone_range.confirmed_target_zone_counties;
  else if(typeof sp.verified_target_counties==="string") counties=sp.verified_target_counties.split(";").map(function(x){ return x.trim(); });
  else if(Array.isArray(sp.county_occurrences_reported)) counties=sp.county_occurrences_reported;
  const allowed=(state.project && state.project.target_zone_counties) || [];
  return Array.from(new Set(counties.filter(function(x){ return allowed.includes(x); })));
}
function rangeSummary(sp){
  const counties=countyList(sp);
  const direct=sp.target_zone_range && sp.target_zone_range.meets_three_county_rule;
  const tracker=String((sp.project_inclusion && sp.project_inclusion.target_zone_status) || sp.native_range_status || "").toUpperCase();
  const role=String(sp.learner_role || "").toUpperCase();
  if(direct===true || tracker==="PASS" || sp.native_target_zone_calculated===true){
    const n=counties.length || sp.target_zone_count || (sp.target_zone_range && (sp.target_zone_range.target_zone_count_confirmed || sp.target_zone_range.target_zone_count_confirmed_minimum)) || "3+";
    return "Confirmed target-zone native · "+n+" supported counties";
  }
  if(tracker.includes("NON_NATIVE") || tracker==="COMPARISON" || role.includes("NON_NATIVE")){
    return "Learner comparison · not counted as target-zone native";
  }
  if(tracker.includes("FAIL")){
    return "Not confirmed target-zone native · learner entry retained";
  }
  if(tracker==="UNRESOLVED" || tracker==="CONFLICT" || direct===false || role.includes("UNRESOLVED")){
    return "Range unresolved · learner entry retained";
  }
  if(sp.project_inclusion && sp.project_inclusion.strict_native_filter_deferred) return "Range audit deferred · learner entry retained";
  if(counties.length) return counties.length+" supported target-zone county records · native label not finalized";
  return "Native-range label not finalized · learner entry retained";
}


// Encounter labels are intentionally independent of the deferred county-native audit.
// Only explicit, sourced learner classifications may trigger a public label.
// Range FAIL, UNRESOLVED, nonlocal status, or occurrence in Texas does not imply invasiveness.
function encounterBadge(sp){
  const inclusion=sp.project_inclusion || {};
  const role=String(sp.learner_role || inclusion.learner_role || "").toUpperCase();
  const confirmed=String(sp.invasive_status || inclusion.invasive_status || "").toUpperCase();
  if(role.includes("INVASIVE") || confirmed==="CONFIRMED_INVASIVE"){
    return '<span class="encounter-badge encounter-invasive">⚠ Invasive</span>';
  }
  if(role.includes("NON_NATIVE") || role.includes("INTRODUCED")){
    return '<span class="encounter-badge encounter-introduced">Introduced / non-native</span>';
  }
  return "";
}

function lookHereFirst(sp){
  if(typeof sp.look_here_first==="string" && sp.look_here_first.trim()) return sp.look_here_first;
  const c=callout(sp);
  if(c && c.standout) return c.standout;
  const m=sp.morphology_keys || {};
  const best=m.best_field_traits || m.high_value_field_traits;
  if(Array.isArray(best) && best.length) return formatValue(best[0]);
  const keys=["leaf_arrangement","phyllotaxy","sap_type","leaves","leaf_morphology","phyllaries","flower","heads","inflorescence","fruit","habit","growth_habit","bark","acorn"];
  for(let i=0;i<keys.length;i++) if(m[keys[i]]) return titleCase(keys[i])+": "+formatValue(m[keys[i]]);
  const first=Object.entries(m)[0];
  return first ? titleCase(first[0])+": "+formatValue(first[1]) : ((familyProfile(sp.family)||{}).look_here_first || "Start with overall architecture, then inspect reproductive structures.");
}
function fieldCues(sp,max){
  const m=sp.morphology_keys || {};
  const cues=[];
  const best=m.best_field_traits || m.high_value_field_traits;
  if(Array.isArray(best)) best.forEach(function(v){ if(v && cues.length<max) cues.push(formatValue(v)); });
  const keys=["leaf_arrangement","phyllotaxy","sap_type","leaves","leaf_morphology","phyllaries","flower","flower_color","heads","inflorescence","fruit","habit","growth_habit","bark","acorn"];
  keys.forEach(function(k){
    if(cues.length>=max || !m[k]) return;
    const value=titleCase(k)+": "+formatValue(m[k]);
    if(!cues.includes(value)) cues.push(value);
  });
  if(!cues.length) Object.entries(m).slice(0,max).forEach(function(p){ cues.push(titleCase(p[0])+": "+formatValue(p[1])); });
  return cues.slice(0,max);
}
function termMatches(entry,text){
  const hay=norm(text);
  return [entry.term].concat(entry.aliases||[]).map(norm).filter(function(x){ return x.length>=4; }).some(function(x){ return hay.includes(x); });
}
function termsForSpecies(sp,max){
  const profile=familyProfile(sp.family) || {};
  const found=[];
  function add(id){ if(state.learning.terms[id] && !found.includes(id)) found.push(id); }
  (profile.key_terms||[]).forEach(add);
  const body=JSON.stringify({morphology:sp.morphology_keys,callout:callout(sp),family:profile});
  Object.entries(state.learning.terms).forEach(function(pair){ if(termMatches(pair[1],body)) add(pair[0]); });
  return found.slice(0,max);
}
function termChip(id){
  const t=state.learning.terms[id];
  if(!t) return "";
  return '<button class="term-chip" type="button" data-term="'+esc(id)+'" title="'+esc(t.plain||"Tap to learn this word")+'"><span>'+esc(t.term)+'</span><b aria-hidden="true">?</b></button>';
}
function clueWithTerms(value){
  const raw=String(value||"");
  const entries=Object.entries((state.learning&&state.learning.terms)||{})
    .filter(function(x){return x[1]&&x[1].term&&x[1].term.length>=4;})
    .sort(function(a,b){return b[1].term.length-a[1].term.length;});
  if(!entries.length) return esc(raw);
  const ids=new Map(entries.map(function(x){return [x[1].term.toLowerCase(),x[0]];}));
  const names=entries.map(function(x){return x[1].term;});
  let result="",pos=0;
  while(pos<raw.length){
    const match=names.find(function(name){
      if(raw.slice(pos,pos+name.length).toLowerCase()!==name.toLowerCase()) return false;
      const before=pos?raw[pos-1]:"",after=raw[pos+name.length]||"";
      return !/[a-z]/i.test(before)&&!/[a-z]/i.test(after);
    });
    if(match){
      result+='<button class="inline-term" type="button" data-term="'+esc(ids.get(match.toLowerCase()))+'" title="Learn this botanical word">'+esc(raw.slice(pos,pos+match.length))+' <b aria-hidden="true">?</b></button>';
      pos+=match.length;
    }else{result+=esc(raw[pos]);pos++;}
  }
  return result;
}
function familySpecies(family){ return state.species.filter(function(sp){ return sp.family===family; }); }
function generaForFamily(family){
  const counts=new Map();
  familySpecies(family).forEach(function(sp){ counts.set(sp.genus,(counts.get(sp.genus)||0)+1); });
  return Array.from(counts.entries()).sort(function(a,b){ return a[0].localeCompare(b[0]); });
}
function familyCounts(){
  const counts=new Map();
  state.species.forEach(function(sp){ counts.set(sp.family,(counts.get(sp.family)||0)+1); });
  return counts;
}
function taxonomyLadder(family,genus,sp){
  let out='<nav class="taxonomy-ladder" aria-label="Taxonomy path">';
  out+='<button type="button" class="taxonomy-rank '+(!genus?"current":"")+'" data-family="'+esc(family)+'"><span>Family</span><strong>'+esc(family)+'</strong></button>';
  out+='<b class="taxonomy-step" aria-hidden="true">→</b>';
  if(genus) out+='<button type="button" class="taxonomy-rank '+(!sp?"current":"")+'" data-genus="'+esc(genus)+'" data-genus-family="'+esc(family)+'"><span>Genus</span><strong><i>'+esc(genus)+'</i></strong></button>';
  else out+='<div class="taxonomy-rank pending"><span>Genus</span><strong>Choose below</strong></div>';
  out+='<b class="taxonomy-step" aria-hidden="true">→</b>';
  if(sp) out+='<div class="taxonomy-rank current"><span>Species</span><strong><i>'+esc(scientificName(sp))+'</i></strong></div>';
  else out+='<div class="taxonomy-rank pending"><span>Species</span><strong>Compare or open one</strong></div>';
  return out+'</nav>';
}
function familyComparePanel(family,members){
  if(!members || members.length<2) return "";
  const opts=members.map(function(sp){ return '<option value="'+esc(sp.id)+'">'+esc(scientificName(sp))+(commonName(sp)?' — '+esc(commonName(sp)):'')+'</option>'; }).join("");
  const second=members[1] ? members[1].id : members[0].id;
  return '<section class="family-compare-panel"><div><div class="eyebrow">Compare within '+esc(family)+'</div><h2>Put two species side by side</h2><p>Start with what they share as family members, then use the differing characters to separate them.</p></div>'+
    '<div class="family-compare-controls"><label><span>Species A</span><select id="familyCompareA">'+opts+'</select></label>'+
    '<span class="compare-vs">vs</span><label><span>Species B</span><select id="familyCompareB">'+opts.replace('value="'+esc(second)+'"','value="'+esc(second)+'" selected')+'</select></label>'+
    '<button type="button" class="primary-button" data-family-compare>Compare</button></div></section>';
}
function genusSpecies(family,genus){
  return state.species.filter(function(sp){ return sp.family===family && sp.genus===genus; });
}
function genusSharedTraits(data){
  if(!data) return [];
  // Genus builders use either the older study_strategy/genus_diagnostics
  // schema or direct shared_traits; honor both without changing science.
  if(data.study_strategy && Array.isArray(data.study_strategy.shared_traits) && data.study_strategy.shared_traits.length) return data.study_strategy.shared_traits;
  if(data.shared_genus_recognition && Array.isArray(data.shared_genus_recognition.shared_traits) && data.shared_genus_recognition.shared_traits.length) return data.shared_genus_recognition.shared_traits;
  if(Array.isArray(data.shared_traits) && data.shared_traits.length) return data.shared_traits;
  if(data.shared_traits && typeof data.shared_traits==="object"){
    return Object.entries(data.shared_traits).map(function(pair){ return titleCase(pair[0])+": "+formatValue(pair[1]); });
  }
  if(data.genus_diagnostics && typeof data.genus_diagnostics==="object"){
    return Object.entries(data.genus_diagnostics).map(function(pair){ return titleCase(pair[0])+": "+formatValue(pair[1]); });
  }
  return [];
}
function genusPriorityTraits(data){
  if(!data) return [];
  if(data.study_strategy && Array.isArray(data.study_strategy.priority)) return data.study_strategy.priority;
  if(Array.isArray(data.high_value_diagnostics)) return data.high_value_diagnostics;
  if(Array.isArray(data.high_value_field_traits)) return data.high_value_field_traits;
  return [];
}
function genusQuickRows(data){
  if(!data) return [];
  const rows=data.quick_key || data.central_texas_quick_key;
  if(Array.isArray(rows)) return rows.map(function(row){ return {if:row.if||row.look_for||"",then:row.then||row.id||""}; });
  if(data.quick_comparison && typeof data.quick_comparison==="object"){
    return Object.entries(data.quick_comparison).map(function(pair){ return {if:pair[1],then:(data.name||"")+" "+pair[0]}; });
  }
  return [];
}
function genusTextComparisons(data){
  const cards=Array.isArray(data && data.comparison_cards) ? data.comparison_cards : [];
  if(!cards.length) return "";
  let out='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Similar species · real field characters</div><h2>Side-by-side identification lessons</h2><p>Start with the most reliable separating structure. Photo overlays are added only after the exact feature is verified.</p></div></div>';
  cards.forEach(function(card){
    out+='<article class="learning-card"><div class="eyebrow">Look here first</div><h3>'+esc(card.title||"Species comparison")+'</h3><p>'+esc(card.look_here_first||"")+'</p>';
    if(Array.isArray(card.field_matrix) && card.field_matrix.length){
      out+='<ul class="trait-list">';
      card.field_matrix.forEach(function(row){
        const differences=Object.entries(row).filter(function(pair){ return pair[0]!=="character" && pair[0]!=="strength"; });
        out+='<li><b>'+esc(row.character||"Character")+'</b> — '+differences.map(function(pair){ return '<strong>'+esc(titleCase(pair[0]))+':</strong> '+esc(formatValue(pair[1])); }).join(' · ');
        if(row.strength) out+=' <small>('+esc(row.strength)+')</small>';
        out+='</li>';
      });
      out+='</ul>';
    }
    if(card.caution || card.ecological_warning) out+='<p class="diagnostic-overlay-note">'+esc(card.caution||card.ecological_warning)+'</p>';
    out+='</article>';
  });
  out+='</section>';
  return out;
}
function genusVisualComparison(data){
  const v=data && data.visual_comparison;
  if(!v) return "";
  const items=Array.isArray(v.items)?v.items:[];
  const hasItems=items.length>0;
  const hasPlate=!!v.plate_image_url;
  if(!hasItems && !hasPlate) return "";
  let out='<section class="section-block diagnostic-visual-section"><div class="section-heading"><div><div class="eyebrow">Visual field key</div><h2>'+esc(v.title||"Diagnostic comparison")+'</h2>'+(v.subtitle?'<p>'+esc(v.subtitle)+'</p>':'')+'</div></div>';
  if(v.memory_rule) out+='<div class="diagnostic-memory-rule"><span>MEMORY RULE</span><strong>'+esc(v.memory_rule)+'</strong></div>';
  if(hasPlate){
    out+='<figure class="diagnostic-comparison-plate"><a class="diagnostic-comparison-plate-link" href="'+esc(v.plate_image_url)+'" target="_blank" rel="noopener noreferrer" aria-label="Open comparison plate full size"><img src="'+esc(v.plate_image_url)+'" alt="'+esc(v.plate_alt||v.title||"Diagnostic comparison plate")+'" loading="lazy"></a>';
    if(v.plate_caption) out+='<figcaption>'+esc(v.plate_caption)+'</figcaption>';
    out+='</figure>';
  }
  if(hasItems) out+='<div class="diagnostic-visual-grid">';
  items.forEach(function(item,index){
    const markers=Array.isArray(item.markers)?item.markers:[];
    // Optional per-photo framing makes sure small buds and diagnostic lobe tips survive gallery cropping.
    const fit=item.image_fit==="contain" ? "contain" : "cover";
    const focus=item.image_focus==="top" ? "top" : item.image_focus==="bottom" ? "bottom" : "center";
    const photoSrc=item.image_url||"";
    const safePhotoSrc=/^(https?:\/\/|content\/)/i.test(photoSrc);
    out+='<article class="diagnostic-visual-card"><div class="diagnostic-photo-wrap">';
    if(safePhotoSrc) out+='<a class="diagnostic-photo-open" href="'+esc(photoSrc)+'" target="_blank" rel="noopener noreferrer" title="Open full diagnostic photo to zoom">';
    out+='<img data-diagnostic-image src="'+esc(photoSrc)+'" alt="'+esc((item.label||item.scientific_name||"Diagnostic plant")+" — "+(item.image_role||"diagnostic view"))+'" loading="lazy" style="object-fit:'+fit+';object-position:center '+focus+'">';
    if(safePhotoSrc) out+='</a>';
    if(markers.length){
      const arrowId="diagnosticArrow"+String(v.instance_id || data.id || data.name || "visual").replace(/[^a-z0-9]/gi,"")+"-"+index;
      out+='<div class="diagnostic-arrow-stage" data-diag-stage hidden><svg class="diagnostic-arrow-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><marker id="'+arrowId+'" markerUnits="userSpaceOnUse" markerWidth="1.8" markerHeight="1.8" refX="1.6" refY=".9" orient="auto"><path d="M0,0 L1.8,.9 L0,1.8 z"></path></marker></defs>';
      markers.forEach(function(m){
        const lx=Number(m.label_x||8), ly=Number(m.label_y||10), tx=Number(m.target_x||50), ty=Number(m.target_y||50);
        out+='<line x1="'+lx+'" y1="'+ly+'" x2="'+tx+'" y2="'+ty+'" marker-end="url(#'+arrowId+')"></line>';
      });
      out+='</svg>';
      markers.forEach(function(m){
        out+='<span class="diagnostic-photo-label" style="left:'+Number(m.label_x||8)+'%;top:'+Number(m.label_y||10)+'%">'+esc(m.label||"look here")+'</span>';
      });
      out+='</div>';
    }
    out+='</div><div class="diagnostic-visual-copy"><div class="eyebrow">'+esc(item.label||"Diagnostic view")+'</div><h3><i>'+esc(item.scientific_name||"")+'</i></h3>'+
      '<div class="anatomy-teach-steps diagnostic-guided-copy">'+
      anatomyTeachingSentence("Where to look",anatomyWhereToLook(item.image_role||item.label))+
      anatomyTeachingSentence("What to compare",item.caption||"Use the identified photo role to inspect the same structure in the other species.")+
      (item.why_it_matters?anatomyTeachingSentence("How it separates them",item.why_it_matters):"")+
      '</div>'+
      '<details class="anatomy-next-step"><summary>How to confirm this comparison</summary><p>Compare the same view on the other species and use the documented genus key. A single view or an unverified label should not settle the identification.</p></details>';
    if(item.source_page) out+='<p class="diagnostic-photo-credit">'+esc(item.creator||"Source photo")+' · '+esc(item.license||"license review")+' · <a href="'+esc(item.source_page)+'" target="_blank" rel="noopener noreferrer">source ↗</a></p>';
    out+='</div></article>';
  });
  if(hasItems) out+='</div>';
  if(v.overlay_note) out+='<p class="diagnostic-overlay-note">'+esc(v.overlay_note)+'</p>';
  if(Array.isArray(v.study_only_photo_links) && v.study_only_photo_links.length){
    const links=v.study_only_photo_links.filter(function(link){ return link && /^https:\/\/[a-z0-9.-]+(?:\/|$)/i.test(String(link.url||"")); }).slice(0,8);
    if(links.length){
      out+='<div class="diagnostic-overlay-note"><div class="eyebrow">Original-site botanical photographs</div><h3>Additional photo references · link only</h3><p>'+esc(v.study_only_intro||"These images open at their source site; they are not included in the licensed learner gallery.")+'</p><ul class="trait-list">';
      links.forEach(function(link){
        out+='<li><a href="'+esc(link.url)+'" target="_blank" rel="noopener noreferrer">'+esc(link.label||"View original photo")+' ↗</a>';
        if(link.look_for) out+=' — '+esc(link.look_for);
        if(link.reuse) out+='<span class="diagnostic-photo-credit"> · '+esc(link.reuse)+'</span>';
        out+='</li>';
      });
      out+='</ul></div>';
    }
  }
  out+='</section>';
  return out;
}
// Annotation coordinates are percentages of original IMAGE pixels, not the
// 4:3 card. Align overlay to the actual visible image after object-fit.
function positionDiagnosticArrowStages(){
  document.querySelectorAll('.diagnostic-photo-wrap [data-diag-stage]').forEach(function(stage){
    const wrap=stage.parentElement;
    const image=wrap.querySelector('img[data-diagnostic-image]');
    if(!image || !image.naturalWidth || !image.naturalHeight){ stage.hidden=true; return; }
    const cw=wrap.clientWidth, ch=wrap.clientHeight;
    if(!cw || !ch){ stage.hidden=true; return; }
    const cover=image.style.objectFit==="cover";
    const scale=cover ? Math.max(cw/image.naturalWidth,ch/image.naturalHeight) :
      Math.min(cw/image.naturalWidth,ch/image.naturalHeight);
    const width=image.naturalWidth*scale, height=image.naturalHeight*scale;
    stage.style.left=((cw-width)/2)+'px';
    stage.style.top=((ch-height)/2)+'px';
    stage.style.width=width+'px';
    stage.style.height=height+'px';
    stage.hidden=false;
  });
}
document.addEventListener("load",function(e){
  if(e.target && e.target.matches && e.target.matches('img[data-diagnostic-image]')){
    window.requestAnimationFrame(positionDiagnosticArrowStages);
  }
},true);
window.addEventListener("resize",positionDiagnosticArrowStages,{passive:true});
/* The original lesson lived inside a closed <details> drawer. Lazy-loaded
   images can finish while hidden; when the user opens the drawer, reposition
   the overlay after layout even if no new image load event fires. */
document.addEventListener("toggle",function(e){
  if(e.target && e.target.matches && e.target.matches("details")){
    window.requestAnimationFrame(positionDiagnosticArrowStages);
  }
},true);

function genusComparePanel(genus,members){
  if(!members || members.length<2) return "";
  const opts=members.map(function(sp){ return '<option value="'+esc(sp.id)+'">'+esc(scientificName(sp))+(commonName(sp)?' — '+esc(commonName(sp)):'')+'</option>'; }).join("");
  const second=members[1].id;
  return '<section class="family-compare-panel genus-compare-panel"><div><div class="eyebrow">Species separation drill</div><h2>Compare two '+esc(genus)+' species</h2><p>The family and genus characters should stay stable. Focus on the smaller characters that actually split these species.</p></div>'+
    '<div class="family-compare-controls"><label><span>Species A</span><select id="genusCompareA">'+opts+'</select></label>'+
    '<span class="compare-vs">vs</span><label><span>Species B</span><select id="genusCompareB">'+opts.replace('value="'+esc(second)+'"','value="'+esc(second)+'" selected')+'</select></label>'+
    '<button type="button" class="primary-button" data-genus-compare>Compare</button></div></section>';
}
function selectedSpecies(){ return state.speciesById.get(state.selectedSpeciesId) || null; }

function similarCandidates(sp){
  const ids=[], reasons=new Map();
  function add(id,reason){
    if(!id || id===sp.id || ids.includes(id) || !state.speciesById.has(id)) return;
    ids.push(id); reasons.set(id,reason);
  }
  const overrides=(state.learning.comparison_overrides && state.learning.comparison_overrides[sp.id]) || [];
  overrides.forEach(function(id){ add(id,"Useful comparison"); });
  state.species.filter(function(x){ return x.genus===sp.genus && x.id!==sp.id; }).forEach(function(x){ add(x.id,"Same genus"); });
  if(ids.length<5) state.species.filter(function(x){ return x.family===sp.family && x.id!==sp.id; }).forEach(function(x){ add(x.id,"Same family"); });
  return ids.slice(0,5).map(function(id){ return {sp:state.speciesById.get(id),reason:reasons.get(id)}; });
}

async function ensureFamilyData(family){
  if(state.familyCache.has(family)) return state.familyCache.get(family);
  try{
    const data=await loadJSON("content/taxa/"+encodeURIComponent(family)+"/family.json");
    state.familyCache.set(family,data); return data;
  }catch(e){ state.familyCache.set(family,null); return null; }
}
async function ensureGenusByName(family,genus){
  const key=family+"/"+genus;
  if(state.genusCache.has(key)) return state.genusCache.get(key);
  try{
    const data=await loadJSON("content/taxa/"+encodeURIComponent(family)+"/"+encodeURIComponent(genus)+"/genus.json");
    state.genusCache.set(key,data); return data;
  }catch(e){ state.genusCache.set(key,null); return null; }
}
async function ensureGenusData(sp){ return ensureGenusByName(sp.family,sp.genus); }

function updateHeader(){
  document.body.dataset.view=state.view;
  document.querySelectorAll("[data-difficulty]").forEach(function(btn){
    const on=btn.dataset.difficulty===state.difficulty;
    btn.classList.toggle("active",on); btn.setAttribute("aria-pressed",String(on));
  });
  document.querySelectorAll(".main-nav [data-nav]").forEach(function(btn){
    const on=btn.dataset.nav===state.view || (btn.dataset.nav==="home" && (state.view==="family" || state.view==="genus" || state.view==="plant"));
    btn.classList.toggle("active",on);
  });
  els.quiz.classList.toggle("active",state.quizMode);
  els.quiz.textContent=state.quizMode ? "Quiz: on" : "Quiz: off";
}
function setView(view){
  state.view=view; state.quizRevealed=false;
  if(view!=="plant") state.selectedSpeciesId=null;
  closeModal(); render(); window.scrollTo({top:0,behavior:"smooth"});
  if(view==="approvals" && !state.approvals){
    loadApprovals().then(function(){ if(state.view==="approvals") render(); });
  }
}
function openFamily(family){
  state.selectedFamily=family; state.view="family"; state.quizRevealed=false; render();
  ensureFamilyData(family).then(function(){ if(state.view==="family" && state.selectedFamily===family) render(); });
  window.scrollTo({top:0,behavior:"smooth"});
}
function openGenus(family,genus){
  if(!family || !genus) return;
  state.selectedFamily=family; state.selectedGenusFamily=family; state.selectedGenus=genus; state.view="genus"; state.quizRevealed=false;
  closeModal(); render();
  Promise.all([ensureFamilyData(family),ensureGenusByName(family,genus)]).then(function(){
    if(state.view==="genus" && state.selectedGenusFamily===family && state.selectedGenus===genus) render();
  });
  window.scrollTo({top:0,behavior:"smooth"});
}
function openPlant(id){
  if(!state.speciesById.has(id)) return;
  state.selectedSpeciesId=id; state.view="plant"; state.quizRevealed=false;
  els.search.value=""; hideResults(); render();
  const sp=selectedSpecies();
  Promise.all([ensureFamilyData(sp.family),ensureGenusData(sp)]).then(function(){ if(state.view==="plant" && state.selectedSpeciesId===id) render(); });
  window.scrollTo({top:0,behavior:"smooth"});
}
function randomQuiz(){
  if(!state.species.length) return;
  state.quizMode=true; writeLocal("hays-botany-quiz","true");
  const sp=state.species[Math.floor(Math.random()*state.species.length)];
  openPlant(sp.id);
}
function setDifficulty(level){
  if(!state.learning.difficulty_levels[level]) return;
  state.difficulty=level; writeLocal("hays-botany-difficulty",level); render();
}


async function loadApprovals(force){
  if(state.approvals && !force) return;
  state.approvalsError="";
  const localHost=location.hostname==="127.0.0.1" || location.hostname==="localhost";
  if(localHost){
    try{
      const r=await fetch("/api/approvals",{cache:"no-store"});
      if(r.ok){
        const data=await r.json();
        state.approvals=data.queue || {items:[]};
        state.approvalRevision=data.revision || null;
        state.approvalsWriteEnabled=Boolean(data.write_enabled);
        state.approvalArtifacts=data.artifacts || {};
        return;
      }
    }catch(err){}
  }
  try{
    state.approvals=await loadJSON("research-queue.json");
    state.approvalRevision=null;
    state.approvalsWriteEnabled=false;
    state.approvalArtifacts={};
  }catch(err){
    state.approvalsError=err.message || String(err);
  }
}
function approvalBatchLabel(item){
  const raw=item.batch_id || "unbatched";
  const match=raw.match(/-b(\d{3})$/i);
  if(match) return "B"+match[1];
  const direct=raw.match(/\bB(\d{3})\b/i);
  return direct ? "B"+direct[1] : raw;
}
function approvalRangeStatus(item){
  const explicit=item.native_range_status || item.range_status || item.target_zone_status || (item.project_inclusion && item.project_inclusion.target_zone_status);
  if(explicit) return String(explicit).toUpperCase();
  const notes=String(item.notes||"").toUpperCase();
  if(notes.includes("UNRESOLVED")) return "UNRESOLVED";
  if(notes.includes("RANGE FAIL") || notes.includes("NATIVE-STATUS FAIL") || notes.includes("TARGET-ZONE FAIL") || notes.includes("STRICT TARGET-ZONE FAIL")) return "FAIL";
  if(notes.includes("PASS")) return "PASS";
  return "UNKNOWN";
}
function approvalNeedsAction(item){
  if(item.learner_admission_status==="APPROVED") return false;
  if(item.user_decision && item.user_decision.decision) return false;
  const a=item.approval_status || "";
  const s=item.status || "";
  return ["ready_for_approval","ready_for_comparison_approval","needs_manual_review"].includes(a)
    || ["reviewed_ready_for_approval","reviewed_comparison_recommended","needs_manual_review"].includes(s);
}
function approvalDecisionText(item){
  const d=item.user_decision && item.user_decision.decision;
  if(!d && item.learner_admission_status==="APPROVED"){
    if(item.learner_curation_status==="approved_taxonomy_mapping_needed") return "Learner approved · taxonomy mapping needed";
    if(item.learner_curation_status==="represented_existing_no_new_card") return "Learner approved · represented by existing concept";
    return "Learner approved";
  }
  if(!d) return "";
  const labels={
    approve_for_curation:"Approved for curation",
    approve_as_comparison:"Approved as comparison",
    approve_with_range_exception:"Approved for learner; range remains unresolved",
    hold_unresolved:"Held unresolved",
    needs_more_review:"Needs more review",
    reject:"Rejected",
    accept_range_fail:"Range fail accepted",
    accept_review_keep_unresolved:"Review accepted; unresolved held"
  };
  return labels[d] || titleCase(d);
}
function approvalStatusClass(value){
  const v=String(value||"").toUpperCase();
  if(v==="PASS") return "status-pass";
  if(v==="FAIL") return "status-fail";
  if(v==="UNRESOLVED") return "status-unresolved";
  return "status-neutral";
}
function approvalBatchNumber(label){
  const m=String(label).match(/B(\d+)/i);
  return m ? Number(m[1]) : -1;
}

function mediumInatPhoto(url){
  return String(url||"").replace(/\/(square|small|medium|large)\./,"/medium.");
}
async function approvalDraft(item){
  if(state.approvalDraftCache.has(item.id)) return state.approvalDraftCache.get(item.id);
  const promise=loadJSON("research-drafts/"+encodeURIComponent(item.id)+"/draft.json").catch(function(){ return null; });
  state.approvalDraftCache.set(item.id,promise);
  return promise;
}
async function inatObservationPhotos(observationUrl){
  const match=String(observationUrl||"").match(/\/observations\/(\d+)/);
  if(!match) return [];
  const r=await fetch("https://api.inaturalist.org/v1/observations/"+match[1],{cache:"no-store"});
  if(!r.ok) throw new Error("iNaturalist observation request failed");
  const data=await r.json();
  const obs=(data.results||[])[0];
  if(!obs) return [];
  return (obs.photos||[]).map(function(photo){
    return {
      url:mediumInatPhoto(photo.url),
      source:obs.uri || observationUrl,
      attribution:photo.attribution || "",
      license:photo.license_code || "",
      label:"Reference observation"
    };
  });
}
async function inatTaxonPhotos(name,limit){
  const params=new URLSearchParams({
    taxon_name:name,
    quality_grade:"research",
    photos:"true",
    per_page:"12",
    order_by:"votes",
    order:"desc"
  });
  const r=await fetch("https://api.inaturalist.org/v1/observations?"+params.toString(),{cache:"no-store"});
  if(!r.ok) throw new Error("iNaturalist photo search failed");
  const data=await r.json(), out=[];
  (data.results||[]).some(function(obs){
    (obs.photos||[]).forEach(function(photo){
      if(out.length>=limit) return;
      const url=mediumInatPhoto(photo.url);
      if(out.some(function(x){ return x.url===url; })) return;
      out.push({
        url:url,
        source:obs.uri || ("https://www.inaturalist.org/observations/"+obs.id),
        attribution:photo.attribution || "",
        license:photo.license_code || "",
        label:"Species photo candidate"
      });
    });
    return out.length>=limit;
  });
  return out;
}
async function approvalPhotoPackage(item){
  if(state.approvalPhotoCache.has(item.id)) return state.approvalPhotoCache.get(item.id);
  const promise=(async function(){
    const draft=await approvalDraft(item);
    const pv=(draft && draft.photo_verification) || {};
    const roles=Array.isArray(pv.diagnostic_roles) ? pv.diagnostic_roles : [];
    const refs=Array.isArray(pv.reference_candidates) ? pv.reference_candidates : [];
    let photos=[];
    if(pv.user_inaturalist_example_observation){
      try{ photos=await inatObservationPhotos(pv.user_inaturalist_example_observation); }catch(err){}
    }
    if(photos.length<6){
      try{
        const extra=await inatTaxonPhotos(item.scientific_name||item.id,6-photos.length);
        extra.forEach(function(p){ if(!photos.some(function(x){ return x.url===p.url; })) photos.push(p); });
      }catch(err){}
    }
    return {
      roles:roles,
      photos:photos.slice(0,6),
      references:refs,
      example:pv.user_inaturalist_example_observation || ""
    };
  })();
  state.approvalPhotoCache.set(item.id,promise);
  return promise;
}
function approvalPhotoPlaceholder(item){
  return '<section class="approval-photo-block" data-approval-photos="'+esc(item.id)+'"><div class="approval-photo-loading">Loading diagnostic photo candidates…</div></section>';
}
function approvalPhotosHTML(item,pkg){
  let out='<div class="approval-photo-heading"><div><b>Diagnostic photo review</b><span>Reference candidates — not the final locked image set.</span></div>'+
    (pkg.photos.length?'<strong>'+pkg.photos.length+' photos</strong>':'')+'</div>';
  if(pkg.roles.length){
    out+='<div class="approval-role-label">This package needs:</div><div class="approval-role-chips">'+
      pkg.roles.map(function(role){ return '<span>'+esc(role)+'</span>'; }).join("")+'</div>';
  }
  if(pkg.photos.length){
    out+='<div class="approval-photo-gallery">';
    pkg.photos.forEach(function(photo,index){
      const credit=[photo.attribution,photo.license].filter(Boolean).join(" · ");
      out+='<a class="approval-photo-candidate" href="'+esc(photo.source)+'" target="_blank" rel="noreferrer" title="Open source observation">'+
        '<img src="'+esc(photo.url)+'" alt="'+esc((item.scientific_name||item.id)+" photo candidate "+(index+1))+'" loading="lazy">'+
        '<span><b>'+esc(photo.label)+'</b>'+(credit?'<small>'+esc(credit)+'</small>':'')+'</span></a>';
    });
    out+='</div>';
  }else{
    out+='<div class="approval-photo-empty">No live candidate thumbnails loaded. The diagnostic roles are still shown so the missing photo package is obvious.</div>';
  }
  const sourceLinks=[];
  if(pkg.example) sourceLinks.push({url:pkg.example,label:"iNaturalist reference observation"});
  pkg.references.forEach(function(url,i){ sourceLinks.push({url:url,label:"Reference source "+(i+1)}); });
  if(sourceLinks.length){
    out+='<div class="approval-photo-sources">'+sourceLinks.map(function(x){ return '<a href="'+esc(x.url)+'" target="_blank" rel="noreferrer">'+esc(x.label)+' ↗</a>'; }).join("")+'</div>';
  }
  return out;
}
async function hydrateApprovalPhotoBlock(el){
  if(!el || el.dataset.loaded==="true" || el.dataset.loading==="true") return;
  const id=el.dataset.approvalPhotos;
  const item=(state.approvals && state.approvals.items || []).find(function(x){ return x.id===id; });
  if(!item) return;
  el.dataset.loading="true";
  try{
    const pkg=await approvalPhotoPackage(item);
    const current=document.querySelector('[data-approval-photos="'+CSS.escape(id)+'"]');
    if(current){
      current.innerHTML=approvalPhotosHTML(item,pkg);
      current.dataset.loaded="true";
      current.dataset.loading="false";
    }
  }catch(err){
    const current=document.querySelector('[data-approval-photos="'+CSS.escape(id)+'"]');
    if(current){
      current.innerHTML='<div class="approval-photo-empty">Photo candidates could not be loaded. Open the review files below for the source leads.</div>';
      current.dataset.loaded="true";
      current.dataset.loading="false";
    }
  }
}
function hydrateVisibleApprovalPhotos(){
  const blocks=Array.from(document.querySelectorAll("[data-approval-photos]"));
  if(!blocks.length) return;
  if("IntersectionObserver" in window){
    const observer=new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          observer.unobserve(entry.target);
          hydrateApprovalPhotoBlock(entry.target);
        }
      });
    },{rootMargin:"300px 0px"});
    blocks.forEach(function(block){ observer.observe(block); });
  }else{
    blocks.slice(0,20).forEach(hydrateApprovalPhotoBlock);
  }
}

function approvalArtifactLinks(item){
  const paths=state.approvalArtifacts[item.id] || [];
  if(!paths.length) return "";
  return '<details class="approval-artifacts"><summary>Review files ('+paths.length+')</summary><div>'+
    paths.map(function(path){ return '<a href="'+encodeURI(path)+'" target="_blank" rel="noreferrer">'+esc(path.split("/").pop())+' ↗</a>'; }).join("")+
    '</div></details>';
}
function approvalCard(item){
  const range=approvalRangeStatus(item);
  const decided=approvalDecisionText(item);
  const artifacts=approvalArtifactLinks(item);
  const pool=item.source_pool || {};
  const busy=state.approvalsBusy===item.id;
  const curationState=String(item.learner_curation_status||"");
  const canInstallSeparate=!["approved_taxonomy_mapping_needed","represented_existing_no_new_card"].includes(curationState);
  const comparisonSuggested=(item.approval_status==="ready_for_comparison_approval") || String(item.learner_role||"").includes("COMPARISON");
  let out='<article class="approval-card" data-approval-item="'+esc(item.id)+'">'+
    '<div class="approval-card-top"><div><div class="eyebrow">'+esc(item.family||"")+" › "+esc(item.genus||"")+'</div><h3><i>'+esc(item.scientific_name||item.id)+'</i></h3></div>'+
    encounterBadge(item)+'</div>'+
    '<p class="approval-notes">'+esc(item.notes||"No review note recorded.")+'</p>'+
    approvalPhotoPlaceholder(item)+
    '<div class="approval-meta">'+
      '<span><b>Status</b>'+esc(titleCase(item.status||"unknown"))+'</span>'+
      '<span><b>Approval</b>'+esc(titleCase(item.approval_status||"not set"))+'</span>'+
      (pool.wild_observations!=null?'<span><b>Wild obs</b>'+esc(pool.wild_observations)+'</span>':'')+
      (pool.source_count!=null?'<span><b>Source points</b>'+esc(pool.source_count)+'</span>':'')+
      (item.last_deep_reviewed_at?'<span><b>Reviewed</b>'+esc(String(item.last_deep_reviewed_at).replace("T"," ").slice(0,16))+'</span>':'')+
    '</div>'+artifacts;
  if(decided){
    const decisionNote=(item.user_decision && item.user_decision.note) || "";
    out+='<div class="approval-decision-record"><strong>'+esc(decided)+'</strong>'+(decisionNote?'<span>'+esc(decisionNote)+'</span>':'')+'</div>';
  }else if(state.approvalsWriteEnabled){
    out+='<label class="approval-note"><span>Optional decision note</span><textarea data-approval-note="'+esc(item.id)+'" rows="2" placeholder="Why you approved, held, or rejected this one…"></textarea></label>'+
      '<div class="approval-actions">'+
      (canInstallSeparate?'<button class="approval-action approve" type="button" data-approval-decision="approve_for_curation" data-approval-id="'+esc(item.id)+'">Approve for learner</button>':'')+
      '<button class="approval-action review" type="button" data-approval-decision="needs_more_review" data-approval-id="'+esc(item.id)+'">Needs more review</button>'+
      (comparisonSuggested && canInstallSeparate?'<button class="approval-action compare" type="button" data-approval-decision="approve_as_comparison" data-approval-id="'+esc(item.id)+'">Keep as comparison</button>':'')+
      '<button class="approval-action reject" type="button" data-approval-decision="reject" data-approval-id="'+esc(item.id)+'">Reject</button>'+
      '</div>';
    if(busy) out+='<div class="approval-saving">Saving decision…</div>';
  }else{
    out+='<div class="approval-readonly">Open this site with <code>RUN_LOCAL_SERVER.bat</code> to make approval decisions. This view is read-only on the static site.</div>';
  }
  return out+'</article>';
}
function approvalsView(){
  if(state.approvalsError && !state.approvals){
    return '<section class="page-intro"><div class="eyebrow">Curation gate</div><h1>Approvals</h1><p class="error-card">Could not load the approval queue: '+esc(state.approvalsError)+'</p></section>';
  }
  if(!state.approvals){
    return '<section class="page-intro"><div class="eyebrow">Curation gate</div><h1>Approvals</h1><p>Loading review decisions…</p></section>';
  }
  const all=(state.approvals.items||[]).slice();
  const action=all.filter(approvalNeedsAction);
  const decided=all.filter(function(x){ return Boolean(x.user_decision && x.user_decision.decision); });
  const pendingCuration=all.filter(function(x){ return x.learner_curation_status==="approved_pending_curation" || ["approved_pending_curation","approved_comparison_pending_curation"].includes(x.status); });
  const held=all.filter(function(x){ const d=x.user_decision && x.user_decision.decision; return d==="hold_unresolved" || d==="needs_more_review" || d==="accept_review_keep_unresolved"; });
  let list=all;
  if(state.approvalsFilter==="action") list=action;
  else if(state.approvalsFilter==="decided") list=decided;
  else if(state.approvalsFilter==="pending") list=pendingCuration;

  const groups=new Map();
  list.forEach(function(item){
    const label=approvalBatchLabel(item);
    if(!groups.has(label)) groups.set(label,[]);
    groups.get(label).push(item);
  });
  const ordered=Array.from(groups.entries()).sort(function(a,b){ return approvalBatchNumber(b[0])-approvalBatchNumber(a[0]); });

  let out='<section class="page-intro approval-intro"><div class="eyebrow">Learner admission</div><h1>Review special cases.</h1>'+
    '<p>Approved source-pool plants are eligible for visual identification lessons regardless of county-range research. This screen handles exceptional admission and taxonomy decisions; confirmed invasive or introduced plants may be labeled separately.</p></section>'+
    '<section class="approval-summary">'+
      '<div><strong>'+action.length+'</strong><span>need a decision</span></div>'+
      '<div><strong>'+pendingCuration.length+'</strong><span>approved, awaiting curation</span></div>'+
      '<div><strong>'+held.length+'</strong><span>held / more review</span></div>'+
      '<div><strong>'+all.length+'</strong><span>queue records</span></div>'+
    '</section>'+
    '<section class="approval-toolbar"><div class="approval-filters" role="group" aria-label="Approval filters">'+
      '<button type="button" data-approval-filter="action" class="'+(state.approvalsFilter==="action"?"active":"")+'">Needs decision</button>'+
      '<button type="button" data-approval-filter="pending" class="'+(state.approvalsFilter==="pending"?"active":"")+'">Awaiting curation</button>'+
      '<button type="button" data-approval-filter="decided" class="'+(state.approvalsFilter==="decided"?"active":"")+'">My decisions</button>'+
      '<button type="button" data-approval-filter="all" class="'+(state.approvalsFilter==="all"?"active":"")+'">All</button>'+
    '</div><button class="secondary-button" type="button" data-approval-refresh>Refresh queue</button></section>';
  if(state.approvalsError){
    out+='<div class="approval-save-error"><strong>Decision not saved.</strong><span>'+esc(state.approvalsError)+'</span><button class="secondary-button" type="button" data-approval-refresh>Refresh queue</button></div>';
  }
  out+='<div class="approval-mode-banner '+(state.approvalsWriteEnabled?"writable":"readonly")+'">'+
    (state.approvalsWriteEnabled
      ? '<strong>Decision mode is active.</strong><span>Changes are written locally to <code>research-queue.json</code> with revision checking and an audit log.</span>'
      : '<strong>Read-only queue view.</strong><span>Use <code>RUN_LOCAL_SERVER.bat</code> on your computer to approve, hold, compare, or reject records.</span>')+
    '</div>';
  if(!ordered.length) return out+'<div class="empty-panel">Nothing matches this filter.</div>';
  ordered.forEach(function(entry){
    const label=entry[0], items=entry[1];
    const family=Array.from(new Set(items.map(function(x){ return x.family; }).filter(Boolean))).join(" / ");
    out+='<section class="approval-batch"><div class="approval-batch-head"><div><div class="eyebrow">'+esc(label)+'</div><h2>'+esc(family||"Review batch")+'</h2></div><span>'+items.length+' record'+(items.length===1?"":"s")+'</span></div><div class="approval-grid">';
    items.forEach(function(item){ out+=approvalCard(item); });
    out+='</div></section>';
  });
  return out;
}
async function submitApprovalDecision(itemId,decision){
  if(!state.approvalsWriteEnabled || state.approvalsBusy) return;
  if(decision==="reject" && !window.confirm("Reject this record from the current curation path?")) return;
  if(decision==="approve_with_range_exception" && !window.confirm("Approve this learner entry while preserving its unresolved range label?")) return;
  const noteEl=document.querySelector('[data-approval-note="'+CSS.escape(itemId)+'"]');
  const note=noteEl ? noteEl.value.trim() : "";
  state.approvalsBusy=itemId; render();
  try{
    const r=await fetch("/api/approvals/decision",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({item_id:itemId,decision:decision,note:note,expected_revision:state.approvalRevision})
    });
    const data=await r.json().catch(function(){ return {}; });
    if(!r.ok) throw new Error(data.error || ("Decision failed with HTTP "+r.status));
    state.approvals=data.queue;
    state.approvalRevision=data.revision;
    state.approvalArtifacts=data.artifacts || state.approvalArtifacts;
    state.approvalsWriteEnabled=Boolean(data.write_enabled);
    state.approvalsError="";
  }catch(err){
    state.approvalsError=err.message || String(err);
  }finally{
    state.approvalsBusy=null; render();
  }
}

/* Compact, accessible presentation-only drawer. All source content remains in the DOM. */
function studyDrawer(title,preview,content,tone,id){
  if(!content) return "";
  return '<details class="study-drawer study-drawer-'+esc(tone||"neutral")+'"'+(id?' id="'+esc(id)+'Section"':'')+'>'+
    '<summary><span class="study-drawer-icon" aria-hidden="true">'+(tone==="photo"?"◉":tone==="compare"?"⇄":tone==="terms"?"Aa":"✣")+'</span>'+
    '<span class="study-drawer-label"><strong>'+esc(title)+'</strong><small>'+esc(preview)+'</small></span>'+
    '<span class="study-drawer-chevron" aria-hidden="true">⌄</span></summary>'+
    '<div class="study-drawer-body">'+content+'</div></details>';
}
function familyCard(family){
  const p=familyProfile(family)||{};
  const members=familySpecies(family);
  const genera=generaForFamily(family).length;
  const countLabel=members.length ? members.length+" curated taxa" : "Family lesson ready";
  const imgs=members.map(function(sp){ return {sp:sp,img:firstImage(sp)}; }).filter(function(x){ return x.img; }).slice(0,3);
  let mosaic='<span class="family-mosaic">';
  if(imgs.length) imgs.forEach(function(x){ mosaic+='<img src="'+imagePath(x.sp,x.img)+'" alt="" loading="lazy">'; });
  else mosaic+='<span class="family-mosaic-empty">✣</span>';
  mosaic+='</span>';
  return '<button class="family-card" type="button" data-family="'+esc(family)+'">'+mosaic+
    '<span class="family-card-body"><span class="family-count">'+esc(countLabel)+'</span><strong>'+esc(family)+'</strong>'+
    '<em>'+esc(p.common_name||"")+'</em><span class="family-card-meta">'+(members.length?genera+' genera · '+members.length+' species anchors':'lesson built · species anchors pending')+'</span>'+
    '<span class="family-clue">'+esc(p.plain_signature||"Open this family to see recurring field characters.")+'</span></span></button>';
}
function homeView(){
  const counts=familyCounts();
  const profiles=Object.keys((state.learning&&state.learning.family_profiles)||{});
  const preferred=state.learning.home_families || [];
  const discovered=Array.from(new Set(profiles.concat(Array.from(counts.keys()),state.lessonIndex.families))).sort(function(a,b){ return a.localeCompare(b); });
  const families=preferred.concat(discovered.filter(function(f){ return !preferred.includes(f); }));
  const anchoredFamilies=families.filter(function(f){ return familySpecies(f).length; }).length;
  const profileFamilies=families.filter(function(f){ return !!familyProfile(f); }).length;
  const completedFamilyLessons=state.lessonIndex.families.length;
  const completedGenusLessons=state.lessonIndex.genera.length;
  const level=state.learning.difficulty_levels[state.difficulty];
  let out='<section class="home-hero"><div class="eyebrow">Structure-first field botany</div>'+
    '<h1>Learn what to look at, then learn what it is called.</h1>'+
    '<p>Start with a plant or a family. The first screen stays simple; deeper botany is always one tap away.</p>'+
    '<div class="home-actions"><button class="primary-button" type="button" data-random-quiz>Quiz me with a random plant</button>'+
    '<button class="secondary-button" type="button" data-nav="browse">Browse Family → Genus → Species</button></div>'+
    '<div class="difficulty-explainer"><span>'+esc(level.label)+'</span><strong>'+esc(level.mantra)+'</strong><p>'+esc(level.description)+'</p></div></section>';
  out+='<section class="section-block family-library"><div class="section-heading"><div><div class="eyebrow">Your plant adventure</div><h2>Meet the plant families 🌿</h2></div>'+
    '<button class="text-button" type="button" data-nav="browse">Open taxonomy browser →</button></div>'+
    '<p class="section-intro">Start with the big picture. Look at photos, spot a clue, then follow the trail from family to genus to species. Every scientific word is a tool you can learn.</p>'+
    '<div class="library-summary"><div><strong>'+families.length+'</strong><span>families represented</span></div><div><strong>'+completedFamilyLessons+'</strong><span>family modules</span></div><div><strong>'+completedGenusLessons+'</strong><span>genus modules</span></div><div><strong>'+state.species.length+'</strong><span>curated species</span></div></div>'+ 
    '<div class="family-grid">';
  families.slice(0,8).forEach(function(f){ out+=familyCard(f); });
  out+='</div>';
  if(families.length>8){
    out+='<details class="home-more-families"><summary><strong>Explore all '+families.length+' plant families</strong><span>Open the complete photo-tile library · '+(families.length-8)+' more families <b aria-hidden="true">⌄</b></span></summary><div class="family-grid">';
    families.slice(8).forEach(function(f){out+=familyCard(f);});
    out+='</div></details>';
  }
  out+='</section><section class="method-strip"><div><b>1</b><span><strong>See it</strong>Start with the structure.</span></div>'+
    '<div><b>2</b><span><strong>Name it</strong>Tap terms as they appear.</span></div>'+
    '<div><b>3</b><span><strong>Compare it</strong>Put relatives side by side.</span></div></section>';
  return out;
}
function speciesTile(sp,showFamily){
  return '<button class="species-tile" type="button" data-species="'+sp.id+'">'+thumb(sp,"species-tile-img")+
    '<span>'+(showFamily?'<small>'+esc(sp.genus)+'</small>':'')+'<strong><i>'+esc(scientificName(sp))+'</i></strong>'+
    '<em>'+esc(commonName(sp))+'</em>'+encounterBadge(sp)+'</span></button>';
}
function familyVisualVocabulary(p){
  const ids=(p && Array.isArray(p.key_terms) ? p.key_terms : []).filter(function(id){ return state.learning.terms[id]; });
  if(!ids.length) return "";
  let out='<section class="section-block family-vocab"><div class="section-heading"><div><div class="eyebrow">Learn the secret plant words</div><h2>See it → name it → remember it</h2></div>'+
    '<button class="secondary-button" type="button" data-family-term-drill>Drill these terms</button></div><p class="section-intro">Tap a picture to learn its botanical term, what it means in plain language, and where to look for it on a real plant.</p><div class="family-vocab-grid">';
  ids.slice(0,9).forEach(function(id){
    const t=state.learning.terms[id];
    out+='<button class="family-vocab-card" type="button" data-term="'+esc(id)+'">'+termPreviewMedia(t)+'<span><strong>'+esc(t.term)+'</strong><small>'+esc(t.plain)+'</small></span></button>';
  });
  return out+'</div></section>';
}

function studyPath(level){
  const steps=[["1","Family","Big group"],["2","Genus","Close relatives"],["3","Species","One kind"]];
  return '<div class="study-path" aria-label="Plant learning path">'+steps.map(function(x,i){return '<span'+(i===level?' aria-current="step"':'')+'><b>'+x[0]+'</b> '+x[1]+' · '+x[2]+'</span>';}).join('<b aria-hidden="true">→</b>')+'</div>';
}
function familyView(){
  const family=state.selectedFamily, p=familyProfile(family)||{}, members=familySpecies(family), genera=generaForFamily(family);
  const canon=state.familyCache.get(family);
  const signature=state.difficulty==="field" ? (p.field_signature||p.plain_signature) : (p.plain_signature||p.field_signature);
  const familyFirst=p.look_here_first||(canon&&canon.family_diagnostics&&(canon.family_diagnostics.where_to_look_first||canon.family_diagnostics.field_tip||canon.family_diagnostics.inflorescence))||"Start with the plant's reproductive structures and leaf arrangement.";
  const photoLesson=canon?familyVisualLessonHTML(canon):"";
  let out='<section class="breadcrumbs"><button type="button" data-nav="home">Home</button><span>›</span><strong>'+esc(family)+'</strong></section>'+
    taxonomyLadder(family,null,null)+studyPath(0)+
    '<section class="family-hero"><div class="family-hero-copy"><div class="eyebrow">Family · '+members.length+' curated taxa</div><h1>'+esc(family)+'</h1>'+
    '<p class="family-common">'+esc(p.common_name || (canon&&canon.common_name) || "")+'</p>'+
    '<div class="look-card"><span>LOOK HERE FIRST</span><strong>'+esc(familyFirst)+'</strong></div>'+
    '<p class="family-signature">'+esc(signature||"")+'</p><div class="term-row">';
  (p.key_terms||[]).slice(0,state.difficulty==="simple"?4:9).forEach(function(id){ out+=termChip(id); });
  out+='</div><div class="button-row"><button class="primary-button" type="button" data-family-info="'+esc(family)+'">Why is this a family?</button>'+
    '<button class="secondary-button" type="button" data-nav="glossary">Open botanical terms</button></div></div><div class="family-photo-stack">';
  if(members.length) members.slice(0,4).forEach(function(sp){ out+='<button type="button" data-species="'+sp.id+'">'+thumb(sp,"family-stack-img")+'<span>'+esc(commonName(sp)||scientificName(sp))+'</span></button>'; });
  else out+='<div class="empty-panel">Family lesson ready. Canonical species anchors are still being installed.</div>';
  out+='</div></section>';
  out+='<nav class="lesson-route" aria-label="Family study sequence"><strong>What should I do next?</strong>'+
    (photoLesson?'<button type="button" data-jump="familyPhoto"><b>1</b><span>Look at the anatomy</span></button>':'')+
    (genera.length?'<button type="button" data-jump="familyGenus"><b>2</b><span>Choose a genus</span></button>':'')+
    (members.length?'<button type="button" data-jump="familySpecies"><b>3</b><span>Study species photos</span></button>':'')+'</nav>';
  out+='<div class="study-drawer-grid">';
  if(photoLesson) out+=studyDrawer("Study family structures","See the first three photo clues, then reveal every other example.",photoLesson,"photo","familyPhoto");
  out+=studyDrawer("Learn the botanical terms","Visual vocabulary and a short practice drill.",familyVisualVocabulary(p),"terms");
  const genusStart=out.length;
  out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Next stop · closer relatives</div><h2>Choose a genus to explore</h2></div></div><div class="genus-buttons">';
  if(genera.length) genera.forEach(function(g){ out+='<button type="button" data-genus="'+esc(g[0])+'" data-genus-family="'+esc(family)+'"><i>'+esc(g[0])+'</i><span>'+g[1]+'</span></button>'; });
  else out+='<div class="empty-panel">No canonical genus anchors are installed yet. The family-level lesson above is still available.</div>';
  out+='</div></section>';
  out=out.slice(0,genusStart)+studyDrawer("Choose a genus",genera.length+" close-relative groups to explore.",out.slice(genusStart),"browse","familyGenus");
  const speciesStart=out.length;
  out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Meet the plants</div><h2>Explore the species</h2></div></div><div class="species-tile-grid">';
  if(members.length) members.forEach(function(sp){ out+=speciesTile(sp,true); });
  else out+='<div class="empty-panel">No canonical species anchors are installed for this family yet.</div>';
  out+='</div></section>';
  out=out.slice(0,speciesStart)+studyDrawer("Species photo library",members.length+" species with identity photos and field clues.",out.slice(speciesStart),"photo","familySpecies");
  out+=studyDrawer("Compare species", "Side-by-side field identification.",familyComparePanel(family,members),"compare");
  out+='</div>';
  return out;
}
function genusView(){
  const family=state.selectedGenusFamily, genus=state.selectedGenus;
  if(!family || !genus) return browseView();
  const members=genusSpecies(family,genus), data=state.genusCache.get(family+"/"+genus), p=familyProfile(family)||{};
  const shared=genusSharedTraits(data), priority=genusPriorityTraits(data), quick=genusQuickRows(data);
  const common=(data&&data.common_group)||genus;
  const genusFirst=(data&&(data.look_here_first||(data.shared_genus_recognition&&data.shared_genus_recognition.look_here_first)||(data.study_strategy&&data.study_strategy.look_here_first)))||("Compare shared "+genus+" structures before separating individual species.");
  const genusPhotoLesson=botanyGenusPartPreview(members,data);
  const warning=(data&&data.study_strategy&&data.study_strategy.warning) || (data&&Array.isArray(data.study_notes)&&data.study_notes[0]) || "";
  let out='<section class="breadcrumbs"><button type="button" data-nav="home">Home</button><span>›</span><button type="button" data-family="'+esc(family)+'">'+esc(family)+'</button><span>›</span><strong><i>'+esc(genus)+'</i></strong></section>'+
    taxonomyLadder(family,genus,null)+studyPath(1)+
    '<section class="genus-hero"><div><div class="eyebrow">Genus · '+members.length+' curated species</div><h1><i>'+esc(genus)+'</i></h1><p class="family-common">'+esc(common)+'</p>'+
    '<div class="look-card"><span>LOOK HERE FIRST · GENUS</span><strong>'+esc(genusFirst)+'</strong></div>'+
    (warning?'<details class="genus-warning"><summary>Identification caution · what not to rely on</summary><p>'+esc(warning)+'</p></details>':'')+'</div><div class="genus-photo-strip">';
  if(members.length) members.slice().sort(function(a,b){return imagesFor(b).length-imagesFor(a).length;}).slice(0,3).forEach(function(sp){ out+='<button type="button" data-species="'+esc(sp.id)+'">'+thumb(sp,"genus-hero-img")+'<span>'+esc(commonName(sp)||scientificName(sp))+'</span></button>'; });
  else out+='<div class="empty-panel">Species anchors for this genus are still being installed.</div>';
  out+='</div></section>';
  out+='<nav class="lesson-route" aria-label="Genus study sequence"><strong>How to identify a '+esc(genus)+' species</strong>'+
    (genusPhotoLesson?'<button type="button" data-jump="genusPhoto"><b>1</b><span>Inspect genus anatomy</span></button>':'')+
    (priority.length?'<button type="button" data-jump="genusPriority"><b>2</b><span>Check dividing features</span></button>':'')+
    (members.length?'<button type="button" data-jump="genusSpecies"><b>3</b><span>Open a species card</span></button>':'')+'</nav>';
  out+='<div class="study-drawer-grid">'+
    studyDrawer("Study genus anatomy","Find the real structures, then open more examples.",genusPhotoLesson,"photo","genusPhoto");
  const sharedStart=out.length;
  out+='<section class="two-column-learning genus-levels"><article class="learning-card"><div class="eyebrow">Family characters</div><h2>Why '+esc(family)+'?</h2><p>'+esc(p.plain_signature||p.field_signature||"Use the family lesson to recognize the broader structural pattern.")+'</p><button class="text-button" type="button" data-family="'+esc(family)+'">Open family →</button></article>'+
    '<article class="learning-card"><div class="eyebrow">Genus characters</div><h2>What makes <i>'+esc(genus)+'</i> hang together?</h2>';
  if(shared.length) out+='<ul class="trait-list">'+shared.map(function(x){ return '<li>'+esc(formatValue(x))+'</li>'; }).join("")+'</ul>';
  else out+='<p>The genus-level diagnostic module is still being expanded. Use the species set and comparison key below in the meantime.</p>';
  out+='</article></section>';
  out=out.slice(0,sharedStart)+studyDrawer("Why this family & genus?","Shared structure, family clues and exceptions.",out.slice(sharedStart),"terms");
  const priorityStart=out.length;
  if(priority.length){
    out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Species-level characters</div><h2>Look here to separate '+esc(genus)+' species</h2></div></div><div class="diagnostic-chip-grid">';
    priority.forEach(function(x){ out+='<div>'+esc(formatValue(x))+'</div>'; });
    out+='</div></section>';
  }
  if(out.length>priorityStart) out=out.slice(0,priorityStart)+studyDrawer("Which features separate these species?","Inspect leaf, flower and fruit differences supported by the genus lesson.",out.slice(priorityStart),"terms","genusPriority");
  out+=studyDrawer("Photo comparisons","Compare the actual distinguishing plant parts.",genusVisualComparison(data),"photo");
  out+=studyDrawer("Detailed comparison notes","All existing diagnostic comparisons.",genusTextComparisons(data),"compare");
  const quickStart=out.length;
  if(quick.length){
    out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Quick separation key</div><h2>Character → likely species</h2></div></div><div class="genus-key">';
    quick.forEach(function(row){ out+='<div><span>'+esc(row.if)+'</span><b>→</b><strong><i>'+esc(row.then)+'</i></strong></div>'; });
    out+='</div></section>';
  }
  if(out.length>quickStart) out=out.slice(0,quickStart)+studyDrawer("Quick separation key","Character by character, find the likely species.",out.slice(quickStart),"compare");
  const genusSpeciesStart=out.length;
  out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Drill down</div><h2>'+esc(genus)+' species in the learner</h2></div></div><div class="species-tile-grid">';
  if(members.length) members.forEach(function(sp){ out+=speciesTile(sp,true); });
  else out+='<div class="empty-panel">No canonical species are installed for this genus yet.</div>';
  out+='</div></section>';
  out=out.slice(0,genusSpeciesStart)+studyDrawer("Explore species photos",members.length+" species in this genus.",out.slice(genusSpeciesStart),"photo","genusSpecies");
  out+=studyDrawer("Compare two species","Open a side-by-side field test.",genusComparePanel(genus,members),"compare");
  out+='</div>';
  return out;
}
/* Main swipe carousel uses the SAME vetted original-image marker coordinates
   as the species diagnostic lesson. Do not assign the markers to look-alike
   photos or guess at photo coordinate scaling. */
/* A named Phragmites subspecies photo still belongs to its parent species'
   learning guide, but cannot establish genetics for a field specimen.
   Only match the precise taxon prefix; NEVER transfer Arundo look-alike arrows. */
function matchesOwnSpeciesOrNamedSubspecies(sp,item){
  const name=String(item&&item.scientific_name||"");
  const species=scientificName(sp);
  return name===species || name.startsWith(species+" subsp. ");
}
function galleryMarkersFor(sp,img){
  const panels=sp && sp.visual_comparison && sp.visual_comparison.items;
  if(!Array.isArray(panels)||!img)return [];
  const src=imagePath(sp,img);
  const source=String(img.source_page||"").trim();
  const candidates=panels.filter(function(p){
    return p && matchesOwnSpeciesOrNamedSubspecies(sp,p) &&
      Array.isArray(p.markers) && p.markers.length;
  });
  const normalized=function(v){return String(v||"").split("?")[0].replace(/%2C/gi,",");};
  // Exact photo file is definitive: multiple different images may share one GBIF
  // occurrence/source page. Never reuse another photo's anatomical arrow map.
  let match=candidates.find(function(p){return normalized(p.image_url)===normalized(src);});
  if(!match && source){
    const sameSource=candidates.filter(function(p){return String(p.source_page||"").trim()===source;});
    if(sameSource.length===1)match=sameSource[0];
  }
  if(!match)return [];
  return match.markers.filter(function(m){
    return m && typeof m.label==="string" && m.label.trim() &&
      ["label_x","label_y","target_x","target_y"].every(function(k){
        return Number.isFinite(Number(m[k])) && Number(m[k])>=0 && Number(m[k])<=100;
      });
  });
}
function galleryArrowOverlay(sp,markers){
  if(!markers.length)return "";
  const arrowId="swipeArrow"+String(sp.id||"plant").replace(/[^a-z0-9]/gi,"");
  let html='<div class="gallery-arrow-stage" data-gallery-arrow-stage hidden>'+
    '<svg class="gallery-arrow-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'+
    '<defs><marker id="'+arrowId+'" markerUnits="userSpaceOnUse" markerWidth="1.8" markerHeight="1.8" refX="1.6" refY=".9" orient="auto">'+
    '<path d="M0,0 L1.8,.9 L0,1.8 z"></path></marker></defs>';
  markers.forEach(function(m){
    html+='<line x1="'+Number(m.label_x)+'" y1="'+Number(m.label_y)+
      '" x2="'+Number(m.target_x)+'" y2="'+Number(m.target_y)+
      '" marker-end="url(#'+arrowId+')"></line>';
  });
  html+='</svg>';
  markers.forEach(function(m){
    html+='<span class="gallery-arrow-label" style="left:'+Number(m.label_x)+
      '%;top:'+Number(m.label_y)+'%">'+esc(m.label)+'</span>';
  });
  return html+'</div>';
}
/* Photo element uses object-fit: contain. Place the arrow stage exactly on
   the rendered image rectangle, NOT on the letterboxed button background. */
function positionGalleryArrowStages(){
  document.querySelectorAll(".focus-photo-image [data-gallery-arrow-stage]").forEach(function(stage){
    const button=stage.parentElement,photo=button&&button.querySelector("img[data-gallery-image]");
    if(!photo||!photo.naturalWidth||!photo.naturalHeight||!photo.clientWidth||!photo.clientHeight){
      stage.hidden=true;return;
    }
    const scale=Math.min(photo.clientWidth/photo.naturalWidth,photo.clientHeight/photo.naturalHeight);
    const width=photo.naturalWidth*scale,height=photo.naturalHeight*scale;
    stage.style.left=((photo.clientWidth-width)/2)+"px";
    stage.style.top=(photo.offsetTop+(photo.clientHeight-height)/2)+"px";
    stage.style.width=width+"px";stage.style.height=height+"px";
    stage.hidden=false;
  });
}
document.addEventListener("load",function(e){
  if(e.target && e.target.matches && e.target.matches("img[data-gallery-image]")){
    window.requestAnimationFrame(positionGalleryArrowStages);
  }
},true);
window.addEventListener("resize",positionGalleryArrowStages,{passive:true});

function photoCarousel(sp){
  const imgs=galleryImagesFor(sp);
  if(!imgs.length) return '<div class="focus-photo-empty">No curated photo installed yet.</div>';
  const order=galleryPhotoOrder(sp), best=order[0];
  let idx=state.photoIndex[sp.id]===undefined?best:state.photoIndex[sp.id];
  if(!Number.isInteger(idx)||idx<0||idx>=imgs.length) idx=best;
  state.photoIndex[sp.id]=idx;
  const position=order.indexOf(idx), img=imgs[idx];
  const role=img.role||img.view||"Curated study image";
  const credit=[img.creator||img.credit,img.license].filter(Boolean).join(" · ");
  const vetted=Boolean(img.visual_role_reviewed || img.diagnostic_role_verified || img.annotation_verified);
  const diagnostic=galleryPhotoScore(img)>=53;
  const check=diagnostic?anatomyFieldCue(sp,role):"";
  const sourceKind=img.external_reference?"Externally hosted licensed photo (not downloaded)":"Installed learner photo";
  const markers=galleryMarkersFor(sp,img);
  let out='<div class="species-gallery">'+
    '<div class="gallery-study-intro"><b>'+(diagnostic?"Diagnostic study view":"Plant overview / reference")+'</b>'+
    '<span>'+(diagnostic?"Inspect the named structures, then confirm against another view.":"Swipe or tap a thumbnail to inspect another plant structure.")+'</span></div>'+
    '<figure class="focus-photo"><button class="focus-photo-image" type="button" data-photo-step="1" aria-label="Next photo"><img data-gallery-image src="'+imagePath(sp,img)+'" alt="'+esc(scientificName(sp))+' — '+esc(role)+'">'+galleryArrowOverlay(sp,markers)+'</button>'+
    '<div class="photo-topline"><span>'+esc(role)+'</span><b>'+(position+1)+' / '+imgs.length+'</b></div>';
  if(imgs.length>1) out+='<button class="photo-arrow prev" type="button" data-photo-step="-1" aria-label="Previous photo">‹</button><button class="photo-arrow next" type="button" data-photo-step="1" aria-label="Next photo">›</button>';
  out+='<figcaption class="gallery-photo-caption">'+
    (markers.length?'<strong>↗ '+markers.length+' anatomy arrow'+(markers.length===1?"":"s")+' on this photograph</strong>':'')+
    (check?'<strong>Look for:</strong> '+esc(check)+(markers.length?'<small>Compare this field clue with the marked structures.</small>':'<small>Based on the species record; this particular photograph has no anatomy arrows.</small>'):"")+
    '<span>'+esc(sourceKind)+(vetted?" · Study role reviewed":"")+'</span>'+
    '<span>'+esc(credit||"Source metadata retained in species record")+'</span>'+
    (img.source_page?'<a href="'+esc(img.source_page)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':"")+ (img.license_url?'<a href="'+esc(img.license_url)+'" target="_blank" rel="noopener noreferrer">Image license ↗</a>':"")+
    '</figcaption></figure>';
  if(imgs.length>1){
    out+='<div class="photo-filmstrip" role="group" aria-label="Choose a plant photo">';
    order.forEach(function(actualIndex,rank){
      const photo=imgs[actualIndex],label=photo.role||photo.view||("Photo "+(rank+1));
      const note=galleryMarkersFor(sp,photo).length?"↗ Annotated · ":"";
      out+='<button type="button" class="photo-thumbnail'+(actualIndex===idx?' active':'')+'" data-photo-index="'+actualIndex+'" aria-pressed="'+String(actualIndex===idx)+'" aria-label="Show photo '+(rank+1)+' of '+imgs.length+': '+esc(note+label)+'">'+
        '<img src="'+imagePath(sp,photo)+'" alt="" loading="lazy"><span>'+esc(note+label)+'</span></button>';
    });
    out+='</div>';
  }
  return out+'</div>';
}
function identityPanel(sp){
  if(state.quizMode && !state.quizRevealed){
    return '<div class="identity-panel mystery"><div class="eyebrow">Quiz mode</div><h1>Mystery plant</h1><p>Use the photo sequence and field characters before revealing the name.</p>'+
      '<button class="primary-button" type="button" data-reveal-quiz>Reveal identification</button></div>';
  }
  return '<div class="identity-panel"><div class="eyebrow">'+esc(sp.family)+' › '+esc(sp.genus)+'</div><h1><i>'+esc(scientificName(sp))+'</i></h1>'+
    '<p class="plant-common">'+esc(commonName(sp))+'</p>'+encounterBadge(sp)+(sp.authority?'<p class="authority">'+esc(sp.authority)+'</p>':'')+
    (state.quizMode?'<button class="text-button" type="button" data-next-quiz>Next mystery plant →</button>':'')+'</div>';
}
function similarCard(base,other,reason){
  return '<article class="similar-card"><button class="similar-open" type="button" data-species="'+other.id+'">'+thumb(other,"similar-thumb")+
    '<span class="comparison-reason">'+esc(reason)+'</span><strong><i>'+esc(scientificName(other))+'</i></strong><em>'+esc(commonName(other))+'</em></button>'+
    '<button class="compare-button" type="button" data-compare="'+base.id+'|'+other.id+'">Compare side by side</button></article>';
}
function structuredTeachingHTML(value){
  if(Array.isArray(value)) return '<ul>'+value.map(function(v){ return '<li>'+esc(formatValue(v))+'</li>'; }).join("")+'</ul>';
  if(value && typeof value==="object"){
    return '<div class="structured-list">'+Object.entries(value).map(function(p){ return '<div><b>'+esc(titleCase(p[0]))+'</b><span>'+esc(formatValue(p[1]))+'</span></div>'; }).join("")+'</div>';
  }
  return '<p>'+esc(formatValue(value))+'</p>';
}
function familyVisualThumb(sp,step,cls){
  const external=familyExternalImageUrl(step);
  if(external) return '<img class="'+cls+'" src="'+esc(external)+'" alt="'+esc((step&&step.photo_role)||scientificName(sp))+'" loading="lazy">';
  const imgs=imagesFor(sp);
  let idx=Number(step && step.anchor_image_index);
  if(!Number.isInteger(idx) || idx<0 || idx>=imgs.length) idx=0;
  const img=imgs[idx] || null;
  if(img) return '<img class="'+cls+'" src="'+imagePath(sp,img)+'" alt="'+esc((step&&step.photo_role)||scientificName(sp))+'" loading="lazy">';
  return '<div class="'+cls+' thumb-empty" aria-hidden="true">✣</div>';
}

function familyExternalImageUrl(step){
  if(!step) return "";
  if(step.image_url) return step.image_url;
  const src=step.source_page||"";
  if(/^https?:\/\/commons\.wikimedia\.org\/wiki\/File:/i.test(src)){
    return src.replace("/wiki/File:","/wiki/Special:Redirect/file/");
  }
  return "";
}

function familyExternalVisual(step){
  const url=familyExternalImageUrl(step);
  if(!url) return "";
  const label=step.image_label||step.photo_role||"Reference image";
  const img='<img class="family-visual-img" src="'+esc(url)+'" alt="'+esc(step.image_alt||label)+'" loading="lazy">';
  const caption='<span><b>'+esc(label)+'</b><i>'+esc(step.image_credit||"rights-cleared reference")+'</i></span>';
  if(step.source_page) return '<a class="family-visual-photo" href="'+esc(step.source_page)+'" target="_blank" rel="noopener noreferrer">'+img+caption+'</a>';
  return '<div class="family-visual-photo">'+img+caption+'</div>';
}

function familyVisualStepCard(step,index){
  const sp=step.anchor_species_id ? state.species.find(function(x){return x.id===step.anchor_species_id;}) : null;
  const external=Boolean(familyExternalImageUrl(step));
  const imgs=sp?imagesFor(sp):[];
  const indexNumber=Number(step.anchor_image_index);
  const selected=Number.isInteger(indexNumber)&&indexNumber>=0&&indexNumber<imgs.length?imgs[indexNumber]:imgs[0];
  const photoCredit=external?(step.image_credit||""):[selected&&selected.creator,selected&&selected.license].filter(Boolean).join(" · ") || step.image_credit||"";
  const role=step.photo_role||step.title||"Study structure";
  const clue=String(step.look_for||"").trim();
  const why=String(step.why_it_matters||"").trim();
  const longer=clue.length>220;
  const preview=longer?(clue.slice(0,200).replace(/\s+\S*$/,"").trim()||clue.slice(0,200))+"…":clue;
  const whyLong=why.length>200;
  const whyPreview=whyLong?(why.slice(0,185).replace(/\s+\S*$/,"").trim()||why.slice(0,185))+"…":why;
  const source=step.source_page&&/^https?:\/\//i.test(step.source_page)?'<a href="'+esc(step.source_page)+'" target="_blank" rel="noopener noreferrer">Photo / lesson source ↗</a>':"";
  let out='<article class="family-visual-step family-anatomy-lesson"><div class="family-study-stepnum">Look '+(index+1)+'</div>';
  if(sp){
    out+='<button class="family-visual-photo" type="button" data-species="'+esc(sp.id)+'">'+familyVisualThumb(sp,step,"family-visual-img")+
      '<span><b>'+esc(commonName(sp)||scientificName(sp))+'</b><i>'+esc(scientificName(sp))+'</i></span></button>';
  }else if(external){
    out+=familyExternalVisual(step);
  }else{
    out+='<div class="family-visual-photo family-visual-placeholder"><span>Diagram / photo lock pending</span></div>';
  }
  out+='<div class="family-visual-copy"><div class="family-visual-step-title">'+esc(step.title||step.photo_role||"Look here")+'</div>'+
    (step.photo_role?'<small>'+esc(step.photo_role)+'</small>':"")+
    '<div class="family-anatomy-steps">'+
      anatomyTeachingSentence("1 · Where to look",anatomyWhereToLook(role))+
      anatomyTeachingSentence("2 · What to check",preview||"Check the original visual lesson for the intended structural character.")+
      anatomyTeachingSentence("3 · Why it matters",whyPreview||"Confirm this character alongside another reliable family or genus trait.")+
    '</div>';
  if(longer||whyLong) out+='<details class="family-why-detail"><summary>Read the complete botanical explanation</summary>'+
    (longer?'<p><b>Complete observation:</b> '+esc(clue)+'</p>':"")+
    (whyLong?'<p><b>Complete reasoning:</b> '+esc(why)+'</p>':"")+'</details>';
  out+='<div class="family-study-source"><b>'+esc(external?"External image reference":selected?"Gallery-linked example":"Photo still needed")+'</b>'+
    (sp?'<span>Photographed plant: <i>'+esc(scientificName(sp))+'</i></span>':"")+
    (photoCredit?'<small>'+esc(photoCredit)+'</small>':"")+
    (source?'<span>'+source+'</span>':"")+
    '<small>Unannotated imagery is an inspection reference, not verification that the named part is visible.</small></div>';
  if(step.status && /pending/i.test(step.status)) out+='<em class="visual-lock-status">Visual polish pending</em>';
  return out+'</div></article>';
}
function familyVisualLessonHTML(canon){
  const lesson=canon && canon.visual_lesson;
  if(!lesson || !Array.isArray(lesson.steps) || !lesson.steps.length) return "";
  const first=lesson.steps.slice(0,3), later=lesson.steps.slice(3);
  let out='<section class="family-visual-lesson"><div class="family-visual-heading"><div><div class="eyebrow">Visual family lesson</div><h3>Learn the family pattern one structure at a time</h3></div><span>'+esc(lesson.status||"visual lesson")+'</span></div>';
  if(lesson.intro) out+='<p class="family-visual-intro">'+esc(lesson.intro)+'</p>';
  out+='<p class="family-study-guidance">Start with these examples. Tap the image to explore the plant, then open the explanation to learn why that character matters.</p>';
  out+='<div class="family-visual-steps">'+first.map(familyVisualStepCard).join("")+'</div>';
  if(later.length) out+='<details class="family-more-photo-steps"><summary><strong>Explore '+later.length+' more family structures</strong><span>Additional photographic lessons and identification clues ⌄</span></summary><div class="family-visual-steps">'+later.map(function(step,i){return familyVisualStepCard(step,i+first.length);}).join("")+'</div></details>';
  if(Array.isArray(lesson.comparisons) && lesson.comparisons.length){
    out+='<details class="family-tie-breakers"><summary>Compare with similar families · '+lesson.comparisons.length+' tie-breakers</summary><div class="family-visual-comparisons"><h4>Fast tie-breakers</h4>';
    lesson.comparisons.forEach(function(c){out+='<div><b>'+esc(c.title||"Compare")+'</b><span>'+esc(c.rule||"")+'</span></div>';});
    out+='</div></details>';
  }
  if(lesson.caveat) out+='<p class="modal-caveat"><b>Visual lesson note:</b> '+esc(lesson.caveat)+'</p>';
  return out+'</section>';
}

function termsInText(text,max){
  const out=[];
  Object.entries(state.learning.terms).forEach(function(pair){ if(out.length<max && termMatches(pair[1],text)) out.push(pair[0]); });
  return out;
}
function fieldBotanySection(sp,genusData){
  const rows=Object.entries(sp.morphology_keys||{}).filter(function(p){ return !["best_field_traits","high_value_field_traits"].includes(p[0]); });
  const strategy=genusData && (genusData.study_strategy || genusData.genus_diagnostics || genusData.high_value_field_traits);
  let out='<section class="section-block technical-section"><div class="section-heading"><div><div class="eyebrow">Field botany</div><h2>Technical morphology</h2></div></div><div class="morphology-grid">';
  rows.forEach(function(p){
    const ids=termsInText(titleCase(p[0])+" "+formatValue(p[1]),3);
    out+='<article class="morph-card"><b>'+esc(titleCase(p[0]))+'</b><p>'+esc(formatValue(p[1]))+'</p>'+(ids.length?'<div class="mini-terms">'+ids.map(termChip).join("")+'</div>':'')+'</article>';
  });
  out+='</div>';
  if(strategy) out+='<details class="genus-strategy"><summary>How to study <i>'+esc(sp.genus)+'</i> as a genus</summary><div>'+structuredTeachingHTML(strategy)+'</div></details>';
  out+='</section>';
  return out;
}
/* Photo-first taxonomy examples. Images are illustrative, never a claim of unverified anatomy. */
function taxonomyRoleText(img){
  return String([img.role,img.view,img.caption,img.image_role,img.diagnostic_roles].filter(Boolean).join(" ")).toLowerCase();
}
function taxonomyPhotoPriority(rank,detail){
  const cue=String(detail||"").toLowerCase();
  const families=[
    {words:/leaf|foliage|blade|petiole|phyllotaxy|venation|margin|apex/,roles:["leaf","leaves","foliage","node","stem"]},
    {words:/acorn|cupule|cup|nut|seed|fruit|follicle|pod|berry/,roles:["acorn","cupule","fruit","follicle","seed","pod","nut"]},
    {words:/bud|twig|bark|prickle|thorn/,roles:["bud","twig","bark","stem"]},
    {words:/phyllar|capitul|floret|inflorescen|umbel|spike|head/,roles:["phyllar","flower-head","floret","head","inflorescence","umbel","flower"]},
    {words:/flower|corolla|petal|anther|stamen|corona|hood|horn|gynostegium|receptacle|ligule|calyx|sepal/,roles:["flower macro","flower close","flower","reproductive","floral"]}
  ];
  const match=families.find(function(group){ return group.words.test(cue); });
  if(match) return match.roles.concat(["diagnostic","macro","close-up","habit"]);
  if(rank==="species") return ["diagnostic","macro","leaf","leaves","flower","fruit","habit"];
  if(rank==="genus") return ["flower macro","flower close","flower","inflorescence","fruit","leaves","diagnostic","habit"];
  return ["flower","inflorescence","habit","leaves","fruit","diagnostic"];
}
function taxonomyPickPhoto(sp,rank,detail,preferredIndex,usedPhotos){
  if(!sp) return null;
  const gallery=imagesFor(sp).filter(function(img){ return !/^(javascript|data|file):/i.test(String(img.file)); });
  if(!gallery.length) return null;
  const hints=taxonomyPhotoPriority(rank,detail);
  const specified=Number(preferredIndex);
  let chosen=null;
  if(preferredIndex!==undefined && preferredIndex!==null && Number.isInteger(specified) && specified>=0 && specified<gallery.length){
    chosen=gallery[specified];
  }else{
    const ranked=gallery.map(function(img,index){
      const role=taxonomyRoleText(img);
      let score=0;
      hints.forEach(function(hint,i){ if(role.includes(hint)) score=Math.max(score,40-i*2); });
      // Real diagnostic close-ups are preferred over pretty but uninformative portraits.
      if(/macro|close-up|diagnostic/.test(role)) score+=3;
      // Installed local media is more reliable than a hotlinked reference image.
      if(!/^https?:\/\//i.test(String(img.file))) score+=60;
      // Different taxonomic ranks should show different plant views when available.
      if(usedPhotos && usedPhotos.has(imagePath(sp,img))) score-=250;
      return {img:img,index:index,score:score};
    }).sort(function(a,b){ return b.score-a.score || a.index-b.index; });
    chosen=ranked[0].img;
  }
  return {species:sp,img:chosen,role:chosen.role||chosen.view||"Plant reference",src:imagePath(sp,chosen)};
}
function taxonomyTeachingPhoto(sp,rank,detail,familyData,usedPhotos){
  let picked=null,step=null,linkedRank=rank;
  const lesson=familyData && familyData.visual_lesson;
  if((rank==="family" || rank==="order") && lesson && Array.isArray(lesson.steps)){
    for(const candidate of lesson.steps){
      if(!candidate || !candidate.anchor_species_id || /pending/i.test(String(candidate.status||""))) continue;
      const representative=state.speciesById.get(candidate.anchor_species_id);
      if(!representative || !imagesFor(representative).length) continue;
      picked=taxonomyPickPhoto(representative,"family",candidate.photo_role||detail,candidate.anchor_image_index,usedPhotos);
      if(picked){ step=candidate;break; }
    }
  }
  if(!picked){
    let representative=sp;
    if(rank==="genus" && !imagesFor(sp).length){
      representative=genusSpecies(sp.family,sp.genus).find(function(x){return imagesFor(x).length;})||sp;
    }
    if((rank==="family" || rank==="order") && !imagesFor(representative).length){
      representative=familySpecies(sp.family).find(function(x){return imagesFor(x).length;})||sp;
    }
    picked=taxonomyPickPhoto(representative,rank,detail,null,usedPhotos);
  }
  if(!picked) return '<div class="taxonomy-teaching-photo-empty"><span aria-hidden="true">✣</span><strong>Photo example needed</strong><small>The identification clues below are still available.</small></div>';
  if(usedPhotos) usedPhotos.add(picked.src);
  const photo=picked.img, photoSp=picked.species;
  const recordedRole=String(picked.role||"Plant reference");
  const caption=step && step.image_label ? step.image_label : recordedRole;
  const credit=[photo.creator||photo.credit,photo.license].filter(Boolean).join(" · ");
  // Link only the chosen image's actual source, not a different family-lesson reference.
  const page=photo.source_page||"";
  const isRepresentative=photoSp.id!==sp.id;
  const title=(rank==="species"?"Species study view":rank==="genus"?"Genus example":rank==="order"?"Related family example":"Family example");
  const note=(isRepresentative?"Representative: "+scientificName(photoSp)+" · ":"")+caption;
  const description=scientificName(photoSp)+" — "+recordedRole+". Teaching example; inspect the written clues for diagnostic evidence.";
  return '<figure class="taxonomy-teaching-media">'+
    '<img src="'+esc(picked.src)+'" alt="'+esc(description)+'" loading="lazy" decoding="async">'+
    '<figcaption><b>'+esc(title)+'</b><span>'+esc(note)+'</span>'+
      (credit?'<small>'+esc(credit)+'</small>':'<small>Photo attribution not recorded in this entry</small>')+
      (page && /^https?:\/\//i.test(page)?'<a href="'+esc(page)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':'')+
    '</figcaption></figure>';
}

/* Presentation-only name/relationship lesson. Canonical ranks and ID evidence stay in their source modules. */
function taxonomyTeachingTrail(sp,genusData,profile,callouts){
  const familyData=state.familyCache.get(sp.family)||{};
  const familyDiagnostics=familyData.family_diagnostics||{};
  const familyClue=callouts.family_connection||profile.look_here_first||profile.plain_signature||
    familyDiagnostics.where_to_look_first||familyDiagnostics.field_tip||
    "Open this family lesson to learn its shared structures and important exceptions.";
  const genusTraits=genusSharedTraits(genusData);
  const genusClue=(genusData && (genusData.look_here_first ||
    (genusData.study_strategy && genusData.study_strategy.look_here_first))) ||
    (genusData && genusData.genus_diagnostics && (
      genusData.genus_diagnostics.flower || genusData.genus_diagnostics.inflorescence ||
      genusData.genus_diagnostics.fruit || genusData.genus_diagnostics.leaves)) ||
    (genusTraits.length?genusTraits[0]:"The genus lesson is still being expanded. Open it to compare shared traits across close relatives.");
  const speciesClue=callouts.standout||lookHereFirst(sp);
  const order=[sp.order,genusData&&genusData.order,familyData.order].find(function(value){
    return typeof value==="string" && value.trim();
  });
  const ranks=[];
  if(order){
    const orderHint=(familyData.order_diagnostics && typeof familyData.order_diagnostics==="string")?
      familyData.order_diagnostics:"This broader evolutionary group includes multiple families. Its identifying traits need to be checked at the family and genus levels.";
    ranks.push({rank:"Order",name:order,detail:orderHint,helper:"Broader group",tone:"order"});
  }
  ranks.push({rank:"Family",name:sp.family,detail:familyClue,helper:"Shared family architecture",tone:"family",open:'data-family="'+esc(sp.family)+'"',action:"Explore family"});
  ranks.push({rank:"Genus",name:sp.genus,detail:genusClue,helper:"What close relatives share",tone:"genus",open:'data-genus="'+esc(sp.genus)+'" data-genus-family="'+esc(sp.family)+'"',action:"Explore genus",italic:true});
  ranks.push({rank:"Species",name:scientificName(sp),detail:speciesClue,helper:"What separates this plant",tone:"species",italic:true});
  let out='<section id="taxonomySection" class="section-block taxonomy-teaching" aria-labelledby="taxonomyTeachingTitle">'+
    '<div class="section-heading"><div><div class="eyebrow">Name detective · follow the clues</div>'+
    '<h2 id="taxonomyTeachingTitle">Why does this plant have that name?</h2></div></div>'+
    '<p class="section-intro">Follow the classification from broader relatives to this species. Each image is a representative study view; use the written clues and detailed lessons to verify individual structures.</p>'+
    '<div class="taxonomy-teaching-grid">';
  const usedTaxonomyPhotos=new Set();
  ranks.forEach(function(rank,index){
    out+='<article class="taxonomy-teaching-card taxonomy-teaching-'+rank.tone+'">'+
      taxonomyTeachingPhoto(sp,rank.tone,rank.detail,familyData,usedTaxonomyPhotos)+
      '<div class="taxonomy-teaching-head"><span class="taxonomy-teaching-number">'+String(index+1).padStart(2,"0")+'</span>'+
      '<span><small>'+esc(rank.rank)+' · '+esc(rank.helper)+'</small><strong>'+(rank.italic?'<i>'+esc(rank.name)+'</i>':esc(rank.name))+'</strong></span></div>'+
      '<div class="taxonomy-teaching-body"><b>Look for</b><p>'+clueWithTerms(rank.detail)+'</p></div>'+
      (rank.open?'<button class="taxonomy-teaching-link" type="button" '+rank.open+'>'+rank.action+' <span aria-hidden="true">→</span></button>':
        '<span class="taxonomy-teaching-note">'+(rank.tone==="species"?"Now compare it with look-alikes ↓":"A broader classification level")+'</span>')+
      '</article>';
  });
  out+='</div><p class="taxonomy-teaching-footnote"><b>Read the name:</b> <i>'+esc(sp.genus)+'</i> names the genus, <i>'+esc(scientificName(sp))+'</i> names the species, and '+
    '<b>'+esc(sp.family)+'</b> names the family. Most botanical family names end in <b>-aceae</b>. Tap the highlighted botanical words above for examples.</p></section>';
  return out;
}


/* Multi-view visual field guide. Source-derived descriptions; photographs are unannotated until verified. */
function botanyPartLabel(raw){
  const v=String(raw||"").trim().toLowerCase();
  if(/corona|hood/.test(v)) return "Corona and hoods";
  if(/gynostegium/.test(v)) return "Flower center";
  if(/pollin/.test(v)) return "Pollen structures";
  if(/inflorescen|umbel/.test(v)) return "Flower cluster";
  if(/fruit|follicle|pod|acorn|cupule/.test(v)) return "Fruit and seed";
  if(/leaf|leaves|foliage|venation|phyllotaxy/.test(v)) return "Leaves and attachment";
  if(/stem|bud|bark|twig/.test(v)) return "Stem, twig or buds";
  if(/latex|sap/.test(v)) return "Sap and latex";
  if(/habit/.test(v)) return "Whole plant";
  if(/flower|corolla|stamen|calyx|anther/.test(v)) return "Flower anatomy";
  return titleCase(v);
}
function botanyPartPhotoPattern(raw){
  const v=String(raw||"").toLowerCase();
  if(/latex|sap/.test(v)) return /latex|sap|cut.stem|exudate/;
  if(/leaf|leaves|foliage|venation|phyllotaxy/.test(v)) return /leaves|leaf|foliage|stem.node|venation/;
  if(/fruit|follicle|pod|acorn|cupule|seed/.test(v)) return /fruit|follicle|pod|acorn|cupule|seed/;
  if(/habit/.test(v)) return /habit|whole.plant|branching/;
  if(/inflorescen|umbel/.test(v)) return /inflorescence|umbel|flower.head|flowering.plant|flower.cluster/;
  if(/stem|bud|bark|twig/.test(v)) return /stem|bud|bark|twig/;
  if(/pollinarium|pollinia/.test(v)) return /pollinarium|pollinia|pollinium|pollinator.macro/;
  return /flower|macro|corolla|calyx|corona|gynostegium|floret|hood|horn|diagnostic.close/;
}
function botanyPartPhoto(sp,part,usedPhotos,related){
  const pattern=botanyPartPhotoPattern(part);
  const candidates=[sp].concat(related||[]);
  const possible=[];
  const seen=new Set();
  candidates.forEach(function(candidate,index){
    if(!candidate || seen.has(candidate.id)) return;
    seen.add(candidate.id);
    imagesFor(candidate).forEach(function(img,ix){
      if(index>0 && /^(no|review|private|restricted)$/i.test(String(img.public_reuse||"").trim())) return;
      const role=String([img.role,img.view,img.image_role,img.caption].filter(Boolean).join(" "));
      if(!pattern.test(role.toLowerCase())) return;
      const src=imagePath(candidate,img);
      if(!src) return;
      let score=(index===0?12:0)+(usedPhotos&&usedPhotos.has(src)?-22:14)+(/https?:\/\//.test(src)?0:5);
      const k=String(part).toLowerCase();
      if(role.toLowerCase().includes(k)) score+=20;
      if(/macro|close-up/.test(role.toLowerCase())) score+=3;
      possible.push({species:candidate,img:img,src:src,score:score,order:ix});
    });
  });
  possible.sort(function(a,b){return b.score-a.score || a.order-b.order;});
  const result=possible[0]||null;
  if(result && usedPhotos)usedPhotos.add(result.src);
  return result;
}

/* Reusable observation-led anatomy cards. Source text remains authoritative:
   photo roles guide where to inspect; no unverified annotation is asserted. */
function anatomyWhereToLook(role){
  const v=String(role||"").toLowerCase();
  if(/phyllar|involucre|head underside|cupule/.test(v)) return "Turn the head or fruiting structure sideways and examine the structures underneath.";
  if(/leaf|foliage|venation|petiole|blade|phyllotaxy/.test(v)) return "Find a mature leaf, its base, and the point where it joins the stem.";
  if(/bud|twig|bark|stem|node/.test(v)) return "Follow a stem or twig and inspect its nodes, surface, and buds.";
  if(/fruit|follicle|seed|acorn|pod|cypsela/.test(v)) return "Look closely at mature fruit or seed structures when they are present.";
  if(/flower|floret|corolla|calyx|petal|inflorescen|umbel|corona|hood/.test(v)) return "View the flower or flower cluster from the front and side, then examine its smaller parts.";
  if(/habit|whole plant|architecture|branching/.test(v)) return "Step back to see the whole plant, then look at its branching and overall form.";
  if(/sap|latex/.test(v)) return "Find a documented view of the sap or latex character; do not rely on a general habit photograph.";
  return "Locate the named part in the photo. If the structure cannot be seen clearly, open another view.";
}
function anatomyFieldCue(sp,role){
  const m=sp&&sp.morphology_keys||{};
  const v=String(role||"").toLowerCase();
  let keys=[];
  if(/phyllar|involucre|head underside/.test(v)) keys=["phyllaries","involucre","heads"];
  else if(/leaf|vein|petiole|foliage|blade/.test(v)) keys=["leaf_venation","leaf_attachment","leaves","leaf_arrangement","leaf_morphology"];
  else if(/flower|floret|corolla|inflorescen|umbel/.test(v)) keys=["flower","flowers","inflorescence","heads","corolla"];
  else if(/fruit|seed|pod|acorn|follicle|cypsela/.test(v)) keys=["fruit","fruits","acorn","seed"];
  else if(/stem|bark|bud|twig|node/.test(v)) keys=["stem","bark","buds","habit"];
  else if(/habit|whole plant|branching/.test(v)) keys=["habit","growth_habit","life_cycle"];
  else if(/sap|latex/.test(v)) keys=["sap_type","latex"];
  const hit=keys.find(function(key){return typeof m[key]==="string" && m[key].trim();});
  return hit?m[hit]:"";
}
function anatomyNextCheck(level){
  if(level==="family") return "Next, compare this family pattern with the genus-level structures.";
  if(level==="genus") return "Next, look for a species-level difference in the plant gallery or comparison key.";
  return "Next, check the same feature in a look-alike and confirm with at least one other field character.";
}
function anatomyTeachingSentence(label,body){
  return '<div class="anatomy-teach-step"><b>'+esc(label)+'</b><p>'+esc(body)+'</p></div>';
}
function botanyPartPhotoCard(item,level){
  const name=item.title||"Examine this part";
  const photo=item.photo||null;
  const note=String(item.description||"").trim();
  const why=String(item.why||"").trim();
  const role=String(item.role || (photo&&photo.img&&photo.img.role) || name);
  const suggestedFieldCue=item.fieldCue||"";
  const fieldCue=why||suggestedFieldCue;
  const noteLong=note.length>220;
  const shortNote=noteLong?(note.slice(0,200).replace(/\s+\S*$/,"").trim()||note.slice(0,200))+"…":note;
  let media='<div class="part-example-empty" role="img" aria-label="Close-up not yet available"><span aria-hidden="true">⌕</span><strong>Close-up needed</strong></div>';
  if(photo && photo.src){
    const label=photo.species?scientificName(photo.species):"Botanical reference";
    const photoRole=(photo.img&&photo.img.role)||item.role||"Reference photograph";
    media='<button class="part-example-photo-button" type="button" data-part-preview data-part-src="'+esc(photo.src)+'" data-part-title="'+esc(name)+'" data-part-caption="'+esc(label+" · "+photoRole)+'" data-part-credit="'+esc([photo.img&&(photo.img.creator||photo.img.credit),photo.img&&photo.img.license].filter(Boolean).join(" · "))+'" aria-label="Enlarge '+esc(name)+' reference photo">'+
      '<img src="'+esc(photo.src)+'" loading="lazy" decoding="async" alt="'+esc(label+" — "+photoRole+" (unannotated study photo)")+'">'+
      '<span class="part-example-zoom-tag">Enlarge ↗</span></button>';
  }
  const source=(photo && photo.img && photo.img.source_page)||item.source||"";
  const attribution=photo && photo.img ? [photo.img.creator||photo.img.credit,photo.img.license].filter(Boolean).join(" · ") : (item.credit||"");
  const photoName=photo&&photo.species ? scientificName(photo.species) : "";
  const sourceLink=source&&/^https?:\/\//i.test(source)?'<a href="'+esc(source)+'" target="_blank" rel="noopener noreferrer">Photo source ↗</a>':"";
  const glossaryKey=item.term&&state.learning&&state.learning.terms&&state.learning.terms[item.term]?item.term:null;
  const externallyHosted=Boolean(photo&&photo.img&&(photo.img.external_reference||/^https?:\/\//i.test(String(photo.img.file||""))||/external/i.test(String(photo.img.media_storage||""))));
  const subjectLabel=photo&&photo.src ? (externallyHosted?"Externally hosted reference":photo.img&&photo.img.file?"Gallery-linked photo":"Photo reference") : "Photo still needed";
  const viewLabel=photoName ? "Photographed plant: "+photoName : "Photo subject not specified";
  const fullExtra=noteLong?'<p><b>Complete observation:</b> '+esc(note)+'</p>':"";
  const comparePrompt=anatomyNextCheck(level);
  const diagnosticText=fieldCue||"This view alone does not prove the ID. Use another documented character before deciding.";
  return '<article class="part-example-card anatomy-lesson-card">'+
    '<div class="part-example-media">'+media+'</div>'+
    '<div class="part-example-content">'+
    '<div class="part-example-title">'+(glossaryKey?'<button type="button" data-term="'+esc(glossaryKey)+'">'+esc(name)+' <span aria-hidden="true">↗</span></button>':'<strong>'+esc(name)+'</strong>')+'</div>'+
    '<div class="anatomy-photo-context"><b>'+esc(subjectLabel)+'</b><span>'+esc(viewLabel)+'</span></div>'+
    '<div class="anatomy-teach-steps">'+
       anatomyTeachingSentence("1 · Where to look",anatomyWhereToLook(role))+
       anatomyTeachingSentence("2 · What to check",shortNote||"Inspect this structure using the source photo role and the identification clues above.")+
       anatomyTeachingSentence("3 · How it helps identify",diagnosticText)+
    '</div>'+
    (noteLong?'<details class="part-example-explain"><summary>Read the complete observation</summary><div>'+fullExtra+'</div></details>':"")+
    '<details class="anatomy-next-step"><summary>What should I compare next?</summary><p>'+esc(comparePrompt)+'</p></details>'+
    '<div class="anatomy-photo-sources">'+
    (photoName&&photo.species.id?'<button class="anatomy-reference-link" type="button" data-species="'+esc(photo.species.id)+'">Study this photographed plant →</button>':"")+
    (attribution?'<small class="part-example-credit">'+esc(attribution)+'</small>':"")+
    (sourceLink?'<span class="part-example-source">'+sourceLink+'</span>':"")+
    '<small class="anatomy-photo-caution">Photo labels suggest what to investigate; no unverified arrows or structures are asserted.</small></div>'+
    '</div></article>';
}

function openPartPhotoPreview(button){
  const src=String(button.dataset.partSrc||"");
  if(!/^(https?:\/\/|content\/)/i.test(src)) return;
  const heading=button.dataset.partTitle||"Botanical photo";
  const caption=button.dataset.partCaption||"Unannotated real-plant reference";
  const credit=button.dataset.partCredit||"";
  els.modal.innerHTML='<div class="modal-backdrop" data-close-modal><section class="modal-card part-photo-modal" role="dialog" aria-modal="true" aria-labelledby="partPhotoTitle">'+
    '<button class="modal-close" type="button" data-close-modal aria-label="Close photo">×</button>'+
    '<h2 id="partPhotoTitle">'+esc(heading)+'</h2>'+
    '<div class="part-photo-zoom"><img src="'+esc(src)+'" alt="'+esc(caption)+'" loading="eager"></div>'+
    '<p>'+esc(caption)+'</p>'+
    (credit?'<small>'+esc(credit)+'</small>':'')+
    '<p class="part-modal-caveat">Unannotated study photograph. Arrows will only be added after individual structures are visually checked.</p>'+
    '</section></div>';
}
function botanyPartGroup(rank,label,subtext,items,button,cue){
  if(!items || !items.length) return "";
  const number=rank==="family"?"01":rank==="genus"?"02":"03";
  const group=rank==="family"?"Family":rank==="genus"?"Genus":"Species";
  const name=String(label||"").replace(/^(Family|Genus|Species)\s*·\s*/i,"");
  const fieldCue=cue ? '<div class="part-gallery-practice"><b>Where to look first</b><p>'+esc(formatValue(cue))+'</p><small>Use photographs as study examples. Confirm any diagnostic character from the written description before assigning an ID.</small></div>' : "";
  const first=items.slice(0,2),later=items.slice(2);
  return '<details class="part-gallery-group part-gallery-'+rank+'">'+
    '<summary><span class="part-gallery-marker" aria-hidden="true">'+number+'</span>'+
    '<span class="part-gallery-summary"><small class="part-gallery-level">'+group+' · Step '+Number(number)+'</small>'+
    '<strong>'+(rank==="family"?esc(name):'<i>'+esc(name)+'</i>')+'</strong>'+
    '<small class="part-gallery-description">'+esc(subtext)+'</small></span>'+
    '<span class="part-gallery-count"><b>'+items.length+' study parts</b><span aria-hidden="true">⌄</span></span></summary>'+
    fieldCue+'<div class="part-example-grid">'+first.map(function(item){return botanyPartPhotoCard(item,rank);}).join("")+'</div>'+
    (later.length?'<details class="anatomy-more-views"><summary>Explore '+later.length+' additional study views ⌄</summary><div class="part-example-grid">'+later.map(function(item){return botanyPartPhotoCard(item,rank);}).join("")+'</div></details>':"")+
    (button||"")+'</details>';
}

/* Optional exact-species part examples selected by curators after inspecting real gallery files.
   Unmapped parts deliberately remain as missing-photo cards; don't substitute similar-looking taxa. */
function botanyExactGenusParts(genusData){
  const entries=genusData&&genusData.visual_comparison&&genusData.visual_comparison.part_examples;
  if(!Array.isArray(entries)||!entries.length)return [];
  return entries.slice(0,9).map(function(entry){
    let picked=null;
    if(entry.anchor_species_id && entry.image_file){
      const host=state.speciesById.get(entry.anchor_species_id);
      if(host && host.family===genusData.family && host.genus===genusData.name){
        const img=imagesFor(host).find(function(candidate){return candidate.file===entry.image_file;});
        if(img)picked={species:host,img:img,src:imagePath(host,img)};
      }
    }
    return {title:entry.title||"Study this part",description:entry.look_for||"",why:entry.why_it_matters||"",
      role:entry.role||"",photo:picked,source:entry.source_page||""};
  });
}
function botanyGenusPartPreview(members,genusData){
  if(!genusData || !members || !members.length) return "";
  const explicit=botanyExactGenusParts(genusData);
  const traits=genusData.genus_diagnostics||{};
  const keys=Object.keys(traits);
  const order=["flower","corona","gynostegium","inflorescence","leaves","leaf","fruit","bud","stem","habit","latex"];
  keys.sort(function(a,b){
    const ia=order.indexOf(a),ib=order.indexOf(b);
    return (ia<0?100:ia)-(ib<0?100:ib);
  });
  const anchor=members.find(function(sp){return imagesFor(sp).length;})||members[0];
  const used=new Set();
  let cards=explicit.length?explicit:keys.slice(0,6).map(function(key){
    const photo=botanyPartPhoto(anchor,key,used,members.filter(function(sp){return sp.id!==anchor.id;}));
    return {title:botanyPartLabel(key),description:formatValue(traits[key]),term:state.learning&&state.learning.terms&&state.learning.terms[key]?key:null,photo:photo,role:key};
  });
  if(!cards.length)cards=imagesFor(anchor).slice(0,5).map(function(img){
    return {title:botanyPartLabel(img.role||"Study image"),description:"Compare this view among the species below.",photo:{species:anchor,img:img,src:imagePath(anchor,img)}};
  });
  if(!cards.length)return "";
  return '<section class="section-block botany-genus-preview">'+
    '<div class="section-heading"><div><div class="eyebrow">Learning with real plant images</div><h2>What parts help recognize <i>'+esc(genusData.name||anchor.genus)+'</i>?</h2></div></div>'+
    '<p class="section-intro">Explore the structures that define the genus. Photo labels are unannotated examples; arrows will be added after verifying each structure.</p>'+
    '<p class="genus-photo-guidance">Examine the first three structures. The name of the photographed plant stays visible so a representative family or genus photo is not mistaken for this exact species.</p>'+
    '<div class="part-example-grid">'+cards.slice(0,3).map(function(item){return botanyPartPhotoCard(item,"genus");}).join("")+'</div>'+
    (cards.length>3?'<details class="genus-more-photo-steps"><summary>Show '+(cards.length-3)+' more structure examples ⌄</summary><div class="part-example-grid">'+cards.slice(3).map(function(item){return botanyPartPhotoCard(item,"genus");}).join("")+'</div></details>':'')+'</section>';
}

function botanyPartExamples(sp,genusData){
  if(!sp) return "";
  const family=state.familyCache.get(sp.family)||{};
  const familyLesson=family.visual_lesson||{};
  const usedFamily=new Set(),usedGenus=new Set();
  const familyItems=(Array.isArray(familyLesson.steps)?familyLesson.steps:[])
    .filter(function(step){return step && !/pending/i.test(String(step.status||""));})
    .slice(0,7).map(function(step){
      const host=step.anchor_species_id ? state.speciesById.get(step.anchor_species_id) : null;
      const direct=familyExternalImageUrl(step);
      let photo=null;
      if(host && Number.isInteger(step.anchor_image_index)){
        const chosen=imagesFor(host)[step.anchor_image_index];
        if(chosen && chosen.file && !/^(no|private|restricted|review)$/i.test(String(chosen.public_reuse||""))){
          photo={species:host,img:chosen,src:imagePath(host,chosen)};
          usedFamily.add(photo.src);
        }
      }
      if(host && !photo){
        photo=botanyPartPhoto(host,step.photo_role||step.title,usedFamily,[]);
        if(!photo && imagesFor(host).length && /habit|whole.plant/i.test(String(step.photo_role||""))) {
          const img=imagesFor(host)[0];photo={species:host,img:img,src:imagePath(host,img)};
        }
      }
      if(!photo && direct && /^https?:\/\//i.test(direct)){
        photo={species:null,img:{role:step.photo_role||"Teaching close-up",creator:step.image_credit||"",source_page:step.source_page||""},src:direct};
      }
      return {title:String(step.title||step.photo_role||"Family part").replace(/^\d+\s*[·.-]\s*/,""),description:step.look_for||"",why:step.why_it_matters||"",role:step.photo_role||"",photo:photo,credit:step.image_credit||""};
    });
  if(!familyItems.length){
    const diag=family.family_diagnostics||{};
    Object.entries(diag).filter(function(pair){return /flower|fruit|leaf|follicle|stem|reproductive|where_to_look/i.test(pair[0]);}).slice(0,4).forEach(function(pair){
      const photo=botanyPartPhoto(sp,pair[0],usedFamily,[]);
      familyItems.push({title:botanyPartLabel(pair[0]),description:String(pair[1]),photo:photo});
    });
  }
  const diag=genusData && genusData.genus_diagnostics ||{};
  const keyPriority=["corona","gynostegium","flower","inflorescence","leaves","leaf","fruit","buds","bark","stem","latex","habit"];
  const available=Object.keys(diag);
  const chosen=available.sort(function(a,b){
    const aa=keyPriority.indexOf(a),bb=keyPriority.indexOf(b);
    return (aa<0?100:aa)-(bb<0?100:bb);
  }).slice(0,5);
  const relatives=genusSpecies(sp.family,sp.genus).filter(function(x){return x.id!==sp.id;});
  const exactParts=botanyExactGenusParts(genusData);
  const genusItems=exactParts.length?exactParts:chosen.map(function(key){
    return {title:botanyPartLabel(key),description:formatValue(diag[key]),term:state.learning?.terms?.[key]?key:null,photo:botanyPartPhoto(sp,key,usedGenus,relatives),role:key};
  });
  if(!genusItems.length){
    imagesFor(sp).slice(0,4).forEach(function(img){
      genusItems.push({title:botanyPartLabel(img.role||"Field feature"),description:"Compare this structure across species in the genus lesson.",photo:{species:sp,img:img,src:imagePath(sp,img)}});
    });
  }
  const seenRoles=new Set();
  const speciesItems=imagesFor(sp).filter(function(img){
    const role=String(img.role||"").trim().toLowerCase();
    const group=botanyPartLabel(role);
    if(seenRoles.has(group)) return false;
    seenRoles.add(group);return true;
  }).slice(0,5).map(function(img){
    return {title:botanyPartLabel(img.role),description:img.caption||"Compare this "+(img.role||"view").toLowerCase()+" with the identification clues above.",fieldCue:anatomyFieldCue(sp,img.role||""),role:img.role||"",photo:{species:sp,img:img,src:imagePath(sp,img)}};
  });
  const familyButton='<button class="part-gallery-open" type="button" data-family="'+esc(sp.family)+'">Explore full '+esc(sp.family)+' family lesson →</button>';
  const genusButton='<button class="part-gallery-open" type="button" data-genus="'+esc(sp.genus)+'" data-genus-family="'+esc(sp.family)+'">Explore full '+esc(sp.genus)+' genus lesson →</button>';
  const familyProfileData=familyProfile(sp.family)||{};
  const familyCue=familyProfileData.look_here_first||family.family_diagnostics?.where_to_look_first||familyProfileData.plain_signature||"Look for reliable structures shared across members of this family.";
  const genusCue=genusData?.look_here_first||genusData?.shared_genus_recognition?.look_here_first||genusData?.study_strategy?.look_here_first||genusData?.study_strategy?.priority?.[0]||"Look at the structures shared by close relatives before deciding on a species.";
  const speciesCue=lookHereFirst(sp);
  return '<section id="partsSection" class="section-block botany-parts-section" aria-labelledby="botanyPartsTitle">'+
    '<div class="botany-parts-hero"><div class="eyebrow">Next step · Learn by looking</div>'+
    '<h2 id="botanyPartsTitle">What should I look at on this plant?</h2>'+
    '<p>Begin with the family pattern, check traits shared by the genus, and then inspect this species. Open each step to see photos next to the structure and identification clue.</p>'+
    '<div class="botany-parts-keys"><span>01 · Find the family pattern</span><span>02 · Narrow to genus</span><span>03 · Confirm the species</span></div></div>'+
    '<div class="part-groups-grid">'+
    botanyPartGroup("family","Family · "+sp.family,"Recognize the broader structural pattern.",familyItems,familyButton,familyCue)+
    botanyPartGroup("genus","Genus · "+sp.genus,"Find the features shared by close relatives.",genusItems,genusButton,genusCue)+
    botanyPartGroup("species","Species · "+scientificName(sp),"Inspect this plant’s own photo gallery and ID clues.",speciesItems,"",speciesCue)+
    '</div>'+
    '<details class="part-photo-note"><summary>About photos, labels and arrows</summary><p>General part examples may be unmarked. When an exact botanical structure has been reviewed, its arrows appear in the <b>Field identification</b> photo guide and the <b>Diagnostic photo comparisons</b> panel; otherwise the named part is a place to investigate, not a verified arrow. Always examine the full-resolution source for fine calyx teeth.</p></details>'+
    '</section>';
}

/* Prominent paths to the full family and genus lessons on each species page. */
function taxonomyLessonShortcuts(sp){
  if(!sp || !sp.family || !sp.genus) return "";
  return '<section id="lessonsSection" class="section-block taxonomy-lesson-shortcuts" aria-labelledby="taxonomyLessonShortcutTitle">'+
    '<div class="section-heading"><div><div class="eyebrow">Explore the plant family tree</div>'+
    '<h2 id="taxonomyLessonShortcutTitle">Open the family &amp; genus lessons</h2></div></div>'+
    '<p class="section-intro">Family and genus have their own full pages with shared structures and look-alike comparisons. Tap a tile to explore.</p>'+
    '<div class="taxonomy-lesson-shortcut-grid">'+
      '<button class="taxonomy-lesson-shortcut taxonomy-lesson-family" type="button" data-family="'+esc(sp.family)+'">'+
        '<span class="taxonomy-lesson-shortcut-kicker">Family lesson</span>'+
        '<strong>'+esc(sp.family)+'</strong>'+
        '<span class="taxonomy-lesson-shortcut-explainer">Why these genera belong together—and how to recognize the family.</span>'+
        '<span class="taxonomy-lesson-shortcut-action">Open family lesson <span aria-hidden="true">→</span></span>'+
      '</button>'+
      '<button class="taxonomy-lesson-shortcut taxonomy-lesson-genus" type="button" data-genus="'+esc(sp.genus)+'" data-genus-family="'+esc(sp.family)+'">'+
        '<span class="taxonomy-lesson-shortcut-kicker">Genus lesson</span>'+
        '<strong><i>'+esc(sp.genus)+'</i></strong>'+
        '<span class="taxonomy-lesson-shortcut-explainer">What close relatives share—and how to tell their species apart.</span>'+
        '<span class="taxonomy-lesson-shortcut-action">Open genus lesson <span aria-hidden="true">→</span></span>'+
      '</button>'+
    '</div>'+
    '<button class="taxonomy-lesson-jump" type="button" data-jump="parts">Explore 3 levels of plant-part photos ↓</button>'+
  '</section>';
}
/* Optional beginner route: preserve all specialist material below, but
   teach 4 genuinely useful, rights-approved photographs before jargon.
   Uses the SAME canonical panels and existing pixel-verified arrow overlays.
   Never promotes a source-labelled lineage image to genetic certainty. */
function speciesBeginnerPhotoPath(sp){
  const lesson=sp&&sp.beginner_learning_path;
  const panels=sp&&sp.visual_comparison&&sp.visual_comparison.items;
  if(!lesson||!Array.isArray(lesson.steps)||!Array.isArray(panels))return "";
  const items=lesson.steps.slice(0,5).map(function(step){
    const i=Number(step.panel_index);
    const source=Number.isInteger(i)&&i>=0&&i<panels.length?panels[i]:null;
    if(!source||!source.image_url||!(/^(https?:\/\/|content\/)/i.test(source.image_url)))return null;
    return Object.assign({},source,{
      label:step.title||source.label,
      caption:step.look_for||source.caption,
      why_it_matters:step.why_it_matters||source.why_it_matters
    });
  }).filter(Boolean);
  if(!items.length)return "";
  const preview={
    id:sp.id+"-starter",
    visual_comparison:{
      instance_id:sp.id+"-starter",
      title:lesson.title||"Start with these photographs",
      subtitle:lesson.intro||"Recognize the plant, then examine its leaf junction and flowers.",
      items:items
    }
  };
  return '<section class="beginner-reed-guide" aria-label="Beginner photo identification path">'+
    '<div class="diagnostic-memory-rule"><span>FIRST TIME IDENTIFYING THIS PLANT?</span>'+
    '<strong>'+esc(lesson.memory_rule||"Follow these photographs in order before opening advanced details.")+'</strong></div>'+
    genusVisualComparison(preview)+
    (lesson.safety_note?'<p class="diagnostic-overlay-note"><b>When to stop:</b> '+esc(lesson.safety_note)+'</p>':"")+
    '</section>';
}
/* Some highly diagnostic photographs are source-link ONLY. Their creators have
   not licensed repository redistribution; link the original publication but
   NEVER insert those protected JPEGs as <img> or transfer arrow coordinates. */
function speciesSourceOnlyMacroReferences(sp){
  const record=sp&&(sp.kr_final_anatomy_photo_review_20261027||sp.silver_research_only_photos_20261027);
  const sources=record&&record.public_study_sources;
  if(!Array.isArray(sources)||!sources.length)return "";
  const safe=function(raw){
    const url=String(raw||"").trim();
    return /^https:\/\/(?:w3\.biosci\.utexas\.edu|www\.biosci\.utexas\.edu|azinvasiveplants\.arizona\.edu|www\.missouriplants\.com)\//i.test(url)?url:"";
  };
  const links=sources.slice(0,5).map(function(source){
    const photo=safe(source.direct_original);
    const page=safe(source.source_page);
    if(!photo&&!page)return "";
    let out='<article class="learning-card"><h3>'+esc(source.role||"Research anatomy")+'</h3>'+
      '<p>'+esc(source.geography||"")+" · "+esc(source.photographer||"Original photographer")+'</p>'+
      '<p class="diagnostic-overlay-note">External educational reference only. Source photo may be copyrighted; it is NOT stored in this learner.</p>';
    if(photo)out+='<p><a href="'+esc(photo)+'" target="_blank" rel="noopener noreferrer">View the photographer’s original image</a></p>';
    if(page)out+='<p><a href="'+esc(page)+'" target="_blank" rel="noopener noreferrer">Read the source anatomy page</a></p>';
    return out+'</article>';
  }).filter(Boolean);
  return links.length?'<section class="section-block" aria-label="Source-only anatomical photographs">'+
    '<p class="section-intro">These are real scientific photos worth studying. We cannot permanently rehost or annotate them without a specific permission grant; use the source links to learn the structures. Local Texas anatomy evidence is NOT the same as an approved website image license.</p>'+
    '<div class="diagnostic-visual-grid">'+links.join("")+'</div></section>':"";
}
/* Species-specific, always-visible field decision guide: reuse exactly
   inspected photographic arrow evidence, not a generic unverified icon. */
function fieldPhotoQuickcheck(sp){
  const key=sp&&sp.field_photo_quickcheck;
  const visual=sp&&sp.visual_comparison;
  if(!key || !visual || !Array.isArray(visual.items) || !Array.isArray(key.featured_photo_indices)) return "";
  const featured=key.featured_photo_indices.map(function(i){return visual.items[i];}).filter(function(item){
    return item && matchesOwnSpeciesOrNamedSubspecies(sp,item) && Array.isArray(item.markers) &&
      item.markers.length && item.image_url;
  });
  if(!featured.length)return "";
  const steps=Array.isArray(key.steps)?key.steps:[];
  const mini={
    visual_comparison:{
      instance_id:sp.id+"-fast",
      title:key.heading || "Field ID: follow the arrows",
      subtitle:"Start here in the field. Every arrow marks a visible, photo-verified structure; unverified or missing anatomy is not labeled.",
      items:featured
    }
  };
  return '<section class="monarda-photo-first"><div class="monarda-photo-first-intro">'+
    '<div class="eyebrow">Field identification · arrows on real photos</div>'+
    '<h2>Look here first — then compare</h2>'+
    '<ol class="monarda-photo-first-steps">'+steps.map(function(step){
      return '<li>'+esc(step)+'</li>';
    }).join("")+'</ol>'+
    (key.field_rule?'<p class="diagnostic-overlay-note">'+esc(key.field_rule)+'</p>':"")+
    '</div>'+genusVisualComparison(mini)+
    (key.warning?'<p class="monarda-photo-first-warning">'+esc(key.warning)+'</p>':"")+
    '</section>';
}
/* Source-backed matrix rows are a curated species-level field lesson.
   This makes stored comparisons visible; do not imply uninstalled comparison
   species have their own verified learner cards or image annotations. */
function speciesFieldMatrix(sp){
  const data=sp && sp.comparisons;
  const rows=data && Array.isArray(data.field_matrix) ? data.field_matrix : [];
  if(!rows.length) return "";
  let out='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Real field decisions</div><h2>Which look-alike is it?</h2></div></div>'+
    '<p class="section-intro">'+(sp.family==="Poaceae"?"For grasses, compare flowering-branch origins, leaf collars and sheaths, then matched mature spikelets. A nonflowering or mown plant may require a tentative ID.":"Compare reproductive structures, not just flower or fruit color. Uninstalled look-alikes are research comparisons, not confirmed learner species cards.")+'</p>'+
    '<div class="diagnostic-visual-grid">';
  rows.forEach(function(row){
    if(!row || typeof row!=="object")return;
    const name=row.taxon||row.scientific_name||"Comparison species";
    const decision=row.quick_rule||row.field_decision||"";
    out+='<article class="learning-card"><div class="eyebrow">Species field key</div><h3>'+esc(name)+'</h3><div class="anatomy-teach-steps">';
    Object.keys(row).forEach(function(k){
      if(["taxon","scientific_name","quick_rule","field_decision"].includes(k))return;
      const v=row[k];
      if(v==null || typeof v!=="string" || !v.trim())return;
      out+='<div class="anatomy-teach-step"><b>'+esc(titleCase(k.replace(/_/g," ")))+'</b><p>'+esc(v)+'</p></div>';
    });
    if(decision)out+='<div class="anatomy-teach-step"><b>How to decide</b><p>'+esc(decision)+'</p></div>';
    out+='</div></article>';
  });
  out+='</div>';
  const cautions=Array.isArray(data.not_reliable_alone)?data.not_reliable_alone:[];
  if(cautions.length){
    out+='<details class="anatomy-next-step"><summary>Traits that are NOT enough alone</summary><ul>';
    cautions.forEach(function(t){if(typeof t==="string"&&t.trim())out+='<li>'+esc(t)+'</li>';});
    out+='</ul></details>';
  }
  return out+'</section>';
}
function plantView(){
  const sp=selectedSpecies(); if(!sp) return homeView();
  const p=familyProfile(sp.family)||{}, c=callout(sp)||{}, terms=termsForSpecies(sp,state.difficulty==="simple"?3:(state.difficulty==="terms"?7:12));
  const similar=similarCandidates(sp), genusData=state.genusCache.get(sp.family+"/"+sp.genus);
  const familyConnection=c.family_connection || p.plain_signature || "";
  const cues=fieldCues(sp,state.difficulty==="simple"?3:5);
  let out='<section class="breadcrumbs"><button type="button" data-nav="home">Home</button>';
  if(!state.quizMode) out+='<span>›</span><button type="button" data-family="'+esc(sp.family)+'">'+esc(sp.family)+'</button><span>›</span><strong><i>'+esc(sp.genus)+'</i></strong>';
  out+='</section>';
  if(!state.quizMode) out+=taxonomyLadder(sp.family,sp.genus,sp)+studyPath(2);
  out+='<section class="plant-focus"><div class="plant-visual">'+photoCarousel(sp)+'</div><div class="plant-study">'+identityPanel(sp)+
    '<div class="look-card emphasis"><span>🔎 FIRST CLUE · LOOK HERE</span><strong>'+clueWithTerms(lookHereFirst(sp))+'</strong></div><div class="cue-list">';
  cues.forEach(function(x,i){ out+='<div><b aria-hidden="true">'+(i+1)+'</b><span>'+clueWithTerms(x)+'</span></div>'; });
  out+='</div><div class="study-actions">'+(!state.quizMode || state.quizRevealed ? '<button class="primary-button" type="button" data-jump="parts">Next: inspect the plant parts ↓</button>' : '')+
    (similar.length?'<button class="secondary-button" type="button" data-jump="similar">Compare similar plants</button>':'')+
    (state.difficulty==="simple"?'<button class="secondary-button" type="button" data-set-difficulty="terms">Teach me the terms</button>':'')+'</div></div></section>';
  if(!state.quizMode || state.quizRevealed) out+=speciesBeginnerPhotoPath(sp);
  if(!state.quizMode || state.quizRevealed) out+=fieldPhotoQuickcheck(sp);
  if(!state.quizMode || state.quizRevealed) out+=botanyPartExamples(sp,genusData);
  out+='<div class="study-drawer-grid">';
  const similarStart=out.length;
  out+='<section id="similarSection" class="section-block"><div class="section-heading"><div><div class="eyebrow">The confirmation step</div><h2>Compare look-alikes</h2></div></div>'+
    '<p class="section-intro">Check a look-alike before settling on an ID. “Same genus” means close relatives; “useful comparison” is a curated pairing; “same family” is a broader relationship, not proof the plants look alike.</p><div class="similar-grid">';
  if(similar.length) similar.forEach(function(x){ out+=similarCard(sp,x.sp,x.reason); }); else out+='<div class="empty-panel">No comparison plants are curated yet.</div>';
  out+='</div></section>';
  out=out.slice(0,similarStart)+studyDrawer("3 · Check the look-alikes",similar.length?("Compare "+similar.length+" other plants before confirming your ID."):"No comparison plants curated yet; revisit after photo study.",out.slice(similarStart),"compare");
  if(!state.quizMode && sp.visual_comparison && Array.isArray(sp.visual_comparison.items)) out+=studyDrawer("Diagnostic photo comparisons","Use documented photo evidence to check distinguishing structures.",genusVisualComparison(sp),"photo");
  if(!state.quizMode && sp.kr_final_anatomy_photo_review_20261027) out+=studyDrawer("KR research photos — external source links","Study source-author photographs of the true ligule and raised hair bases without copying copyrighted JPEGs.",speciesSourceOnlyMacroReferences(sp),"photo");
  if(!state.quizMode && sp.silver_research_only_photos_20261027) out+=studyDrawer("Silver bluestem — source-only ligule and node photos","Open the original Kansas anatomy photos for study; the copyrighted photographs are not rehosted and their Texas identity has not been independently verified.",speciesSourceOnlyMacroReferences(sp),"photo");
  if(!state.quizMode && sp.comparisons && Array.isArray(sp.comparisons.field_matrix) && sp.comparisons.field_matrix.length) out+=studyDrawer("Detailed species look-alike key",sp.family==="Poaceae"?"Compare attached racemes, leaf sheaths, collar hairs and mature spikelets to avoid false grass IDs.":"Compare the actual distinguishing structures and field checks, not just overall appearance.",speciesFieldMatrix(sp),"compare");
  if(!state.quizMode || state.quizRevealed) out+=studyDrawer("Study the family & genus","Open full lessons for deeper structural evidence.",taxonomyLessonShortcuts(sp),"photo");
  const vocabStart=out.length;
  if(state.difficulty!=="simple"){
    out+='<section class="section-block learning-panel"><div class="section-heading"><div><div class="eyebrow">🔤 Words for what you see</div><h2>Learn the plant parts</h2></div>'+
      '<button class="text-button" type="button" data-nav="glossary">Full glossary →</button></div><div class="term-row large">'+terms.map(termChip).join("")+'</div>'+
      '<p class="teaching-note">Tap a term for plain language, the formal definition, where to look, why it matters, and a labeled diagram.</p></section>';
  }
  if(out.length>vocabStart) out=out.slice(0,vocabStart)+studyDrawer("Learn the plant words","Tap unfamiliar terms to understand each ID clue.",out.slice(vocabStart),"terms");
  if(!state.quizMode || state.quizRevealed) out+=studyDrawer("Why this plant has its name","Follow the family tree using source-backed clues.",taxonomyTeachingTrail(sp,genusData,p,c),"terms");
  if(state.difficulty==="field") out+=studyDrawer("Technical morphology","Every detailed morphological field, without the scrolling.",fieldBotanySection(sp,genusData),"terms");
  out+='</div>';
  return out;
}
function compareSpeciesOptions(selectedId){
  const grouped=new Map();
  state.species.forEach(function(sp){ if(!grouped.has(sp.family)) grouped.set(sp.family,[]); grouped.get(sp.family).push(sp); });
  let out='<option value="">Choose a species…</option>';
  Array.from(grouped.keys()).sort().forEach(function(family){
    out+='<optgroup label="'+esc(family)+'">';
    grouped.get(family).forEach(function(sp){ out+='<option value="'+esc(sp.id)+'" '+(sp.id===selectedId?"selected":"")+'>'+esc(scientificName(sp))+(commonName(sp)?' — '+esc(commonName(sp)):'')+'</option>'; });
    out+='</optgroup>';
  });
  return out;
}
function ensureComparePair(){
  if(state.compareA && state.compareB && state.compareA!==state.compareB && state.speciesById.has(state.compareA) && state.speciesById.has(state.compareB)) return;
  const groups=new Map();
  state.species.forEach(function(sp){ const k=sp.family+"/"+sp.genus; if(!groups.has(k)) groups.set(k,[]); groups.get(k).push(sp); });
  const pair=Array.from(groups.values()).find(function(xs){ return xs.length>=2; }) || state.species.slice(0,2);
  if(pair[0]) state.compareA=pair[0].id;
  if(pair[1]) state.compareB=pair[1].id;
}
function compareRelationshipHTML(a,b){
  if(a.genus===b.genus && a.family===b.family){
    return '<div class="compare-relationship same-genus"><div class="eyebrow">Same genus</div><strong>Start with shared '+esc(a.family)+' structure, then shared <i>'+esc(a.genus)+'</i> structure. Species-level characters should do the final separation.</strong><button class="text-button" type="button" data-genus="'+esc(a.genus)+'" data-genus-family="'+esc(a.family)+'">Open '+esc(a.genus)+' genus lesson →</button></div>';
  }
  if(a.family===b.family){
    const p=familyProfile(a.family)||{};
    return '<div class="compare-relationship same-family"><div class="eyebrow">Same family · different genera</div><strong>Both should first fit '+esc(a.family)+'. Then ask which genus-level architecture each plant follows.</strong><p>'+esc(p.plain_signature||p.field_signature||"")+'</p><button class="text-button" type="button" data-family="'+esc(a.family)+'">Open '+esc(a.family)+' family lesson →</button></div>';
  }
  const pa=familyProfile(a.family)||{}, pb=familyProfile(b.family)||{};
  return '<div class="compare-relationship cross-family"><div class="eyebrow">Different families</div><strong>Do not start with species details. First decide which family architecture the unknown plant matches.</strong><div class="cross-family-signatures"><div><b>'+esc(a.family)+'</b><span>'+esc(pa.plain_signature||pa.field_signature||lookHereFirst(a))+'</span></div><div><b>'+esc(b.family)+'</b><span>'+esc(pb.plain_signature||pb.field_signature||lookHereFirst(b))+'</span></div></div></div>';
}
function compareView(){
  ensureComparePair();
  const a=state.speciesById.get(state.compareA), b=state.speciesById.get(state.compareB);
  let out='<section class="page-intro compare-intro"><div class="eyebrow">Plant detective lab 🔎</div><h1>Spot the differences!</h1><p>Choose two plants. Compare the pictures first, then look for leaf, flower, stem and fruit clues. The botanical words help name what you see.</p></section>'+
    '<section class="global-compare-picker"><label><span>Plant A</span><select data-global-compare="a">'+compareSpeciesOptions(state.compareA)+'</select></label><button class="swap-compare" type="button" data-swap-compare aria-label="Swap plants">⇄</button><label><span>Plant B</span><select data-global-compare="b">'+compareSpeciesOptions(state.compareB)+'</select></label></section>';
  if(!a || !b || a.id===b.id) return out+'<div class="empty-panel">Choose two different curated species to compare.</div>';
  const keys=compareKeys(a,b);
  out+=compareRelationshipHTML(a,b);
  out+='<section class="compare-workspace"><div class="compare-heads">'+compareHead(a)+compareHead(b)+'</div>'+
    '<div class="compare-table"><div class="compare-row compare-header"><b>Character</b><b><i>'+esc(scientificName(a))+'</i></b><b><i>'+esc(scientificName(b))+'</i></b></div>';
  keys.forEach(function(k){ out+='<div class="compare-row"><strong>'+esc(titleCase(k))+'</strong><span>'+esc(formatValue((a.morphology_keys||{})[k] ?? "—"))+'</span><span>'+esc(formatValue((b.morphology_keys||{})[k] ?? "—"))+'</span></div>'; });
  out+='</div><div class="compare-actions"><button class="secondary-button" type="button" data-species="'+esc(a.id)+'">Study '+esc(commonName(a)||a.genus)+'</button><button class="secondary-button" type="button" data-species="'+esc(b.id)+'">Study '+esc(commonName(b)||b.genus)+'</button></div></section>';
  return out;
}
function browseView(){
  const families=Array.from(new Set(state.species.map(function(sp){ return sp.family; }).concat(Object.keys((state.learning&&state.learning.family_profiles)||{}),state.lessonIndex.families))).sort();
  const genera=state.browseFamily ? Array.from(new Set(generaForFamily(state.browseFamily).map(function(x){ return x[0]; }).concat(state.lessonIndex.genera.filter(function(x){ return x.family===state.browseFamily; }).map(function(x){ return x.genus; })))).sort() : [];
  let list=state.species.slice();
  if(state.browseFamily) list=list.filter(function(sp){ return sp.family===state.browseFamily; });
  if(state.browseGenus) list=list.filter(function(sp){ return sp.genus===state.browseGenus; });
  let out='<section class="page-intro"><div class="eyebrow">Pick your path</div><h1>Explore the plant family tree 🌱</h1><p>Start big, then zoom in: a family is a group of related plants, a genus is a closer group, and a species is one kind of plant.</p></section>'+
    '<section class="taxonomy-picker"><label><span>1 · Family</span><select data-browse-select="family"><option value="">All families</option>';
  families.forEach(function(f){ const n=familySpecies(f).length; out+='<option value="'+esc(f)+'" '+(f===state.browseFamily?"selected":"")+'>'+esc(f)+' — '+(n?n+' species':'family lesson')+'</option>'; });
  out+='</select></label><div class="tax-arrow">→</div><label><span>2 · Genus</span><select data-browse-select="genus" '+(!state.browseFamily?"disabled":"")+'><option value="">All genera</option>';
  genera.forEach(function(g){ out+='<option value="'+esc(g)+'" '+(g===state.browseGenus?"selected":"")+'>'+esc(g)+'</option>'; });
  out+='</select></label><div class="tax-arrow">→</div><div class="picker-result"><span>3 · Species</span><strong>'+list.length+' taxa</strong>'+(state.browseGenus?'<button class="text-button" type="button" data-genus="'+esc(state.browseGenus)+'" data-genus-family="'+esc(state.browseFamily)+'">Open genus lesson →</button>':(state.browseFamily?'<button class="text-button" type="button" data-family="'+esc(state.browseFamily)+'">Open family lesson →</button>':''))+'</div></section>'+
    '<section class="section-block"><div class="species-tile-grid">';
  if(list.length) list.forEach(function(sp){ out+=speciesTile(sp,true); });
  else if(state.browseFamily) out+='<div class="empty-panel">This family lesson is ready, but canonical species anchors are still being installed. Open the family lesson above to study its diagnostic characters now.</div>';
  return out+'</div></section>';
}
function termPreviewMedia(t){
  const real=t && t.real_photo ? t.real_photo : null;
  const src=real ? familyExternalImageUrl(real) : "";
  if(src){
    const mediaType=real.media_type==="diagram" ? "diagram" : "real photo";
    return '<span class="glossary-card-media"><img src="'+esc(src)+'" alt="'+esc(real.alt||("Visual example of "+t.term))+'" loading="lazy"><b>'+mediaType+'</b></span>';
  }
  if(t && t.visual) return '<span class="glossary-card-media"><img src="'+esc(t.visual)+'" alt="Labeled diagram for '+esc(t.term)+'" loading="lazy"><b>diagram</b></span>';
  return '<span class="glossary-card-media glossary-card-media-empty" aria-hidden="true">✣</span>';
}
function termDrillMedia(id,revealed){
  const t=state.learning.terms[id]; if(!t) return "";
  const real=t.real_photo||null;
  const src=real ? familyExternalImageUrl(real) : (t.visual||"");
  if(!src) return '<div class="term-drill-empty">No visual available.</div>';
  const overlay=revealed && real ? termPhotoAnnotations(real) : "";
  const kind=real && real.media_type==="diagram" ? "diagram" : "real photo";
  return '<figure class="term-drill-figure"><div class="term-drill-image"><img src="'+esc(src)+'" alt="'+esc((real&&real.alt)||("Visual clue for botanical term"))+'" loading="eager">'+overlay+
    '<span class="term-drill-kind">'+esc(kind)+'</span>'+(revealed?'<span class="term-drill-revealed">labels revealed</span>':'')+'</div></figure>';
}
function chooseTermDrill(){
  const allIds=Object.keys(state.learning.terms||{});
  let ids=Array.isArray(state.termDrillPool) && state.termDrillPool.length ? state.termDrillPool.filter(function(id){ return state.learning.terms[id]; }) : allIds;
  if(!ids.length) ids=allIds;
  if(!ids.length) return null;
  let pool=ids;
  if(state.termDrillId && ids.length>1) pool=ids.filter(function(id){ return id!==state.termDrillId; });
  const id=pool[Math.floor(Math.random()*pool.length)];
  state.termDrillId=id; state.termDrillRevealed=false; return id;
}
function renderTermDrillModal(){
  const id=state.termDrillId || chooseTermDrill();
  const t=id ? state.learning.terms[id] : null; if(!t) return;
  const revealed=state.termDrillRevealed;
  let answer="";
  if(revealed){
    answer='<div class="term-drill-answer"><div class="eyebrow">Answer</div><h2>'+esc(t.term)+'</h2><p class="pronunciation">rough pronunciation · '+esc(t.pronunciation||"—")+'</p>'+
      '<div class="definition plain"><b>Plain language</b><p>'+esc(t.plain)+'</p></div>'+
      '<div class="term-lesson"><div><b>Where do I look?</b><p>'+esc(t.where)+'</p></div><div><b>Why does it matter?</b><p>'+esc(t.why)+'</p></div></div></div>';
  }else{
    answer='<div class="term-drill-question"><div class="eyebrow">Visual term drill</div><h2>What structure are you looking at?</h2><p>Use the photo or diagram first. Say the botanical term before revealing the labels.</p></div>';
  }
  els.modal.innerHTML='<div class="modal-backdrop" data-close-modal><section class="modal-card term-drill-modal" role="dialog" aria-modal="true" aria-labelledby="termDrillTitle">'+
    '<button class="modal-close" type="button" data-close-modal aria-label="Close">×</button><div class="term-drill-layout">'+termDrillMedia(id,revealed)+
    '<div class="term-drill-copy" id="termDrillTitle">'+answer+'<div class="term-drill-actions">'+
    (revealed?'<button class="secondary-button" type="button" data-term-drill-open="'+esc(id)+'">Open full lesson</button>':'<button class="primary-button" type="button" data-term-drill-reveal>Reveal answer + labels</button>')+
    '<button class="'+(revealed?'primary-button':'secondary-button')+'" type="button" data-term-drill-next>Next visual →</button></div></div></div></section></div>';
}
function openTermDrill(ids){
  state.termDrillPool=Array.isArray(ids) && ids.length ? ids.slice() : null;
  chooseTermDrill(); renderTermDrillModal();
}

function termCompareSets(){
  return [
    {title:"Sepal vs calyx",ids:["sepal","calyx"],rule:"one part vs the whole outer whorl"},
    {title:"Phyllary vs involucre",ids:["phyllary","involucre"],rule:"one bract vs the complete bract set"},
    {title:"Ray vs disc florets",ids:["ray-floret","disc-floret","capitulum"],rule:"outer flower vs central flower vs the whole head"},
    {title:"Pappus vs cypsela",ids:["pappus","cypsela"],rule:"dispersal structure vs dry fruit body"},
    {title:"Glume vs lemma vs palea",ids:["glume","lemma","palea"],rule:"spikelet bracts at different structural levels"},
    {title:"Corona vs hood vs horn",ids:["corona","hood","horn"],rule:"whole milkweed crown vs one cup-like part vs inner projection"},
    {title:"Pollinium vs pollinarium",ids:["pollinium","pollinarium","corpusculum"],rule:"pollen mass vs whole transfer unit vs central clip"},
    {title:"Pinna vs pinnule",ids:["pinna","pinnule"],rule:"primary fern division vs subdivision of a pinna"},
    {title:"Schizocarp vs mericarp",ids:["schizocarp","mericarp"],rule:"whole splitting fruit vs one segment"},
    {title:"Aggregate fruit vs drupelet",ids:["aggregate-fruit","drupelet"],rule:"whole fruit cluster vs one tiny drupe"},
    {title:"Superior vs inferior ovary",ids:["superior-ovary","inferior-ovary"],rule:"other flower parts attach below vs above the ovary"},
    {title:"Staminate vs pistillate",ids:["staminate","pistillate"],rule:"functional male flower vs functional female flower"},
    {title:"Dioecious vs monoecious",ids:["dioecious","monoecious"],rule:"sexes on separate plants vs both flower sexes on one plant"}
  ];
}
function termCompareMedia(id){
  const t=state.learning.terms[id]; if(!t) return "";
  const real=t.real_photo||null;
  const src=real ? familyExternalImageUrl(real) : (t.visual||"");
  if(!src) return '<div class="term-compare-empty">No visual.</div>';
  return '<div class="term-compare-image"><img src="'+esc(src)+'" alt="'+esc((real&&real.alt)||("Visual for "+t.term))+'" loading="eager">'+
    (real?termPhotoAnnotations(real):"")+'</div>';
}
function openTermCompare(ids,title,rule){
  const valid=(ids||[]).filter(function(id){ return state.learning.terms[id]; });
  if(valid.length<2) return;
  let cards="";
  valid.forEach(function(id){
    const t=state.learning.terms[id];
    cards+='<article class="term-compare-card">'+termCompareMedia(id)+'<div class="term-compare-copy"><h3>'+esc(t.term)+'</h3><p>'+esc(t.plain)+'</p>'+
      '<button class="text-button" type="button" data-term="'+esc(id)+'">Open full lesson →</button></div></article>';
  });
  els.modal.innerHTML='<div class="modal-backdrop" data-close-modal><section class="modal-card term-compare-modal" role="dialog" aria-modal="true" aria-labelledby="termCompareTitle">'+
    '<button class="modal-close" type="button" data-close-modal aria-label="Close">×</button><div class="eyebrow">Commonly confused structures</div><h2 id="termCompareTitle">'+esc(title||"Compare botanical terms")+'</h2>'+
    (rule?'<p class="term-compare-rule">'+esc(rule)+'</p>':'')+'<div class="term-compare-grid count-'+valid.length+'">'+cards+'</div></section></div>';
}
function confusionSetsHTML(){
  const sets=termCompareSets().filter(function(set){ return set.ids.every(function(id){ return state.learning.terms[id]; }); });
  let out='<section class="section-block term-confusion-section"><div class="section-heading"><div><div class="eyebrow">Train the differences</div><h2>Commonly confused visual terms</h2></div></div>'+
    '<p class="section-intro">These pairs and small groups are easier to learn side by side than as separate definitions.</p><div class="term-confusion-grid">';
  sets.forEach(function(set,index){
    out+='<button class="term-confusion-card" type="button" data-term-compare="'+index+'"><strong>'+esc(set.title)+'</strong><span>'+esc(set.rule)+'</span></button>';
  });
  return out+'</div></section>';
}

function glossaryView(){
  const q=norm(state.glossaryQuery);
  const entries=Object.entries(state.learning.terms).filter(function(pair){
    if(!q) return true;
    const t=pair[1]; return norm([pair[0],t.term,t.plain,t.formal,(t.aliases||[]).join(" ")].join(" ")).includes(q);
  });
  let out='<section class="page-intro"><div class="eyebrow">Botanical vocabulary · '+Object.keys(state.learning.terms).length+' visual terms</div><h1>Learn the word while looking at the structure.</h1>'+
    '<p>Real photos first, learner arrows and labels on the exact structure, and diagrams where a photo cannot show the anatomy clearly.</p>'+
    '<div class="glossary-actions"><button class="primary-button" type="button" data-term-drill-start>Start visual term drill</button><span>Photo first → name it → reveal the labeled structure.</span></div>'+
    '<input id="glossarySearch" class="glossary-search" value="'+esc(state.glossaryQuery)+'" placeholder="Search phyllary, opposite, cupule…"></section>'+
    (!q?confusionSetsHTML():"")+'<section class="glossary-grid">';
  entries.forEach(function(pair){
    const id=pair[0], t=pair[1];
    out+='<button class="glossary-card" type="button" data-term="'+esc(id)+'">'+termPreviewMedia(t)+'<span><strong>'+esc(t.term)+'</strong>'+
      '<em>'+esc(t.pronunciation||"")+'</em><p>'+esc(t.plain)+'</p></span></button>';
  });
  if(!entries.length) out+='<div class="empty-panel">No matching term.</div>';
  return out+'</section>';
}
function render(){
  updateHeader();
  if(state.view==="home") els.app.innerHTML=homeView();
  else if(state.view==="family") els.app.innerHTML=familyView();
  else if(state.view==="genus") els.app.innerHTML=genusView();
  else if(state.view==="plant"){ els.app.innerHTML=plantView(); window.requestAnimationFrame(positionGalleryArrowStages); }
  else if(state.view==="compare") els.app.innerHTML=compareView();
  else if(state.view==="browse") els.app.innerHTML=browseView();
  else if(state.view==="glossary") els.app.innerHTML=glossaryView();
  else if(state.view==="approvals") els.app.innerHTML=approvalsView();
  else els.app.innerHTML=homeView();
  if(state.view==="approvals") requestAnimationFrame(hydrateVisibleApprovalPhotos);
  if(state.view==="genus" || state.view==="plant") requestAnimationFrame(positionDiagnosticArrowStages);
}

function genusMatches(query){
  const q=norm(query); if(!q) return [];
  const seen=new Set(), rows=[];
  state.species.forEach(function(sp){
    const key=sp.family+"/"+sp.genus; if(seen.has(key)) return; seen.add(key);
    let score=0;
    if(norm(sp.genus)===q) score=100;
    else if(norm(sp.genus).startsWith(q)) score=60;
    else if(norm(sp.genus).includes(q)) score=25;
    if(score) rows.push({family:sp.family,genus:sp.genus,score:score,count:genusSpecies(sp.family,sp.genus).length});
  });
  return rows.sort(function(a,b){ return b.score-a.score || a.genus.localeCompare(b.genus); }).slice(0,4);
}
function searchMatches(query){
  const q=norm(query); if(!q) return [];
  return state.species.map(function(sp){
    const sci=scientificName(sp), common=commonName(sp), body=norm([sci,common,sp.genus,sp.family].concat(sp.other_common_names||[]).concat((sp.synonyms||[]).map(function(s){ return typeof s==="string"?s:(s && (s.name||s.scientific_name))||""; })).join(" "));
    let score=0;
    if(norm(sci)===q || norm(common)===q) score+=100;
    if(norm(sci).startsWith(q) || norm(common).startsWith(q)) score+=50;
    if(norm(sp.genus).startsWith(q)) score+=30;
    if(body.includes(q)) score+=10;
    return {sp:sp,score:score};
  }).filter(function(x){ return x.score>0; }).sort(function(a,b){ return b.score-a.score || scientificName(a.sp).localeCompare(scientificName(b.sp)); }).slice(0,8);
}
function renderResults(){
  const q=els.search.value.trim(); els.clear.classList.toggle("visible",Boolean(q));
  if(!q){ hideResults(); return; }
  const matches=searchMatches(q), gmatches=genusMatches(q);
  const fmatch=Object.keys(state.learning.family_profiles).find(function(f){ return norm(f).includes(norm(q)) || norm(state.learning.family_profiles[f].common_name).includes(norm(q)); });
  let out="";
  if(fmatch){
    out+='<button class="search-family-result" type="button" data-family="'+esc(fmatch)+'"><b>Family</b><span><strong>'+esc(fmatch)+'</strong><em>'+esc(familyProfile(fmatch).common_name)+'</em></span></button>';
  }
  gmatches.forEach(function(g){
    out+='<button class="search-genus-result" type="button" data-genus="'+esc(g.genus)+'" data-genus-family="'+esc(g.family)+'"><b>Genus</b><span><strong><i>'+esc(g.genus)+'</i></strong><em>'+esc(g.family)+' · '+g.count+' species</em></span></button>';
  });
  matches.forEach(function(x){
    const sp=x.sp; out+='<button class="search-species-result" type="button" data-species="'+sp.id+'">'+thumb(sp,"search-thumb")+'<span><strong><i>'+esc(scientificName(sp))+'</i></strong>'+
      '<em>'+esc(commonName(sp))+'</em>'+encounterBadge(sp)+'<small>'+esc(sp.family)+' › '+esc(sp.genus)+'</small></span></button>';
  });
  if(!fmatch && !gmatches.length && !matches.length) out='<div class="search-empty">No matching curated plant yet.</div>';
  els.results.innerHTML=out; els.results.hidden=false;
}
function hideResults(){ els.results.hidden=true; }

function termPhotoAnnotations(photo){
  const items=photo && Array.isArray(photo.annotations) ? photo.annotations.filter(function(a){
    return a && Number.isFinite(Number(a.x)) && Number.isFinite(Number(a.y)) && Number.isFinite(Number(a.label_x)) && Number.isFinite(Number(a.label_y)) && a.label;
  }) : [];
  if(!items.length) return "";
  const lines=items.map(function(a){
    return '<line x1="'+Number(a.label_x)+'" y1="'+Number(a.label_y)+'" x2="'+Number(a.x)+'" y2="'+Number(a.y)+'" marker-end="url(#termArrow)"></line>'+
      '<circle cx="'+Number(a.x)+'" cy="'+Number(a.y)+'" r="1.2"></circle>';
  }).join("");
  const labels=items.map(function(a){
    return '<span class="term-annotation-label" style="left:'+Number(a.label_x)+'%;top:'+Number(a.label_y)+'%">'+esc(a.label)+'</span>';
  }).join("");
  return '<div class="term-annotation-stage" aria-hidden="true"><svg class="term-annotation-lines" viewBox="0 0 100 100" preserveAspectRatio="none"><defs><marker id="termArrow" markerWidth="5" markerHeight="5" refX="4.2" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 z"></path></marker></defs>'+lines+'</svg>'+labels+'</div>';
}


/*
 * A glossary coordinate (x,y) is a percentage of the SOURCE PHOTOGRAPH,
 * not of the CSS img element. object-fit:contain can letterbox the photo
 * inside that element, especially in the mobile modal and term drill.
 * Measure the actual visible photo rectangle before placing annotation SVG.
 */
function syncTermAnnotationPositions(){
  document.querySelectorAll(".term-annotation-stage").forEach(function(stage){
    const container=stage.parentElement;
    const img=container && container.querySelector("img");
    if(!img || !img.naturalWidth || !img.naturalHeight){
      stage.style.visibility="hidden";
      return;
    }
    const box=img.getBoundingClientRect();
    const frame=container.getBoundingClientRect();
    if(!box.width || !box.height){stage.style.visibility="hidden";return;}
    const fit=window.getComputedStyle(img).objectFit;
    let drawnW=box.width,drawnH=box.height;
    if(fit==="contain" || fit==="scale-down"){
      let scale=Math.min(box.width/img.naturalWidth,box.height/img.naturalHeight);
      if(fit==="scale-down") scale=Math.min(scale,1);
      drawnW=img.naturalWidth*scale;
      drawnH=img.naturalHeight*scale;
    }
    // Current glossary CSS always centers object-fit media.
    stage.style.left=(box.left-frame.left+(box.width-drawnW)/2)+"px";
    stage.style.top=(box.top-frame.top+(box.height-drawnH)/2)+"px";
    stage.style.width=drawnW+"px";
    stage.style.height=drawnH+"px";
    stage.style.visibility="visible";
  });
}
document.addEventListener("load",function(ev){
  if(ev.target && ev.target.tagName==="IMG") syncTermAnnotationPositions();
},true);
window.addEventListener("resize",syncTermAnnotationPositions,{passive:true});
if(els.modal && window.MutationObserver){
  const termAnnotationObserver=new MutationObserver(function(){
    window.requestAnimationFrame(syncTermAnnotationPositions);
  });
  termAnnotationObserver.observe(els.modal,{childList:true});
}

function openTermModal(id){
  const t=state.learning.terms[id]; if(!t) return;
  const realMedia=t.real_photo||null;
  const duplicateDiagram=Boolean(t.visual && realMedia && realMedia.image_url===t.visual);
  const diagram=t.visual && !duplicateDiagram ? '<div class="term-visual"><img src="'+esc(t.visual)+'" alt="Labeled diagram for '+esc(t.term)+'"><span class="term-media-label">Labeled diagram</span></div>' :
    (!realMedia?'<div class="term-visual term-visual-empty"><span>Visual pending</span></div>':'');
  let real="";
  if(t.real_photo){
    const src=familyExternalImageUrl(t.real_photo);
    if(src){
      const mediaType=t.real_photo.media_type||"photo";
      const photoKind=mediaType==="diagram" ? (t.real_photo.kind==="annotated" ? "Annotated diagram" : "Diagram") : (t.real_photo.kind==="annotated" ? "Annotated real photo" : "Real example");
      const overlay=termPhotoAnnotations(t.real_photo);
      const badge=t.real_photo.kind==="annotated" ? (overlay?'<span class="term-photo-badge">learner labels / arrows</span>':'<span class="term-photo-badge">labels / arrows in photo</span>') : "";
      real='<figure class="term-real-photo '+(t.real_photo.kind==="annotated"?"is-annotated":"")+'"><div class="term-photo-wrap"><img src="'+esc(src)+'" alt="'+esc(t.real_photo.alt||("Real example of "+t.term))+'" loading="lazy">'+
        overlay+badge+
        '</div><figcaption><b>'+photoKind+'</b><span>'+esc(t.real_photo.label||t.term)+'</span>'+
        (t.real_photo.focus?'<em>'+esc(t.real_photo.focus)+'</em>':'')+
        (t.real_photo.annotation_note?'<em class="annotation-note">'+esc(t.real_photo.annotation_note)+'</em>':'')+
        '<small>'+esc(t.real_photo.credit||"")+'</small>'+
        (t.real_photo.source_page?'<a href="'+esc(t.real_photo.source_page)+'" target="_blank" rel="noopener noreferrer">source ↗</a>':'')+'</figcaption></figure>';
    }
  }
  const visual='<div class="term-media-stack">'+diagram+real+'</div>';
  els.modal.innerHTML='<div class="modal-backdrop" data-close-modal><section class="modal-card term-modal" role="dialog" aria-modal="true" aria-labelledby="termTitle">'+
    '<button class="modal-close" type="button" data-close-modal aria-label="Close">×</button>'+visual+
    '<div class="term-copy"><div class="eyebrow">Botanical term</div><h2 id="termTitle">'+esc(t.term)+'</h2><p class="pronunciation">rough pronunciation · '+esc(t.pronunciation||"—")+'</p>'+
    '<div class="definition plain"><b>Plain language</b><p>'+esc(t.plain)+'</p></div><div class="definition"><b>Botanical definition</b><p>'+esc(t.formal)+'</p></div>'+
    '<div class="term-lesson"><div><b>Where do I look?</b><p>'+esc(t.where)+'</p></div><div><b>Why does it matter?</b><p>'+esc(t.why)+'</p></div></div></div></section></div>';
}
async function openFamilyModal(family){
  const p=familyProfile(family)||{}, canon=await ensureFamilyData(family), diagnostics=canon && (canon.family_diagnostics || canon.diagnostic_traits);
  let out='<div class="modal-backdrop" data-close-modal><section class="modal-card family-modal" role="dialog" aria-modal="true" aria-labelledby="familyTitle">'+
    '<button class="modal-close" type="button" data-close-modal aria-label="Close">×</button><div class="eyebrow">Family lesson</div><h2 id="familyTitle">'+esc(family)+'</h2>'+
    '<p class="family-common">'+esc(p.common_name || (canon&&canon.common_name) || "")+'</p><div class="look-card"><span>FAMILY SIGNATURE</span><strong>'+esc(p.plain_signature||"")+'</strong></div>'+
    '<div class="definition"><b>Where should I look first?</b><p>'+esc(p.look_here_first||"")+'</p></div><div class="definition"><b>Field-botany version</b><p>'+esc(p.field_signature||"")+'</p></div>';
  if(p.field_question) out+='<div class="field-question"><b>Ask yourself in the field:</b><p>'+esc(p.field_question)+'</p></div>';
  out+='<div class="term-row large">'+(p.key_terms||[]).map(termChip).join("")+'</div>';
  if(diagnostics && state.difficulty==="field") out+='<div class="canonical-diagnostics"><h3>Canonical family diagnostics</h3>'+structuredTeachingHTML(diagnostics)+'</div>';
  if(canon && canon.visual_lesson) out+=familyVisualLessonHTML(canon);
  if(p.caveat) out+='<p class="modal-caveat"><b>Important:</b> '+esc(p.caveat)+'</p>';
  els.modal.innerHTML=out+'</section></div>';
}
function compareKeys(a,b){
  const ma=a.morphology_keys||{}, mb=b.morphology_keys||{}, keys=[];
  const priority=["life_cycle","habit","growth_habit","sap_type","leaf_arrangement","phyllotaxy","leaves","leaf_morphology","inflorescence","flower","flower_color","heads","phyllaries","fruit","bark","acorn"];
  priority.forEach(function(k){ if((ma[k]!=null || mb[k]!=null) && !keys.includes(k)) keys.push(k); });
  Object.keys(ma).forEach(function(k){ if(mb[k]!=null && !keys.includes(k) && !["best_field_traits","high_value_field_traits"].includes(k)) keys.push(k); });
  return keys.slice(0,8);
}
function compareHead(sp){
  return '<article>'+thumb(sp,"compare-photo")+'<h3><i>'+esc(scientificName(sp))+'</i></h3><p>'+esc(commonName(sp))+'</p><div class="mini-look"><b>Look first</b><span>'+esc(lookHereFirst(sp))+'</span></div></article>';
}
function openCompareModal(aid,bid){
  const a=state.speciesById.get(aid), b=state.speciesById.get(bid); if(!a||!b) return;
  const keys=compareKeys(a,b);
  let out='<div class="modal-backdrop" data-close-modal><section class="modal-card compare-modal" role="dialog" aria-modal="true" aria-labelledby="compareTitle">'+
    '<button class="modal-close" type="button" data-close-modal aria-label="Close">×</button><div class="eyebrow">Side-by-side field comparison</div><h2 id="compareTitle">What should I look at differently?</h2>';
  if(a.family===b.family) out+='<p class="shared-family">Both are <b>'+esc(a.family)+'</b>. First recognize the shared family pattern, then separate them with the characters below.</p>';
  out+='<div class="compare-heads">'+compareHead(a)+compareHead(b)+'</div><div class="compare-table"><div class="compare-row compare-header"><b>Character</b><b><i>'+esc(scientificName(a))+'</i></b><b><i>'+esc(scientificName(b))+'</i></b></div>';
  keys.forEach(function(k){
    out+='<div class="compare-row"><strong>'+esc(titleCase(k))+'</strong><span>'+esc(formatValue((a.morphology_keys||{})[k] ?? "—"))+'</span><span>'+esc(formatValue((b.morphology_keys||{})[k] ?? "—"))+'</span></div>';
  });
  out+='</div><div class="compare-actions"><button class="secondary-button" type="button" data-species="'+a.id+'">Study '+esc(commonName(a)||a.genus)+'</button>'+
    '<button class="secondary-button" type="button" data-species="'+b.id+'">Study '+esc(commonName(b)||b.genus)+'</button>'+
    '<button class="primary-button" type="button" data-full-compare="'+esc(a.id)+'|'+esc(b.id)+'">Open full Compare workspace</button></div></section></div>';
  els.modal.innerHTML=out;
}
function closeModal(){ els.modal.innerHTML=""; }

function handleClick(e){
  const close=e.target.closest("[data-close-modal]");
  if(close && (e.target.classList.contains("modal-backdrop") || close.classList.contains("modal-close"))){ closeModal(); return; }
  const partPreview=e.target.closest("[data-part-preview]");
  if(partPreview){ openPartPhotoPreview(partPreview); return; }
  const nav=e.target.closest("[data-nav]"); if(nav){ setView(nav.dataset.nav); return; }
  if(e.target.closest("#brandHome")){ setView("home"); return; }
  const approvalFilter=e.target.closest("[data-approval-filter]");
  if(approvalFilter){ state.approvalsFilter=approvalFilter.dataset.approvalFilter; render(); return; }
  if(e.target.closest("[data-approval-refresh]")){
    state.approvals=null; state.approvalsError=""; render();
    loadApprovals(true).then(function(){ if(state.view==="approvals") render(); }); return;
  }
  const approvalDecision=e.target.closest("[data-approval-decision]");
  if(approvalDecision){ submitApprovalDecision(approvalDecision.dataset.approvalId,approvalDecision.dataset.approvalDecision); return; }
  const diff=e.target.closest("[data-difficulty]"); if(diff){ setDifficulty(diff.dataset.difficulty); return; }
  const setDiff=e.target.closest("[data-set-difficulty]"); if(setDiff){ setDifficulty(setDiff.dataset.setDifficulty); return; }
  if(e.target.closest("[data-term-drill-start]")){ openTermDrill(null); return; }
  if(e.target.closest("[data-family-term-drill]")){
    const p=familyProfile(state.selectedFamily)||{};
    openTermDrill((p.key_terms||[]).filter(function(id){ return state.learning.terms[id]; })); return;
  }
  const termCompare=e.target.closest("[data-term-compare]");
  if(termCompare){
    const set=termCompareSets()[Number(termCompare.dataset.termCompare)];
    if(set) openTermCompare(set.ids,set.title,set.rule);
    return;
  }
  if(e.target.closest("[data-term-drill-reveal]")){ state.termDrillRevealed=true; renderTermDrillModal(); return; }
  if(e.target.closest("[data-term-drill-next]")){ chooseTermDrill(); renderTermDrillModal(); return; }
  const drillOpen=e.target.closest("[data-term-drill-open]"); if(drillOpen){ openTermModal(drillOpen.dataset.termDrillOpen); return; }
  const term=e.target.closest("[data-term]"); if(term){ e.stopPropagation(); openTermModal(term.dataset.term); return; }
  if(e.target.closest("[data-family-compare]")){
    const a=document.getElementById("familyCompareA"), b=document.getElementById("familyCompareB");
    if(a && b){
      if(a.value===b.value){
        const alternatives=familySpecies(state.selectedFamily).filter(function(sp){ return sp.id!==a.value; });
        if(alternatives.length) b.value=alternatives[0].id;
      }
      if(a.value && b.value && a.value!==b.value) openCompareModal(a.value,b.value);
    }
    return;
  }
  if(e.target.closest("[data-genus-compare]")){
    const a=document.getElementById("genusCompareA"), b=document.getElementById("genusCompareB");
    if(a && b){
      if(a.value===b.value){
        const alternatives=genusSpecies(state.selectedGenusFamily,state.selectedGenus).filter(function(sp){ return sp.id!==a.value; });
        if(alternatives.length) b.value=alternatives[0].id;
      }
      if(a.value && b.value && a.value!==b.value) openCompareModal(a.value,b.value);
    }
    return;
  }
  const fullComp=e.target.closest("[data-full-compare]");
  if(fullComp){
    const ids=fullComp.dataset.fullCompare.split("|");
    state.compareA=ids[0]; state.compareB=ids[1]; closeModal(); setView("compare"); return;
  }
  if(e.target.closest("[data-swap-compare]")){
    const tmp=state.compareA; state.compareA=state.compareB; state.compareB=tmp; render(); return;
  }
  const genus=e.target.closest("[data-genus]");
  if(genus){ closeModal(); openGenus(genus.dataset.genusFamily,genus.dataset.genus); return; }
  const comp=e.target.closest("[data-compare]"); if(comp){ const ids=comp.dataset.compare.split("|"); openCompareModal(ids[0],ids[1]); return; }
  const species=e.target.closest("[data-species]"); if(species){ closeModal(); openPlant(species.dataset.species); return; }
  const fam=e.target.closest("[data-family]"); if(fam){ closeModal(); openFamily(fam.dataset.family); return; }
  const famInfo=e.target.closest("[data-family-info]"); if(famInfo){ openFamilyModal(famInfo.dataset.familyInfo); return; }
  const photoThumb=e.target.closest("[data-photo-index]");
  if(photoThumb){
    const sp=selectedSpecies(), imgs=sp?galleryImagesFor(sp):[];
    const index=Number(photoThumb.dataset.photoIndex);
    if(sp && Number.isInteger(index) && index>=0 && index<imgs.length){ state.photoIndex[sp.id]=index; render(); }
    return;
  }
  const photo=e.target.closest("[data-photo-step]");
  if(photo){
    const sp=selectedSpecies(), imgs=sp?galleryImagesFor(sp):[];
    if(sp && imgs.length){
      const order=galleryPhotoOrder(sp);
      const current=state.photoIndex[sp.id]===undefined?order[0]:state.photoIndex[sp.id];
      const pos=Math.max(0,order.indexOf(current));
      const shift=Number(photo.dataset.photoStep)||1;
      state.photoIndex[sp.id]=order[(pos+shift%order.length+order.length)%order.length];
      render();
    }
    return;
  }
  if(e.target.closest("[data-reveal-quiz]")){ state.quizRevealed=true; render(); return; }
  if(e.target.closest("[data-next-quiz]") || e.target.closest("[data-random-quiz]")){ randomQuiz(); return; }
  const jump=e.target.closest("[data-jump]"); if(jump){
    const target=document.getElementById(jump.dataset.jump+"Section");
    if(target){
      if(target.tagName==="DETAILS") target.open=true;
      let parent=target.parentElement && target.parentElement.closest("details");
      while(parent){parent.open=true;parent=parent.parentElement && parent.parentElement.closest("details");}
      if(jump.dataset.jump==="parts"){
        const speciesGroup=target.querySelector(".part-gallery-species");
        if(speciesGroup) speciesGroup.open=true;
      }
      target.scrollIntoView({behavior:"smooth",block:"start"});
    }
    return;
  }
  const gb=e.target.closest("[data-browse-genus]");
  if(gb){ state.browseFamily=gb.dataset.browseFamily; state.browseGenus=gb.dataset.browseGenus; state.view="browse"; render(); window.scrollTo({top:0,behavior:"smooth"}); }
}
function handleChange(e){
  if(e.target.matches("[data-browse-select='family']")){ state.browseFamily=e.target.value; state.browseGenus=""; render(); }
  if(e.target.matches("[data-browse-select='genus']")){ state.browseGenus=e.target.value; render(); }
  if(e.target.matches("[data-global-compare='a']")){ state.compareA=e.target.value; if(state.compareA===state.compareB) state.compareB=""; render(); }
  if(e.target.matches("[data-global-compare='b']")){ state.compareB=e.target.value; if(state.compareA===state.compareB) state.compareA=""; render(); }
}
function handleInput(e){
  if(e.target.id==="glossarySearch"){
    state.glossaryQuery=e.target.value; const pos=e.target.selectionStart; render();
    const input=document.getElementById("glossarySearch"); if(input){ input.focus(); try{ input.setSelectionRange(pos,pos); }catch(err){} }
  }
}
function bind(){
  document.addEventListener("click",handleClick);
  document.addEventListener("change",handleChange);
  document.addEventListener("input",handleInput);
  els.search.addEventListener("input",renderResults);
  els.search.addEventListener("focus",renderResults);
  els.search.addEventListener("keydown",function(e){
    if(e.key==="Enter"){ const first=searchMatches(els.search.value)[0]; if(first){ e.preventDefault(); openPlant(first.sp.id); } }
    if(e.key==="Escape") hideResults();
  });
  els.clear.addEventListener("click",function(){ els.search.value=""; renderResults(); els.search.focus(); });
  els.results.addEventListener("click",function(e){
    const sp=e.target.closest("[data-species]"); if(sp){ openPlant(sp.dataset.species); return; }
    const genus=e.target.closest("[data-genus]"); if(genus){ openGenus(genus.dataset.genusFamily,genus.dataset.genus); return; }
    const fam=e.target.closest("[data-family]"); if(fam) openFamily(fam.dataset.family);
  });
  els.quiz.addEventListener("click",function(){ state.quizMode=!state.quizMode; state.quizRevealed=false; writeLocal("hays-botany-quiz",String(state.quizMode)); render(); });
  document.addEventListener("click",function(e){ if(!e.target.closest(".search-wrap")) hideResults(); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape") closeModal(); });
}
async function boot(){
  try{
    const loaded=await Promise.all([loadJSON("data/manifest.json"),loadJSON("data/project.json"),loadJSON("data/learning-layer.json")]);
    const manifest=loaded[0]; state.project=loaded[1]; state.learning=loaded[2]; state.manifestSpecies=manifest.species||[];
    state.species=await Promise.all(state.manifestSpecies.map(function(x){ return loadJSON(x.path); }));
    try { const idx=await loadJSON("data/lesson-index.json"); if(Array.isArray(idx.families)&&Array.isArray(idx.genera)) state.lessonIndex=idx; } catch(e){ console.warn("Lesson index unavailable; showing species-backed lessons.",e); }
    state.species.sort(function(a,b){ return (a.family||"").localeCompare(b.family||"") || (a.genus||"").localeCompare(b.genus||"") || scientificName(a).localeCompare(scientificName(b)); });
    state.species.forEach(function(sp){ state.speciesById.set(sp.id,sp); });
    if(!state.learning.difficulty_levels[state.difficulty]) state.difficulty="terms";
    bind(); render();
  }catch(err){
    els.app.innerHTML='<section class="error-card"><h1>Could not load the learner.</h1><p>'+esc(err.message)+'</p><p>Make sure this folder is running through <code>RUN_LOCAL_SERVER.bat</code>.</p></section>';
  }
}
boot();

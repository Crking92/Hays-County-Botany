const state = {
  project: null,
  learning: null,
  manifestSpecies: [],
  species: [],
  speciesById: new Map(),
  familyCache: new Map(),
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
function imagePath(sp,img){
  if(!img || !img.file) return "";
  if(/^https?:\/\//i.test(img.file)) return img.file;
  if(img.file.startsWith("content/")) return encodeURI(img.file);
  return encodeURI(speciesBase(sp)+"/"+img.file);
}
function firstImage(sp){ return imagesFor(sp)[0] || null; }
function thumb(sp,cls){
  const img=firstImage(sp);
  if(img) return '<img class="'+cls+'" src="'+imagePath(sp,img)+'" alt="'+esc(scientificName(sp))+'" loading="lazy">';
  return '<div class="'+cls+' thumb-empty" aria-hidden="true">✣</div>';
}
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
  const tracker=sp.project_inclusion && sp.project_inclusion.target_zone_status;
  if(direct===true || tracker==="PASS" || sp.native_target_zone_calculated===true){
    const n=counties.length || sp.target_zone_count || (sp.target_zone_range && (sp.target_zone_range.target_zone_count_confirmed || sp.target_zone_range.target_zone_count_confirmed_minimum)) || "3+";
    return "PASS · "+n+" supported target-zone counties";
  }
  if(direct===false || tracker==="UNRESOLVED") return "UNRESOLVED · "+counties.length+" supported target-zone counties";
  if(sp.project_inclusion && sp.project_inclusion.strict_native_filter_deferred) return "Native-range audit deferred · local-occurrence-first study taxon";
  if(counties.length) return counties.length+" target-zone county records in current file";
  return "Range status not normalized yet";
}

function lookHereFirst(sp){
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
  return '<button class="term-chip" type="button" data-term="'+esc(id)+'"><span>'+esc(t.term)+'</span><b>?</b></button>';
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
  if(data.study_strategy && Array.isArray(data.study_strategy.shared_traits)) return data.study_strategy.shared_traits;
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
  if(item.user_decision && item.user_decision.decision) return false;
  const a=item.approval_status || "";
  const s=item.status || "";
  return ["ready_for_approval","ready_for_comparison_approval","needs_manual_review"].includes(a)
    || ["reviewed_ready_for_approval","reviewed_comparison_recommended","needs_manual_review"].includes(s);
}
function approvalDecisionText(item){
  const d=item.user_decision && item.user_decision.decision;
  if(!d) return "";
  const labels={
    approve_for_curation:"Approved for curation",
    approve_as_comparison:"Approved as comparison",
    approve_with_range_exception:"Approved with range exception",
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
  const comparisonSuggested=(item.approval_status==="ready_for_comparison_approval") || range==="FAIL" || String(item.learner_role||"").includes("COMPARISON");
  let out='<article class="approval-card" data-approval-item="'+esc(item.id)+'">'+
    '<div class="approval-card-top"><div><div class="eyebrow">'+esc(item.family||"")+" › "+esc(item.genus||"")+'</div><h3><i>'+esc(item.scientific_name||item.id)+'</i></h3></div>'+
    '<span class="approval-range '+approvalStatusClass(range)+'">'+esc(range)+'</span></div>'+
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
      (range!=="UNRESOLVED" && range!=="FAIL"?'<button class="approval-action approve" type="button" data-approval-decision="approve_for_curation" data-approval-id="'+esc(item.id)+'">Approve</button>':'')+
      '<button class="approval-action review" type="button" data-approval-decision="needs_more_review" data-approval-id="'+esc(item.id)+'">Needs more review</button>'+
      (comparisonSuggested?'<button class="approval-action compare" type="button" data-approval-decision="approve_as_comparison" data-approval-id="'+esc(item.id)+'">Keep as comparison</button>':'')+
      (range==="UNRESOLVED"?'<button class="approval-action exception" type="button" data-approval-decision="approve_with_range_exception" data-approval-id="'+esc(item.id)+'">Approve exception</button>':'')+
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
  const pendingCuration=all.filter(function(x){ return ["approved_pending_curation","approved_comparison_pending_curation"].includes(x.status); });
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

  let out='<section class="page-intro approval-intro"><div class="eyebrow">Human approval gate</div><h1>Review before curation.</h1>'+
    '<p>Scout and deep-review work can collect evidence, but nothing should move into final curation until you make the call here.</p></section>'+
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
  if(decision==="approve_with_range_exception" && !window.confirm("Approve this UNRESOLVED record as an explicit range exception? The unresolved evidence will remain documented.")) return;
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
  const discovered=Array.from(new Set(profiles.concat(Array.from(counts.keys())))).sort(function(a,b){ return a.localeCompare(b); });
  const families=preferred.concat(discovered.filter(function(f){ return !preferred.includes(f); }));
  const anchoredFamilies=families.filter(function(f){ return familySpecies(f).length; }).length;
  const level=state.learning.difficulty_levels[state.difficulty];
  let out='<section class="home-hero"><div class="eyebrow">Structure-first field botany</div>'+
    '<h1>Learn what to look at, then learn what it is called.</h1>'+
    '<p>Start with a plant or a family. The first screen stays simple; deeper botany is always one tap away.</p>'+
    '<div class="home-actions"><button class="primary-button" type="button" data-random-quiz>Quiz me with a random plant</button>'+
    '<button class="secondary-button" type="button" data-nav="browse">Browse Family → Genus → Species</button></div>'+
    '<div class="difficulty-explainer"><span>'+esc(level.label)+'</span><strong>'+esc(level.mantra)+'</strong><p>'+esc(level.description)+'</p></div></section>';
  out+='<section class="section-block family-library"><div class="section-heading"><div><div class="eyebrow">Start broad, then drill down</div><h2>Family Library</h2></div>'+
    '<button class="text-button" type="button" data-nav="browse">Open taxonomy browser →</button></div>'+
    '<p class="section-intro">Learn the recurring family pattern first, choose a genus, open a species, then compare it with close relatives and look-alikes.</p>'+
    '<div class="library-summary"><div><strong>'+families.length+'</strong><span>family lessons</span></div><div><strong>'+anchoredFamilies+'</strong><span>families with species anchors</span></div><div><strong>'+state.species.length+'</strong><span>curated species</span></div></div>'+
    '<div class="family-grid">';
  families.forEach(function(f){ out+=familyCard(f); });
  out+='</div></section><section class="method-strip"><div><b>1</b><span><strong>See it</strong>Start with the structure.</span></div>'+
    '<div><b>2</b><span><strong>Name it</strong>Tap terms as they appear.</span></div>'+
    '<div><b>3</b><span><strong>Compare it</strong>Put relatives side by side.</span></div></section>';
  return out;
}
function speciesTile(sp,showFamily){
  return '<button class="species-tile" type="button" data-species="'+sp.id+'">'+thumb(sp,"species-tile-img")+
    '<span>'+(showFamily?'<small>'+esc(sp.genus)+'</small>':'')+'<strong><i>'+esc(scientificName(sp))+'</i></strong>'+
    '<em>'+esc(commonName(sp))+'</em></span></button>';
}
function familyView(){
  const family=state.selectedFamily, p=familyProfile(family)||{}, members=familySpecies(family), genera=generaForFamily(family);
  const canon=state.familyCache.get(family);
  const signature=state.difficulty==="field" ? (p.field_signature||p.plain_signature) : (p.plain_signature||p.field_signature);
  let out='<section class="breadcrumbs"><button type="button" data-nav="home">Home</button><span>›</span><strong>'+esc(family)+'</strong></section>'+
    taxonomyLadder(family,null,null)+
    '<section class="family-hero"><div class="family-hero-copy"><div class="eyebrow">Family · '+members.length+' curated taxa</div><h1>'+esc(family)+'</h1>'+
    '<p class="family-common">'+esc(p.common_name || (canon&&canon.common_name) || "")+'</p>'+
    '<div class="look-card"><span>LOOK HERE FIRST</span><strong>'+esc(p.look_here_first||"Recognize the family structure before species-level details.")+'</strong></div>'+
    '<p class="family-signature">'+esc(signature||"")+'</p><div class="term-row">';
  (p.key_terms||[]).slice(0,state.difficulty==="simple"?4:9).forEach(function(id){ out+=termChip(id); });
  out+='</div><div class="button-row"><button class="primary-button" type="button" data-family-info="'+esc(family)+'">Why is this a family?</button>'+
    '<button class="secondary-button" type="button" data-nav="glossary">Open botanical terms</button></div></div><div class="family-photo-stack">';
  if(members.length) members.slice(0,4).forEach(function(sp){ out+='<button type="button" data-species="'+sp.id+'">'+thumb(sp,"family-stack-img")+'<span>'+esc(commonName(sp)||scientificName(sp))+'</span></button>'; });
  else out+='<div class="empty-panel">Family lesson ready. Canonical species anchors are still being installed.</div>';
  out+='</div></section><section class="section-block"><div class="section-heading"><div><div class="eyebrow">Narrow it down</div><h2>Genera in this learner</h2></div></div><div class="genus-buttons">';
  if(genera.length) genera.forEach(function(g){ out+='<button type="button" data-genus="'+esc(g[0])+'" data-genus-family="'+esc(family)+'"><i>'+esc(g[0])+'</i><span>'+g[1]+'</span></button>'; });
  else out+='<div class="empty-panel">No canonical genus anchors are installed yet. The family-level lesson above is still available.</div>';
  out+='</div></section><section class="section-block"><div class="section-heading"><div><div class="eyebrow">Recognize individuals</div><h2>Species</h2></div></div><div class="species-tile-grid">';
  if(members.length) members.forEach(function(sp){ out+=speciesTile(sp,true); });
  else out+='<div class="empty-panel">No canonical species anchors are installed for this family yet.</div>';
  out+='</div></section>';
  out+=familyComparePanel(family,members);
  return out;
}
function genusView(){
  const family=state.selectedGenusFamily, genus=state.selectedGenus;
  if(!family || !genus) return browseView();
  const members=genusSpecies(family,genus), data=state.genusCache.get(family+"/"+genus), p=familyProfile(family)||{};
  const shared=genusSharedTraits(data), priority=genusPriorityTraits(data), quick=genusQuickRows(data);
  const common=(data&&data.common_group)||genus;
  const warning=(data&&data.study_strategy&&data.study_strategy.warning) || (data&&Array.isArray(data.study_notes)&&data.study_notes[0]) || "";
  let out='<section class="breadcrumbs"><button type="button" data-nav="home">Home</button><span>›</span><button type="button" data-family="'+esc(family)+'">'+esc(family)+'</button><span>›</span><strong><i>'+esc(genus)+'</i></strong></section>'+
    taxonomyLadder(family,genus,null)+
    '<section class="genus-hero"><div><div class="eyebrow">Genus · '+members.length+' curated species</div><h1><i>'+esc(genus)+'</i></h1><p class="family-common">'+esc(common)+'</p>'+
    '<div class="look-card"><span>GENUS QUESTION</span><strong>What stays the same across '+esc(genus)+', and which smaller characters separate the species?</strong></div>'+
    (warning?'<p class="genus-warning">'+esc(warning)+'</p>':'')+'</div><div class="genus-photo-strip">';
  if(members.length) members.slice(0,3).forEach(function(sp){ out+='<button type="button" data-species="'+esc(sp.id)+'">'+thumb(sp,"genus-hero-img")+'<span>'+esc(commonName(sp)||scientificName(sp))+'</span></button>'; });
  else out+='<div class="empty-panel">Species anchors for this genus are still being installed.</div>';
  out+='</div></section>'+
    '<section class="two-column-learning genus-levels"><article class="learning-card"><div class="eyebrow">Family characters</div><h2>Why '+esc(family)+'?</h2><p>'+esc(p.plain_signature||p.field_signature||"Use the family lesson to recognize the broader structural pattern.")+'</p><button class="text-button" type="button" data-family="'+esc(family)+'">Open family →</button></article>'+
    '<article class="learning-card"><div class="eyebrow">Genus characters</div><h2>What makes <i>'+esc(genus)+'</i> hang together?</h2>';
  if(shared.length) out+='<ul class="trait-list">'+shared.slice(0,8).map(function(x){ return '<li>'+esc(formatValue(x))+'</li>'; }).join("")+'</ul>';
  else out+='<p>The genus-level diagnostic module is still being expanded. Use the species set and comparison key below in the meantime.</p>';
  out+='</article></section>';
  if(priority.length){
    out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Species-level characters</div><h2>Look here to separate '+esc(genus)+' species</h2></div></div><div class="diagnostic-chip-grid">';
    priority.slice(0,10).forEach(function(x){ out+='<div>'+esc(formatValue(x))+'</div>'; });
    out+='</div></section>';
  }
  if(quick.length){
    out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Quick separation key</div><h2>Character → likely species</h2></div></div><div class="genus-key">';
    quick.slice(0,12).forEach(function(row){ out+='<div><span>'+esc(row.if)+'</span><b>→</b><strong><i>'+esc(row.then)+'</i></strong></div>'; });
    out+='</div></section>';
  }
  out+='<section class="section-block"><div class="section-heading"><div><div class="eyebrow">Drill down</div><h2>'+esc(genus)+' species in the learner</h2></div></div><div class="species-tile-grid">';
  if(members.length) members.forEach(function(sp){ out+=speciesTile(sp,true); });
  else out+='<div class="empty-panel">No canonical species are installed for this genus yet.</div>';
  out+='</div></section>'+genusComparePanel(genus,members);
  return out;
}
function photoCarousel(sp){
  const imgs=imagesFor(sp);
  if(!imgs.length) return '<div class="focus-photo-empty">No curated photo installed yet.</div>';
  let idx=state.photoIndex[sp.id]||0; idx=((idx%imgs.length)+imgs.length)%imgs.length; state.photoIndex[sp.id]=idx;
  const img=imgs[idx], role=img.role||img.view||"Curated study image", credit=[img.creator||img.credit,img.license].filter(Boolean).join(" · ");
  let out='<figure class="focus-photo"><button class="focus-photo-image" type="button" data-photo-step="1" aria-label="Next photo"><img src="'+imagePath(sp,img)+'" alt="'+esc(scientificName(sp))+' — '+esc(role)+'"></button>'+
    '<div class="photo-topline"><span>'+esc(role)+'</span><b>'+(idx+1)+' / '+imgs.length+'</b></div>';
  if(imgs.length>1) out+='<button class="photo-arrow prev" type="button" data-photo-step="-1" aria-label="Previous photo">‹</button><button class="photo-arrow next" type="button" data-photo-step="1" aria-label="Next photo">›</button>';
  out+='<figcaption><span>'+esc(credit||"Source metadata retained in species record")+'</span>'+(img.source_page?'<a href="'+esc(img.source_page)+'" target="_blank" rel="noreferrer">source ↗</a>':'')+'</figcaption></figure>';
  return out;
}
function identityPanel(sp){
  if(state.quizMode && !state.quizRevealed){
    return '<div class="identity-panel mystery"><div class="eyebrow">Quiz mode</div><h1>Mystery plant</h1><p>Use the photo sequence and field characters before revealing the name.</p>'+
      '<button class="primary-button" type="button" data-reveal-quiz>Reveal identification</button></div>';
  }
  return '<div class="identity-panel"><div class="eyebrow">'+esc(sp.family)+' › '+esc(sp.genus)+'</div><h1><i>'+esc(scientificName(sp))+'</i></h1>'+
    '<p class="plant-common">'+esc(commonName(sp))+'</p>'+(sp.authority?'<p class="authority">'+esc(sp.authority)+'</p>':'')+
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

function familyVisualLessonHTML(canon){
  const lesson=canon && canon.visual_lesson;
  if(!lesson || !Array.isArray(lesson.steps) || !lesson.steps.length) return "";
  let out='<section class="family-visual-lesson"><div class="family-visual-heading"><div><div class="eyebrow">Visual family lesson</div><h3>See the pattern in local plants</h3></div><span>'+esc(lesson.status||"visual lesson")+'</span></div>';
  if(lesson.intro) out+='<p class="family-visual-intro">'+esc(lesson.intro)+'</p>';
  out+='<div class="family-visual-steps">';
  lesson.steps.forEach(function(step){
    const sp=step.anchor_species_id ? state.species.find(function(x){ return x.id===step.anchor_species_id; }) : null;
    out+='<article class="family-visual-step">';
    if(sp){
      out+='<button class="family-visual-photo" type="button" data-species="'+esc(sp.id)+'">'+familyVisualThumb(sp,step,"family-visual-img")+
        '<span><b>'+esc(commonName(sp)||scientificName(sp))+'</b><i>'+esc(scientificName(sp))+'</i></span></button>';
    }else if(familyExternalImageUrl(step)){
      out+=familyExternalVisual(step);
    }else{
      out+='<div class="family-visual-photo family-visual-placeholder"><span>Diagram / photo lock pending</span></div>';
    }
    out+='<div class="family-visual-copy"><div class="family-visual-step-title">'+esc(step.title||step.photo_role||"Look here")+'</div>';
    if(step.photo_role) out+='<small>'+esc(step.photo_role)+'</small>';
    if(step.look_for) out+='<p><b>Look for:</b> '+esc(step.look_for)+'</p>';
    if(step.why_it_matters) out+='<p><b>Why it matters:</b> '+esc(step.why_it_matters)+'</p>';
    if(step.status && /pending/i.test(step.status)) out+='<em class="visual-lock-status">Visual polish pending</em>';
    out+='</div></article>';
  });
  out+='</div>';
  if(Array.isArray(lesson.comparisons) && lesson.comparisons.length){
    out+='<div class="family-visual-comparisons"><h4>Fast tie-breakers</h4>';
    lesson.comparisons.forEach(function(c){ out+='<div><b>'+esc(c.title||"Compare")+'</b><span>'+esc(c.rule||"")+'</span></div>'; });
    out+='</div>';
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
  let out='<section class="section-block technical-section"><div class="section-heading"><div><div class="eyebrow">Field botany</div><h2>Technical morphology</h2></div><span class="range-badge">'+esc(rangeSummary(sp))+'</span></div><div class="morphology-grid">';
  rows.forEach(function(p){
    const ids=termsInText(titleCase(p[0])+" "+formatValue(p[1]),3);
    out+='<article class="morph-card"><b>'+esc(titleCase(p[0]))+'</b><p>'+esc(formatValue(p[1]))+'</p>'+(ids.length?'<div class="mini-terms">'+ids.map(termChip).join("")+'</div>':'')+'</article>';
  });
  out+='</div>';
  if(strategy) out+='<details class="genus-strategy"><summary>How to study <i>'+esc(sp.genus)+'</i> as a genus</summary><div>'+structuredTeachingHTML(strategy)+'</div></details>';
  out+='<details class="range-details"><summary>Project range evidence summary</summary><p>'+esc(rangeSummary(sp))+'</p>'+
    (countyList(sp).length?'<p><b>Supported target-zone counties in this file:</b> '+esc(countyList(sp).join(", "))+'</p>':'')+'</details></section>';
  return out;
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
  if(!state.quizMode) out+=taxonomyLadder(sp.family,sp.genus,sp);
  out+='<section class="plant-focus"><div class="plant-visual">'+photoCarousel(sp)+'</div><div class="plant-study">'+identityPanel(sp)+
    '<div class="look-card emphasis"><span>LOOK HERE FIRST</span><strong>'+esc(lookHereFirst(sp))+'</strong></div><div class="cue-list">';
  cues.forEach(function(x){ out+='<div><b aria-hidden="true">→</b><span>'+esc(x)+'</span></div>'; });
  out+='</div><div class="study-actions"><button class="primary-button" type="button" data-family-info="'+esc(sp.family)+'">Why '+esc(sp.family)+'?</button>'+
    (similar.length?'<button class="secondary-button" type="button" data-jump="similar">Compare similar plants</button>':'')+
    (state.difficulty==="simple"?'<button class="secondary-button" type="button" data-set-difficulty="terms">Teach me the terms</button>':'')+'</div></div></section>';
  if(state.difficulty!=="simple"){
    out+='<section class="section-block learning-panel"><div class="section-heading"><div><div class="eyebrow">See it → name it → use it</div><h2>Botanical words on this plant</h2></div>'+
      '<button class="text-button" type="button" data-nav="glossary">Full glossary →</button></div><div class="term-row large">'+terms.map(termChip).join("")+'</div>'+
      '<p class="teaching-note">Tap a term for plain language, the formal definition, where to look, why it matters, and a labeled diagram.</p></section>';
  }
  out+='<section class="two-column-learning"><article class="learning-card"><div class="eyebrow">Family pattern</div><h2>Why does this fit '+esc(sp.family)+'?</h2><p>'+esc(familyConnection)+'</p>'+
    '<button class="text-button" type="button" data-family-info="'+esc(sp.family)+'">Open family lesson →</button></article>'+
    '<article class="learning-card"><div class="eyebrow">Species-level clue</div><h2>What makes this one stand out?</h2><p>'+esc(c.standout || lookHereFirst(sp))+'</p><p class="muted">'+esc(p.caveat||"")+'</p></article></section>';
  out+='<section id="similarSection" class="section-block"><div class="section-heading"><div><div class="eyebrow">Train your eye</div><h2>Compare with look-alikes and relatives</h2></div></div>'+
    '<p class="section-intro">“Same genus” means close taxonomic relatives. “Useful comparison” is a hand-picked study pairing. “Same family” shares family structure but may not look alike overall.</p><div class="similar-grid">';
  if(similar.length) similar.forEach(function(x){ out+=similarCard(sp,x.sp,x.reason); }); else out+='<div class="empty-panel">No comparison plants are curated yet.</div>';
  out+='</div></section>';
  if(state.difficulty==="field") out+=fieldBotanySection(sp,genusData);
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
  let out='<section class="page-intro compare-intro"><div class="eyebrow">Botanical compare & contrast</div><h1>Compare any two plants in the learner.</h1><p>Move from broad characters to narrow ones: family first, genus second, species last.</p></section>'+
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
  const families=Array.from(new Set(state.species.map(function(sp){ return sp.family; }).concat(Object.keys((state.learning&&state.learning.family_profiles)||{})))).sort();
  const genera=state.browseFamily ? generaForFamily(state.browseFamily).map(function(x){ return x[0]; }) : [];
  let list=state.species.slice();
  if(state.browseFamily) list=list.filter(function(sp){ return sp.family===state.browseFamily; });
  if(state.browseGenus) list=list.filter(function(sp){ return sp.genus===state.browseGenus; });
  let out='<section class="page-intro"><div class="eyebrow">Taxonomy browser</div><h1>Family → Genus → Species</h1><p>Use this when you want to learn the hierarchy instead of searching by name.</p></section>'+
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
  const ids=Object.keys(state.learning.terms||{});
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
function openTermDrill(){
  chooseTermDrill(); renderTermDrillModal();
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
    '<input id="glossarySearch" class="glossary-search" value="'+esc(state.glossaryQuery)+'" placeholder="Search phyllary, opposite, cupule…"></section><section class="glossary-grid">';
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
  else if(state.view==="plant") els.app.innerHTML=plantView();
  else if(state.view==="compare") els.app.innerHTML=compareView();
  else if(state.view==="browse") els.app.innerHTML=browseView();
  else if(state.view==="glossary") els.app.innerHTML=glossaryView();
  else if(state.view==="approvals") els.app.innerHTML=approvalsView();
  else els.app.innerHTML=homeView();
  if(state.view==="approvals") requestAnimationFrame(hydrateVisibleApprovalPhotos);
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
    const sci=scientificName(sp), common=commonName(sp), body=norm([sci,common,sp.genus,sp.family].concat(sp.other_common_names||[]).join(" "));
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
      '<em>'+esc(commonName(sp))+'</em><small>'+esc(sp.family)+' › '+esc(sp.genus)+'</small></span></button>';
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
  return '<svg class="term-annotation-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><marker id="termArrow" markerWidth="5" markerHeight="5" refX="4.2" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 z"></path></marker></defs>'+lines+'</svg>'+labels;
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
  if(e.target.closest("[data-term-drill-start]")){ openTermDrill(); return; }
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
  const photo=e.target.closest("[data-photo-step]");
  if(photo){
    const sp=selectedSpecies(), imgs=sp?imagesFor(sp):[];
    if(sp && imgs.length){ const cur=state.photoIndex[sp.id]||0; state.photoIndex[sp.id]=(cur+Number(photo.dataset.photoStep)+imgs.length)%imgs.length; render(); }
    return;
  }
  if(e.target.closest("[data-reveal-quiz]")){ state.quizRevealed=true; render(); return; }
  if(e.target.closest("[data-next-quiz]") || e.target.closest("[data-random-quiz]")){ randomQuiz(); return; }
  const jump=e.target.closest("[data-jump]"); if(jump){ const target=document.getElementById(jump.dataset.jump+"Section"); if(target) target.scrollIntoView({behavior:"smooth",block:"start"}); return; }
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
    state.species.sort(function(a,b){ return (a.family||"").localeCompare(b.family||"") || (a.genus||"").localeCompare(b.genus||"") || scientificName(a).localeCompare(scientificName(b)); });
    state.species.forEach(function(sp){ state.speciesById.set(sp.id,sp); });
    if(!state.learning.difficulty_levels[state.difficulty]) state.difficulty="terms";
    bind(); render();
  }catch(err){
    els.app.innerHTML='<section class="error-card"><h1>Could not load the learner.</h1><p>'+esc(err.message)+'</p><p>Make sure this folder is running through <code>RUN_LOCAL_SERVER.bat</code>.</p></section>';
  }
}
boot();

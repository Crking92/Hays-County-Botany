const state = { species: [], targetCounties: [], studyMode: false };

async function loadJSON(path){ const r = await fetch(path); if(!r.ok) throw new Error(`${r.status} ${path}`); return r.json(); }

async function boot(){
  try{
    const manifest = await loadJSON("data/manifest.json");
    const project = await loadJSON(manifest.project);
    state.targetCounties = project.target_zone_counties;
    state.species = await Promise.all(manifest.species.map(x => loadJSON(x.path)));
    buildFilters();
    render();
  }catch(err){
    document.querySelector("#grid").innerHTML =
      `<div class="empty warning"><b>Could not load JSON files.</b><br>
      Open this folder through a local web server (see START-HERE.txt).<br><br>${err.message}</div>`;
  }
}

function buildFilters(){
  const families = [...new Set(state.species.map(x=>x.family))].sort();
  const tags = [...new Set(state.species.flatMap(x=>x.tags||[]))].sort();
  fill("familyFilter", ["All families", ...families]);
  fill("countyFilter", ["All counties", ...state.targetCounties]);
  fill("tagFilter", ["All tags", ...tags]);
}

function fill(id, values){
  const sel = document.getElementById(id);
  sel.innerHTML = values.map(v => `<option value="${v.startsWith("All ") ? "" : v}">${v}</option>`).join("");
}

function filteredSpecies(){
  const q = document.getElementById("search").value.trim().toLowerCase();
  const fam = document.getElementById("familyFilter").value;
  const county = document.getElementById("countyFilter").value;
  const tag = document.getElementById("tagFilter").value;

  return state.species.filter(sp => {
    const text = `${sp.genus} ${sp.species} ${sp.common_name} ${(sp.tags||[]).join(" ")}`.toLowerCase();
    return (!q || text.includes(q))
      && (!fam || sp.family === fam)
      && (!county || (sp.county_occurrences_target_zone||[]).includes(county))
      && (!tag || (sp.tags||[]).includes(tag));
  });
}

function card(sp){
  const sci = `${sp.genus} ${sp.species}`;
  const traits = Object.entries(sp.morphology_keys||{}).map(([k,v]) =>
    `<div class="trait"><b>${k.replaceAll("_"," ")}</b>${v}</div>`
  ).join("");

  return `<article class="card ${state.studyMode ? "hidden-study" : ""}">
    <div class="answer">
      <h2><span class="latin">${sci}</span> ${sp.authority||""}</h2>
      <div class="common">${sp.common_name||""}</div>
    </div>
    <div class="tags">${(sp.tags||[]).map(t=>`<span class="tag">${t}</span>`).join("")}</div>
    <div class="traits answer">${traits}</div>
    <p class="answer"><b>Target-zone county records:</b> ${sp.target_zone_count || 0}</p>
    <button class="reveal" onclick="this.parentElement.querySelectorAll('.answer').forEach(x=>x.classList.toggle('revealed'))">
      Reveal / Hide
    </button>
  </article>`;
}

function render(){
  const list = filteredSpecies();
  document.getElementById("stats").textContent = `${list.length} species shown`;
  document.getElementById("grid").innerHTML = list.length ? list.map(card).join("") : `<div class="empty">No matches.</div>`;
}

["search","familyFilter","countyFilter","tagFilter"].forEach(id=>{
  document.addEventListener("input", e => { if(e.target.id===id) render(); });
  document.addEventListener("change", e => { if(e.target.id===id) render(); });
});

document.addEventListener("click", e=>{
  if(e.target.id==="studyToggle"){
    state.studyMode = !state.studyMode;
    e.target.classList.toggle("on", state.studyMode);
    e.target.textContent = state.studyMode ? "Study Mode: ON" : "Study Mode: OFF";
    render();
  }
});

boot();
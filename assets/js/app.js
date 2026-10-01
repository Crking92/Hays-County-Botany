const state = { species: [], targetCounties: [], studyMode: false };

async function loadJSON(path){
  const r = await fetch(path);
  if(!r.ok) throw new Error(`${r.status} ${path}`);
  return r.json();
}

async function boot(){
  try{
    const manifest = await loadJSON("data/manifest.json");
    const project = await loadJSON(manifest.project);
    state.targetCounties = project.target_zone_counties || [];
    state.manifestSpecies = manifest.species || [];
    state.species = await Promise.all(state.manifestSpecies.map(x => loadJSON(x.path)));
    buildFilters();
    render();
  }catch(err){
    document.querySelector("#grid").innerHTML =
      `<div class="empty warning"><b>Could not load JSON files.</b><br>
      Open this folder through a local web server (see START-HERE.txt).<br><br>${err.message}</div>`;
  }
}

function scientificName(sp){
  if(sp.scientific_name) return sp.scientific_name;
  const bits = [sp.genus, sp.species].filter(Boolean);
  if(sp.subspecies) bits.push("subsp.", sp.subspecies);
  if(sp.variety) bits.push("var.", sp.variety);
  return bits.join(" ") || sp.accepted_name || sp.id || "Unnamed taxon";
}

function countyList(sp){
  let counties = [];
  if(Array.isArray(sp.county_occurrences_target_zone)) counties = sp.county_occurrences_target_zone;
  else if(Array.isArray(sp.target_zone_range?.confirmed_target_zone_counties)) counties = sp.target_zone_range.confirmed_target_zone_counties;
  else if(typeof sp.verified_target_counties === "string") counties = sp.verified_target_counties.split(";").map(x=>x.trim());
  else if(Array.isArray(sp.county_occurrences_reported)) counties = sp.county_occurrences_reported;

  return [...new Set(counties.filter(x => state.targetCounties.includes(x)))];
}

function rangeSummary(sp){
  const counties = countyList(sp);
  const directStatus = sp.target_zone_range?.meets_three_county_rule;
  const trackerStatus = sp.project_inclusion?.target_zone_status;

  if(directStatus === true || trackerStatus === "PASS" || sp.native_target_zone_calculated === true){
    return `PASS · ${counties.length || sp.target_zone_count || sp.target_zone_range?.target_zone_count_confirmed || sp.target_zone_range?.target_zone_count_confirmed_minimum || "3+"} supported target-zone counties`;
  }
  if(directStatus === false || trackerStatus === "UNRESOLVED"){
    return `UNRESOLVED · ${counties.length} supported target-zone counties`;
  }
  if(sp.project_inclusion?.strict_native_filter_deferred){
    return `Native-range audit deferred · local-occurrence-first study taxon`;
  }
  if(counties.length){
    return `${counties.length} target-zone county records in current file`;
  }
  return "Range status not normalized yet";
}

function formatValue(value){
  if(Array.isArray(value)) return value.join(" · ");
  if(value && typeof value === "object"){
    return Object.entries(value).map(([k,v]) => `${k.replaceAll("_"," ")}: ${formatValue(v)}`).join(" | ");
  }
  return value ?? "";
}

function buildFilters(){
  const families = [...new Set(state.species.map(x=>x.family).filter(Boolean))].sort();
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
    const text = [
      scientificName(sp),
      sp.authority,
      sp.common_name,
      ...(sp.other_common_names||[]),
      ...(sp.tags||[])
    ].filter(Boolean).join(" ").toLowerCase();

    return (!q || text.includes(q))
      && (!fam || sp.family === fam)
      && (!county || countyList(sp).includes(county))
      && (!tag || (sp.tags||[]).includes(tag));
  });
}

function card(sp){
  const sci = scientificName(sp);
  const traits = Object.entries(sp.morphology_keys||{}).map(([k,v]) =>
    `<div class="trait"><b>${k.replaceAll("_"," ")}</b>${formatValue(v)}</div>`
  ).join("");
  const images = Array.isArray(sp.images) ? sp.images : [];
  const firstImage = images.find(img => img && img.file);
  const imageBlock = firstImage
    ? `<figure class="card-photo">
        <img src="${encodeURI(firstImage.file.startsWith("content/") ? firstImage.file : findSpeciesBase(sp) + "/" + firstImage.file)}" alt="${sci} — ${firstImage.role || firstImage.view || "curated study image"}" loading="lazy">
        <figcaption>${firstImage.role || firstImage.view || "Curated image"} · ${firstImage.creator || firstImage.credit || "source recorded"}${firstImage.license ? " · " + firstImage.license : ""}</figcaption>
      </figure>`
    : `<div class="photo-missing">No curated photo installed yet</div>`;

  return `<article class="card ${state.studyMode ? "hidden-study" : ""}">
    ${imageBlock}
    <div class="answer">
      <h2><span class="latin">${sci}</span> ${sp.authority||""}</h2>
      <div class="common">${sp.common_name||""}</div>
    </div>
    <div class="tags">${(sp.tags||[]).map(t=>`<span class="tag">${t}</span>`).join("")}</div>
    <div class="traits answer">${traits}</div>
    <p class="answer"><b>Project range:</b> ${rangeSummary(sp)}</p>
    <button class="reveal" onclick="this.parentElement.querySelectorAll('.answer').forEach(x=>x.classList.toggle('revealed'))">
      Reveal / Hide
    </button>
  </article>`;
}

function findSpeciesBase(sp){
  const entry = state.manifestSpecies?.find(x => x.id === sp.id);
  if(!entry?.path) return "";
  return entry.path.replace(/\/species\.json$/, "");
}

function render(){
  const list = filteredSpecies();
  document.getElementById("stats").textContent = `${list.length} of ${state.species.length} taxa shown`;
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
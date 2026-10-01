const state = {
  species: [],
  manifestSpecies: [],
  targetCounties: [],
  studyMode: false,
  photoIndex: {}
};

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
    state.species.sort((a,b) =>
      (a.family || "").localeCompare(b.family || "") ||
      (a.genus || "").localeCompare(b.genus || "") ||
      scientificName(a).localeCompare(scientificName(b))
    );
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
  else if(typeof sp.verified_target_counties === "string") counties = sp.verified_target_counties.split(";").map(x => x.trim());
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
    return "Native-range audit deferred · local-occurrence-first study taxon";
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

function countBy(values){
  const counts = new Map();
  values.forEach(v => counts.set(v, (counts.get(v) || 0) + 1));
  return counts;
}

function setOptions(select, options, placeholder, selectedValue=""){
  select.innerHTML = [
    `<option value="">${placeholder}</option>`,
    ...options.map(o => `<option value="${o.value}">${o.label}</option>`)
  ].join("");
  if(options.some(o => o.value === selectedValue)) select.value = selectedValue;
}

function buildFilters(){
  const family = document.getElementById("familyFilter");
  const familyCounts = countBy(state.species.map(x => x.family).filter(Boolean));
  const families = [...familyCounts.keys()].sort().map(name => ({
    value: name,
    label: `${name} (${familyCounts.get(name)})`
  }));
  setOptions(family, families, "All families");

  fillSimple("countyFilter", ["All counties", ...state.targetCounties]);
  const tags = [...new Set(state.species.flatMap(x => x.tags || []))].sort();
  fillSimple("tagFilter", ["All tags", ...tags]);

  refreshTaxonomyChildren();
}

function fillSimple(id, values){
  const sel = document.getElementById(id);
  sel.innerHTML = values.map(v => `<option value="${v.startsWith("All ") ? "" : v}">${v}</option>`).join("");
}

function refreshTaxonomyChildren({preserveGenus=false, preserveSpecies=false}={}){
  const familySel = document.getElementById("familyFilter");
  const genusSel = document.getElementById("genusFilter");
  const speciesSel = document.getElementById("speciesFilter");

  const family = familySel.value;
  const oldGenus = preserveGenus ? genusSel.value : "";
  const oldSpecies = preserveSpecies ? speciesSel.value : "";

  const familySpecies = family
    ? state.species.filter(sp => sp.family === family)
    : [];

  const genusCounts = countBy(familySpecies.map(sp => sp.genus).filter(Boolean));
  const genera = [...genusCounts.keys()].sort().map(name => ({
    value: name,
    label: `${name} (${genusCounts.get(name)})`
  }));

  setOptions(genusSel, genera, family ? "All genera" : "Choose family first", oldGenus);
  genusSel.disabled = !family;

  const genus = genusSel.value;
  const speciesPool = genus
    ? familySpecies.filter(sp => sp.genus === genus)
    : familySpecies;

  const speciesOptions = speciesPool.map(sp => ({
    value: sp.id,
    label: `${scientificName(sp)}${sp.common_name ? " — " + sp.common_name : ""}`
  }));

  setOptions(speciesSel, speciesOptions, family ? "All species" : "Choose family first", oldSpecies);
  speciesSel.disabled = !family;
}

function filteredSpecies(){
  const q = document.getElementById("search").value.trim().toLowerCase();
  const family = document.getElementById("familyFilter").value;
  const genus = document.getElementById("genusFilter").value;
  const speciesId = document.getElementById("speciesFilter").value;
  const county = document.getElementById("countyFilter").value;
  const tag = document.getElementById("tagFilter").value;

  return state.species.filter(sp => {
    const text = [
      scientificName(sp),
      sp.authority,
      sp.common_name,
      ...(sp.other_common_names || []),
      ...(sp.tags || [])
    ].filter(Boolean).join(" ").toLowerCase();

    return (!q || text.includes(q))
      && (!family || sp.family === family)
      && (!genus || sp.genus === genus)
      && (!speciesId || sp.id === speciesId)
      && (!county || countyList(sp).includes(county))
      && (!tag || (sp.tags || []).includes(tag));
  });
}

function findSpeciesBase(sp){
  const entry = state.manifestSpecies.find(x => x.id === sp.id);
  if(!entry?.path) return "";
  return entry.path.replace(/\/species\.json$/, "");
}

function imagePath(sp, image){
  if(!image?.file) return "";
  if(image.file.startsWith("content/")) return encodeURI(image.file);
  return encodeURI(`${findSpeciesBase(sp)}/${image.file}`);
}

function validImages(sp){
  return (Array.isArray(sp.images) ? sp.images : []).filter(img => img && img.file);
}

function photoMarkup(sp){
  const images = validImages(sp);
  if(!images.length){
    return `<div class="photo-missing">No curated photo installed yet</div>`;
  }

  const rawIndex = state.photoIndex[sp.id] || 0;
  const index = ((rawIndex % images.length) + images.length) % images.length;
  state.photoIndex[sp.id] = index;
  const img = images[index];
  const role = img.role || img.view || "Curated study image";
  const creator = img.creator || img.credit || "";
  const license = img.license || "";
  const credit = [creator, license].filter(Boolean).join(" · ");

  return `<figure class="card-photo" data-photo-card="${sp.id}">
    <div class="photo-stage">
      <button type="button" class="photo-image-button" data-photo-action="next" aria-label="Next photo for ${scientificName(sp)}">
        <img src="${imagePath(sp, img)}" alt="${scientificName(sp)} — ${role}" loading="lazy">
      </button>
      <div class="photo-role">${role}</div>
      <div class="photo-counter">${index + 1} / ${images.length}</div>
      ${images.length > 1 ? `
        <button type="button" class="photo-nav photo-prev" data-photo-action="prev" aria-label="Previous photo">‹</button>
        <button type="button" class="photo-nav photo-next" data-photo-action="next" aria-label="Next photo">›</button>
      ` : ""}
    </div>
    <figcaption>
      <span>${credit || "Source metadata retained in species record"}</span>
      ${images.length > 1 ? "<span class=\"cycle-hint\">Click photo or arrows to cycle</span>" : ""}
    </figcaption>
  </figure>`;
}

function card(sp){
  const sci = scientificName(sp);
  const traits = Object.entries(sp.morphology_keys || {}).map(([k,v]) =>
    `<div class="trait"><b>${k.replaceAll("_"," ")}</b>${formatValue(v)}</div>`
  ).join("");

  return `<article class="card ${state.studyMode ? "hidden-study" : ""}" data-species-id="${sp.id}">
    ${photoMarkup(sp)}
    <div class="identity answer">
      <div class="taxonomy-line">${sp.family || ""} › ${sp.genus || ""}</div>
      <h2><span class="latin">${sci}</span> ${sp.authority || ""}</h2>
      <div class="common">${sp.common_name || ""}</div>
    </div>
    <div class="tags">${(sp.tags || []).map(t => `<span class="tag">${t}</span>`).join("")}</div>
    <div class="traits answer">${traits}</div>
    <p class="answer range-line"><b>Project range:</b> ${rangeSummary(sp)}</p>
    <button class="reveal" type="button" data-reveal>Reveal / Hide ID + traits</button>
  </article>`;
}

function taxonomyTrail(){
  const family = document.getElementById("familyFilter").value;
  const genus = document.getElementById("genusFilter").value;
  const speciesId = document.getElementById("speciesFilter").value;
  const sp = speciesId ? state.species.find(x => x.id === speciesId) : null;
  return [family, genus, sp ? scientificName(sp) : ""].filter(Boolean).join(" → ");
}

function render(){
  const list = filteredSpecies();
  const trail = taxonomyTrail();
  const familyCount = new Set(list.map(x => x.family).filter(Boolean)).size;
  const genusCount = new Set(list.map(x => x.genus).filter(Boolean)).size;
  document.getElementById("stats").innerHTML =
    `<strong>${list.length}</strong> of ${state.species.length} taxa shown · ${familyCount} families · ${genusCount} genera`
    + (trail ? `<span class="active-trail">${trail}</span>` : "");

  document.getElementById("grid").innerHTML = list.length
    ? list.map(card).join("")
    : `<div class="empty">No matches. Try clearing a taxonomy level or search filter.</div>`;
}

function updateSinglePhoto(speciesId, delta){
  const sp = state.species.find(x => x.id === speciesId);
  if(!sp) return;
  const images = validImages(sp);
  if(images.length < 2) return;

  const current = state.photoIndex[speciesId] || 0;
  state.photoIndex[speciesId] = (current + delta + images.length) % images.length;

  const cardEl = document.querySelector(`[data-species-id="${speciesId}"]`);
  const photoEl = cardEl?.querySelector("[data-photo-card]");
  if(photoEl) photoEl.outerHTML = photoMarkup(sp);
}

document.getElementById("familyFilter").addEventListener("change", () => {
  refreshTaxonomyChildren();
  render();
});

document.getElementById("genusFilter").addEventListener("change", () => {
  refreshTaxonomyChildren({preserveGenus:true});
  render();
});

document.getElementById("speciesFilter").addEventListener("change", render);

["search","countyFilter","tagFilter"].forEach(id => {
  document.getElementById(id).addEventListener("input", render);
  document.getElementById(id).addEventListener("change", render);
});

document.getElementById("clearTaxonomy").addEventListener("click", () => {
  document.getElementById("familyFilter").value = "";
  refreshTaxonomyChildren();
  render();
});

document.getElementById("studyToggle").addEventListener("click", e => {
  state.studyMode = !state.studyMode;
  e.currentTarget.classList.toggle("on", state.studyMode);
  e.currentTarget.textContent = state.studyMode ? "Study Mode: ON" : "Study Mode: OFF";
  render();
});

document.getElementById("grid").addEventListener("click", e => {
  const photoAction = e.target.closest("[data-photo-action]");
  if(photoAction){
    const cardEl = photoAction.closest("[data-species-id]");
    const speciesId = cardEl?.dataset.speciesId;
    if(speciesId){
      updateSinglePhoto(speciesId, photoAction.dataset.photoAction === "prev" ? -1 : 1);
    }
    return;
  }

  const reveal = e.target.closest("[data-reveal]");
  if(reveal){
    const cardEl = reveal.closest(".card");
    cardEl?.querySelectorAll(".answer").forEach(x => x.classList.toggle("revealed"));
  }
});

boot();

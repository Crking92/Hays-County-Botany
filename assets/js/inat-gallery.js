/* On-demand iNaturalist observation photo browser for public noncommercial Hays Botany.
 * Photos stay on iNaturalist, never silently become canonical diagnostics.
 * No app data or image bytes are written to the repository by this module. */
(function () {
  'use strict';
  const API = 'https://api.inaturalist.org/v1/';
  const LIMIT = 18;
  const PHOTO_LICENSES = Object.freeze({
    cc0: ['CC0', 'https://creativecommons.org/publicdomain/zero/1.0/'],
    'cc-by': ['CC BY', 'https://creativecommons.org/licenses/by/4.0/'],
    'cc-by-sa': ['CC BY-SA', 'https://creativecommons.org/licenses/by-sa/4.0/'],
    'cc-by-nc': ['CC BY-NC', 'https://creativecommons.org/licenses/by-nc/4.0/'],
    'cc-by-nc-sa': ['CC BY-NC-SA', 'https://creativecommons.org/licenses/by-nc-sa/4.0/']
  });
  const cache = new Map();
  let placeCache = null;

  function escapeHTML(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, c =>
      ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', "'":'&#39;'}[c]));
  }
  function safePhoto(url) {
    if (typeof url !== 'string') return '';
    try {
      const u = new URL(url);
      if (u.protocol !== 'https:') return '';
      if (!['inaturalist-open-data.s3.amazonaws.com',
            'static.inaturalist.org', 'inaturalist-production.s3.amazonaws.com'].includes(u.hostname)) return '';
      // iNaturalist documents size replacements for these image URLs.
      u.pathname = u.pathname.replace(/\/(?:square|thumb|small)\.(jpe?g|png)$/i, '/medium.$1');
      return u.toString();
    } catch (err) { return ''; }
  }
  async function json(endpoint, params) {
    const qs = new URLSearchParams(params || {});
    const response = await fetch(API + endpoint + '?' + qs, {
      mode: 'cors', cache: 'no-store', headers: {Accept: 'application/json'}
    });
    if (!response.ok) throw new Error('iNaturalist service returned ' + response.status);
    return response.json();
  }
  function placeMatch(place, type) {
    const title = (String(place.display_name || '') + ' ' + String(place.name || '')).toLowerCase();
    if (type === 'hays') {
      return /hays county/.test(title) && /(?:texas|,\s*tx\b|us,\s*tx\b)/.test(title);
    }
    return /^(texas|texas, us|texas, united states|texas, us, tx)$/i.test(String(place.name || place.display_name || '').trim())
      || /^texas\b/i.test(title) && Number(place.place_type) === 8;
  }
  async function places() {
    if (placeCache) return placeCache;
    const find = async (q, type) => {
      try {
        const result = await json('places/autocomplete', {q});
        const match = (result.results || []).find(p => placeMatch(p, type));
        return match && Number.isSafeInteger(Number(match.id)) ? Number(match.id) : null;
      } catch (err) { return null; }
    };
    const resolved = await Promise.all([
      find('Hays County, Texas', 'hays'), find('Texas', 'texas')
    ]);
    placeCache = {hays: resolved[0], texas: resolved[1]};
    return placeCache;
  }
  function sameTaxon(observed, requested) {
    if (!observed || !requested) return false;
    const obs = String(observed).trim().toLowerCase();
    const name = String(requested).trim().toLowerCase();
    // Species-level match or an explicitly nested subspecies/variety.
    return obs === name || obs.startsWith(name + ' subsp. ') ||
      obs.startsWith(name + ' ssp. ') || obs.startsWith(name + ' var. ');
  }
  function parsePhotos(results, targetName, region, found) {
    for (const obs of results || []) {
      if (!obs || obs.quality_grade !== 'research' ||
          !sameTaxon(obs.taxon && obs.taxon.name, targetName) ||
          !Number.isSafeInteger(Number(obs.id))) continue;
      const observation = 'https://www.inaturalist.org/observations/' + Number(obs.id);
      // At most two from one observation: a broad range of observers is more useful.
      let admitted = 0;
      for (const photo of obs.photos || []) {
        if (admitted >= 2 || found.length >= LIMIT) break;
        if (!photo || !Number.isSafeInteger(Number(photo.id))) continue;
        const lic = PHOTO_LICENSES[String(photo.license_code || '').toLowerCase()];
        if (!lic) continue;  // No unknown / ND / all-rights-reserved photos.
        const url = safePhoto(photo.url);
        const creator = String(photo.attribution || '').trim();
        if (!url || !creator) continue;
        const id = String(photo.id);
        if (found.some(p => p.id === id)) continue;
        found.push({
          id: id, url: url, photoPage: 'https://www.inaturalist.org/photos/' + id,
          observation: observation, creator: creator, license: lic[0],
          licenseUrl: lic[1], region: region
        });
        admitted++;
      }
      if (found.length >= LIMIT) break;
    }
  }
  async function observations(name, area, photos) {
    if (photos.length >= LIMIT) return;
    const filter = {taxon_name: name, quality_grade: 'research', photos: 'true',
      per_page: '90', order: 'desc', order_by: 'observed_on'};
    if (area.place) filter.place_id = String(area.place);
    if (area.bounds) Object.assign(filter, area.bounds);
    const data = await json('observations', filter);
    parsePhotos(data.results || [], name, area.label, photos);
  }
  async function load(name) {
    const result = [];
    const loc = await places();
    const areas = [
      loc.hays ?
        {label:'Hays County', place:loc.hays} :
        {label:'Hays area (approximate)', bounds:{swlat:'29.77',swlng:'-98.32',nelat:'30.22',nelng:'-97.56'}},
      {label:'Nearby Central Texas', bounds:{swlat:'29.4',swlng:'-99.05',nelat:'30.9',nelng:'-97.15'}},
      loc.texas ?
        {label:'Elsewhere in Texas', place:loc.texas} :
        {label:'Texas region (approximate)', bounds:{swlat:'25.8',swlng:'-106.7',nelat:'36.5',nelng:'-93.5'}}
    ];
    let failures = 0;
    for (const area of areas) {
      if (result.length >= LIMIT) break;
      try { await observations(name, area, result); }
      catch (err) { failures++; }
    }
    if (!result.length && failures === areas.length) {
      throw new Error('The iNaturalist photo service is temporarily unavailable.');
    }
    return result;
  }
  function header(name) {
    // This section is rendered at the existing button position, immediately
    // below the species overview. The drawer expands right under that button.
    return '<section class="inat-photo-jump inat-explore" id="inatExplore" data-inat-species="'+escapeHTML(name)+'">'+
      '<button class="button secondary inat-launch" type="button" data-inat-open aria-expanded="false" aria-controls="inatPhotoDrawer">Explore iNaturalist photos ↓</button>'+
      '<div id="inatPhotoDrawer" data-inat-drawer hidden></div>'+
      '</section>';
  }
  function cards(photos) {
    return '<div class="inat-controls"><button type="button" class="button secondary" data-inat-scroll="-1" aria-label="Previous iNaturalist photos">← Previous</button>'+
      '<span class="mini">' + photos.length + ' licensed photos · Swipe sideways to browse</span>'+
      '<button type="button" class="button secondary" data-inat-scroll="1" aria-label="Next iNaturalist photos">Next →</button></div>'+
      '<div class="photostrip inat-strip" id="inatPhotoStrip" tabindex="0" role="region" aria-label="iNaturalist species photo carousel">'+
      photos.map(photo => '<article class="tile inat-tile">'+
        '<a href="' + escapeHTML(photo.photoPage) + '" target="_blank" rel="noopener noreferrer" aria-label="Open original iNaturalist photo">'+
        '<img src="' + escapeHTML(photo.url) + '" alt="Community-observed plant photograph from '+
        escapeHTML(photo.region) + '" loading="lazy" decoding="async" referrerpolicy="no-referrer"></a>'+
        '<div class="tilebody"><div class="role">' + escapeHTML(photo.region) + ' · Research Grade observation</div>'+
        '<small>' + escapeHTML(photo.creator) + '</small><small><a href="' + escapeHTML(photo.licenseUrl) +
        '" target="_blank" rel="noopener noreferrer">' + escapeHTML(photo.license) + ' license</a></small>'+
        '<a href="' + escapeHTML(photo.photoPage) + '" target="_blank" rel="noopener noreferrer">Original photo ↗</a>'+
        ' · <a href="' + escapeHTML(photo.observation) +
        '" target="_blank" rel="noopener noreferrer">Observation ↗</a></div></article>').join('')+
      '</div><p class="mini">Photos are loaded on demand from iNaturalist, remain hosted there, and are not added to the project’s verified diagnostic gallery. No private coordinates are shown. '+
      'CC BY-NC and CC BY-NC-SA images are displayed only under this site’s noncommercial educational use.</p>';
  }
  function body(record) {
    const intro='<div class="inat-inline-intro"><div class="stepbar">Community photo examples</div>'+
      '<h2>iNaturalist observation photos</h2>'+
      '<p class="intro">Browse additional community photographs of <i>'+escapeHTML(record.name)+'</i>. '+
      'Research Grade observations are prioritized from Hays County, nearby Central Texas, then Texas. '+
      'These are independently identified observations, not individually verified diagnostic lessons.</p></div>';
    if (record.loading) return intro+'<div class="loading" role="status">Searching individually licensed iNaturalist photos…</div>';
    if (record.error) return intro+'<p class="info" role="status">'+escapeHTML(record.error)+'</p>';
    if (!record.photos || !record.photos.length) {
      return intro+'<p class="info">No suitably licensed, matching Research Grade photos were found for this species in the searched Texas areas. '+
        'The existing canonical photo lesson remains available below.</p>';
    }
    return intro+cards(record.photos);
  }
  function sectionForClick(btn) {
    return btn.closest('[data-inat-species]');
  }
  function updateVisible(record) {
    const section = document.querySelector('[data-inat-species]');
    if (!section || section.dataset.inatSpecies !== record.name) return;
    const drawer = section.querySelector('[data-inat-drawer]');
    const btn = section.querySelector('[data-inat-open]');
    if (!drawer || !btn) return;
    drawer.hidden = !record.open;
    btn.setAttribute('aria-expanded', String(record.open));
    btn.textContent = record.open ? 'Hide iNaturalist Photos ↑' : 'Explore iNaturalist Photos ↓';
    if (record.open) drawer.innerHTML = body(record);
  }
  async function toggle(btn) {
    const section = sectionForClick(btn);
    if (!section) return;
    const name = section.dataset.inatSpecies;
    if (!name) return;
    let record = cache.get(name);
    if (!record) {
      record = {name, open:true, loading:true, photos:[], error:''};
      cache.set(name, record);
      updateVisible(record);
      try { record.photos = await load(name); }
      catch (err) { record.error = err && err.message ? err.message : 'Photo service unavailable.'; }
      record.loading = false;
      updateVisible(record);
    } else {
      record.open = !record.open;
      updateVisible(record);
    }
  }
  document.addEventListener('click', function(event) {
    const button = event.target.closest('[data-inat-open], [data-inat-scroll]');
    if (!button) return;
    if (button.hasAttribute('data-inat-open')) {
      toggle(button);
    } else {
      const strip = document.getElementById('inatPhotoStrip');
      if (strip) strip.scrollBy({left: Number(button.dataset.inatScroll) * Math.min(410, strip.clientWidth * 0.85), behavior:'smooth'});
    }
  });
  // The Learner may rerender when the cached genus/family notes arrive.
  // Restore an already opened gallery without repeating API requests.
  window.HaysINatGallery = {
    section: function(sp) {
      const name = sp && sp.scientific_name;
      if (!name) return '';
      const record = cache.get(name);
      let markup = header(name);
      markup = markup.replace('data-inat-open aria-expanded="false"',
        'data-inat-open aria-expanded="' + (record && record.open ? 'true' : 'false') + '"');
      if (record && record.open) {
        markup = markup.replace('data-inat-drawer hidden', 'data-inat-drawer')
          .replace('Explore iNaturalist Photos ↓', 'Hide iNaturalist Photos ↑')
          .replace('<div id="inatPhotoDrawer" data-inat-drawer></div>',
            '<div id="inatPhotoDrawer" data-inat-drawer>' + body(record) + '</div>');
      }
      return markup;
    }
  };
})();

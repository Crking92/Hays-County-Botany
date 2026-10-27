/* Hays Botany: source-verified giant reed / common reed / giant cutgrass quiz.
   Every displayed photograph is resolved from a published, individually credited
   species card, not guessed from a third-party result or invented taxon. */
(function(global){
'use strict';
const definitions=[
 {id:'reed1',source:'arundo-donax',panel:0,
  question:'Which species is documented in this whole-plant photograph?',
  options:['Giant reed — Arundo donax','Common reed — Phragmites australis','Giant cutgrass — Zizaniopsis miliacea','Johnsongrass — Sorghum halepense'],correct:0,
  feedback:['This source-labelled giant reed forms tall jointed canes with wide clasping leaves. Confirm with collar and flowers, not height alone.',
   'Common reed also makes tall stands; look for its spikelets and the location of silky hairs along the rachilla.',
   'Giant cutgrass is another coarse marsh grass, but it has a long papery ligule and sex-separated spikelets.',
   'Johnsongrass can grow tall, but it is not this photographed giant reed and has different leaf and flowering structures.'],
  explanation:'Use the wide leaves and robust jointed canes as a starting clue; the source identification is stronger than overall size.',
  study:'arundo-donax'},
 {id:'reed2',source:'phragmites-australis',panel:0,
  question:'Which plant is documented in this source-identified wetland photograph?',
  options:['Giant cutgrass — Zizaniopsis miliacea','Giant reed — Arundo donax','Common reed — Phragmites australis','Johnsongrass — Sorghum halepense'],correct:2,
  feedback:['Giant cutgrass has a different long-ligule and sex-separated spikelet pattern; the source photo is common reed.',
   'Giant reed can also have plumes, but its reproductive hair attachment and leaf-base details differ.',
   'The photographed plant is common reed. This confirms the species label, not whether the lineage is native or introduced.',
   'Johnsongrass is not the recorded identification and usually has a more open sorghum-type flowering head.'],
  explanation:'Species-level Phragmites recognition is the first step. Subspecies or invasive lineage identification is a separate task.',
  study:'phragmites-australis'},
 {id:'reed3',source:'zizaniopsis-miliacea',panel:1,
  question:'A tall marsh grass has broad finely saw-edged leaves, a long papery ligule, and separate male and female spikelets in one panicle. Which is the strongest candidate?',
  options:['Phragmites australis','Arundo donax','Sorghum halepense','Zizaniopsis miliacea'],correct:3,
  feedback:['Common reed has many-flowered spikelets with conspicuous silky rachilla hairs; those are not the described separate sex-spikelets.',
   'Giant reed forms multi-flowered spikelets with silky floret-associated hairs, not the described sex-separated units.',
   'Johnsongrass does not fit this combination of giant cutgrass leaf and sex-separated flowering characters.',
   'Giant cutgrass fits the stated leaf teeth, long membranous ligule and separate male/female spikelets. Inspect organs to confirm.'],
  explanation:'The photograph demonstrates plant habit; the question also supplies distinguishing anatomy that may not be visible in the photograph.',
  study:'zizaniopsis-miliacea'},
 {id:'reed4',source:'phragmites-australis',panel:1,
  question:'In the collar close-up, where should you look for the true ligule?',
  options:['Inside where the blade joins its wrapping leaf sheath','At the very tip of a mature flowering plume','At the base of an excavated rhizome','Between the upper and lower glumes of a spikelet'],correct:0,
  feedback:['The ligule is at the inner blade–sheath junction, often with a short membranous, hair-fringed edge.',
   'The plume contains flowering branches and spikelets, not the leaf-junction ligule.',
   'Rhizomes are underground spreading stems; the ligule belongs at a leaf blade–sheath junction.',
   'Glumes are reproductive bracts, not leaf-collar tissue.'],
  explanation:'Find the attached blade and peel back the sheath to inspect the true membrane; loose hairs alone are not a measured ligule.',
  study:'phragmites-australis'},
 {id:'reed5',source:'arundo-donax',panel:3,
  question:'Why is the hairy-looking ligule in this giant reed collar photograph NOT enough to identify the plant by itself?',
  options:['Because ligules are only found on underground stems','Because common reed can also have a hair-fringed ligule','Because giant reed has no leaf sheaths','Because ligules are reproductive parts of the spikelet'],correct:1,
  feedback:['A ligule is aboveground at a leaf blade–sheath junction, not restricted to underground stems.',
   'Both reed groups can show a membranous, hair-fringed ligule; use several characters together.',
   'Giant reed has wrapping leaf sheaths visible in this source image.',
   'The ligule is a leaf-collar feature, not a spikelet part.'],
  explanation:'A useful photograph can show a genuine structure without that structure being unique to one species.',
  study:'arundo-donax'},
 {id:'reed6',source:'phragmites-australis',panel:2,
  question:'Where are the prominent silky hairs mainly attached in common reed spikelets?',
  options:['Only to the outer surface of the culm','At the leaf-blade tip','Along the rachilla between florets','On the underground rhizome internodes'],correct:2,
  feedback:['The culm surface is not the spikelet axis carrying the prominent reproductive silk.',
   'Leaf tips are vegetative tissue, not the reproductive hair-bearing axis.',
   'Phragmites has conspicuous hairs on the rachilla, the axis between florets; this helps separate it from Arundo.',
   'Rhizomes are vegetative spreading stems, not the spikelet hair attachment.'],
  explanation:'The photo teaches reproductive parts. The rachilla hair position is useful at close magnification; avoid inferring a lineage from a single spikelet.',
  study:'phragmites-australis'},
 {id:'reed7',source:'arundo-donax',panel:9,
  question:'In a grass spikelet, what are the lower and upper glumes?',
  options:['The stem nodes supporting a leaf blade','The two basal bracts below the florets','The long hairs inside the hollow cane','The underground stems that produce shoots'],correct:1,
  feedback:['Nodes are stem structures; the glumes are part of the spikelet.',
   'Glumes are the paired lower bracts at the spikelet base, distinct from the lemmas of florets.',
   'Hairiness may help identification, but glumes are bracts and should not be defined by hair position.',
   'Rhizomes are underground stems; they are not spikelet glumes.'],
  explanation:'In a dissected spikelet, establish the attachment of each basal bract before measuring it. Do not mistake a long sterile-floret lemma for an upper glume.',
  study:'arundo-donax'},
 {id:'reed8',source:'phragmites-australis',panel:19,
  question:'This Gulf Coast source photograph clearly shows outer leaf sheaths. Which needed diagnostic measurement is NOT provided?',
  options:['The presence of attached green leaf blades','The fact that leaf sheaths wrap the culm','The visible position of several leaf attachments','An opened inner ligule measured with a millimeter scale'],correct:3,
  feedback:['Attached leaf blades are plainly visible in the source photo.',
   'The photograph visibly documents outer sheaths around the green culm.',
   'You can see where several blades and outer sheaths attach.',
   'The true inner ligule is not opened or measured, so no diagnostic length can be read from this image.'],
  explanation:'This is a research-grade Gulf Coast source identification, not independent genetic confirmation or a measured inner-ligule photograph.',
  study:'phragmites-australis'},
 {id:'reed9',source:'phragmites-australis',panel:15,
  question:'A North American reed has a reddish exposed mature culm. What can that clue safely tell you?',
  options:['It must be Eurasian introduced reed','It proves the Gulf Coast haplotype','It supports further native-lineage comparison but is not proof','It establishes that the plant is giant reed'],correct:2,
  feedback:['Red or purplish culms can occur in native-reed comparisons; color alone does not prove introduced lineage.',
   'Culm color cannot genetically identify a Gulf Coast haplotype.',
   'Reddish exposed mature culms can support the native americanus comparison, but other characters and provenance matter.',
   'An exposed reddish culm is not a unique giant reed identification.'],
  explanation:'The source photo is a North American native-reference example, with provenance limitations; do not classify a Texas stand from color alone.',
  study:'phragmites-australis'},
 {id:'reed10',source:'phragmites-australis',panel:18,
  question:'A Texas wetland plant is confidently Phragmites australis, but its native/Gulf/introduced lineage is unresolved. What is the responsible Field ID label?',
  options:['Invasive Eurasian reed, confirmed','Native americanus, confirmed','Gulf Coast berlandieri, confirmed','Phragmites australis — lineage unresolved'],correct:3,
  feedback:['A species ID does not establish which introduced or native lineage a Texas population belongs to.',
   'A native designation requires more than recognizing the species in a photograph.',
   'A Gulf Coast designation is not automatically established by a wetland habitat or a short ligule.',
   'Record the species while leaving lineage unresolved; additional characters, voucher work or genetic evidence may be needed for management decisions.'],
  explanation:'The photographed introduced-lineage herbarium collar is a teaching reference, not proof about an untested Texas stand.',
  study:'phragmites-australis'}
];
function build(cards){
 const questions=[];
 for(const d of definitions){
  const species=cards[d.source],panel=species?.visual_comparison?.items?.[d.panel];
  if(!species||!panel||typeof panel.image_url!=='string')continue;
  const root='content/taxa/'+species.family+'/'+species.genus+'/'+species.id+'/';
  // Only serve canonical, physically archived, rights-filtered photos.
  const media=(species.images||[]).find(im=>root+im.file===panel.image_url);
  if(!media||!media.creator||!media.license||!media.source_page)continue;
  const choices=d.options.map((label,i)=>({
   id:d.id+'-'+i,label,feedback:d.feedback[i]||''
  }));
  questions.push({
   id:d.id,mode:'reed',question:d.question,
   answer:choices[d.correct],choices,
   photo:{thumbnail:panel.image_url,thumbnail_creator:media.creator,
     thumbnail_license:media.license,thumbnail_source:media.source_page},
   explanation:d.explanation,study:d.study
  });
 }
 return questions;
}
global.HaysReedQuiz={build,requiredSpecies:['arundo-donax','phragmites-australis','zizaniopsis-miliacea'],definitions};
})(window);

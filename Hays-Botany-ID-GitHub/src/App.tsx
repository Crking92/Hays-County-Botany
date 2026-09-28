import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import {
  familyEvidence as evidenceRows,
  priorityFamilies as familyRows,
  sourceRegister as sourceRows,
  vocabulary as vocabularyRows,
} from "./botany-data.mjs";
import {
  familyCatalog as catalogRows,
  familyEvidenceCatalog as catalogEvidenceRows,
} from "./family-evidence-data.mjs";
import LearningPhoto from "./learning-photo";
import {
  type LearningVisual,
  visualForEvidence,
  visualForTerm,
  visualsForFamily,
} from "./learning-visuals";

const FamilyGuide = lazy(() => import("./family-guide"));

const assetPath = (path: string) =>
  `${import.meta.env.BASE_URL}${path.replace(/^\/+/, "")}`;

type Answer = "yes" | "no" | "unsure" | "hidden";
type Tab = "identify" | "families" | "glossary" | "photos" | "sources";

type Family = {
  order: number;
  family: string;
  commonName: string;
  recognition: string;
  coreSuite: string;
  fastestLook: string;
  confirmation: string;
  vegetative: string;
  exceptions: string;
  confusions: string;
  separation: string;
  localGenera: string;
  subdivisions: string;
  handLens: string;
  safety: string;
  apwebSource: string;
  regionalSource: string;
  confidence: string;
};

type Evidence = {
  family: string;
  code: string;
  organ: string;
  state: string;
  role: string;
  weight: number;
  reliability: string;
  visibility: string;
  season: string;
  statement: string;
  limits: string;
  separates: string;
};

type VocabularyTerm = {
  id: string;
  group: string;
  term: string;
  plain: string;
  fieldCue: string;
  synonyms: string;
  caution: string;
};

type SourceRow = [
  id: string,
  title: string,
  scope: string,
  author: string,
  url: string,
  date: string,
  note: string,
];

const families = familyRows as Family[];
const evidence = evidenceRows as Evidence[];
const vocabulary = vocabularyRows as VocabularyTerm[];
const sources = sourceRows as SourceRow[];
const familyCatalog = catalogRows as Array<{
  family: string;
  inventoryScope: string;
  evidenceCount: number;
}>;
const familyEvidenceCatalog = catalogEvidenceRows as Array<{
  family: string;
}>;

const evidenceBackedFamilies = familyCatalog.filter(
  (row) => row.evidenceCount > 0,
).length;
const currentEvidenceFamilies = familyCatalog.filter(
  (row) =>
    row.inventoryScope === "Current master inventory" &&
    row.evidenceCount > 0,
).length;
const referenceFamilies = familyCatalog.filter(
  (row) => row.inventoryScope === "Reference expansion",
).length;
const glossaryGroups = [
  "All terms",
  ...Array.from(new Set(vocabulary.map((row) => row.group))),
];

const familyMarks: Record<string, string> = {
  Asteraceae: "✺",
  Poaceae: "⌁",
  Fabaceae: "◒",
  Euphorbiaceae: "⬡",
  Lamiaceae: "✦",
  Cyperaceae: "△",
};

const photoTargets: Array<{
  family: string;
  targets: string[];
  note: string;
}> = [
  {
    family: "Asteraceae",
    targets: ["Whole plant", "Head · face", "Head · side", "Single floret", "Anther tube", "Cypsela", "Pappus", "Receptacle"],
    note: "Prove that the apparent flower is a community of florets.",
  },
  {
    family: "Poaceae",
    targets: ["Whole plant", "Leaf sheath", "Ligule", "Culm node", "Spikelet", "Glumes", "Lemma + palea", "Caryopsis"],
    note: "Photograph the spikelet as a construction, not just the plume.",
  },
  {
    family: "Fabaceae",
    targets: ["Whole plant", "Complete leaf", "Stipules", "Pulvinus", "Flower", "Single carpel", "Legume", "Seed row"],
    note: "Connect the jointed leaf and one-carpel fruit to the same plant.",
  },
  {
    family: "Euphorbiaceae",
    targets: ["Whole plant", "Unisexual flowers", "Three-lobed ovary", "Three-coccus fruit", "Central column", "Cyathium", "Hair type", "Existing sap"],
    note: "Use the ovary and fruit; never damage a plant merely to test latex.",
  },
  {
    family: "Lamiaceae",
    targets: ["Whole plant", "Opposite leaves", "Stem section", "Corolla", "Stamens", "Four-lobed ovary", "Gynobasic style", "Nutlets"],
    note: "Move beyond square stems and confirm the ovary–fruit construction.",
  },
  {
    family: "Cyperaceae",
    targets: ["Whole plant", "Culm section", "Closed sheath", "Leaf ranks", "Spikelet", "Achene", "Style branches", "Perigynium"],
    note: "The flower and achene settle cases where the triangular-stem rule fails.",
  },
];

type DiagnosticPhoto = {
  family: string;
  organ: string;
  title: string;
  imageUrl: string;
  sourceUrl: string;
  source: string;
  specimen: string;
  imageKey: string[];
  lookFor: string;
  proves: string;
  caution: string;
};

const diagnosticPhotos: DiagnosticPhoto[] = [
  {
    family: "Asteraceae",
    organ: "Flower head",
    title: "Many flowers hiding inside one ‘flower’",
    imageUrl: "https://images.floristics.info/images/stati_photo2/sunflower/sunflower5e.jpg",
    sourceUrl: "https://floristics.info/ru/stati/ogorod/3378-podsolnechnik-vyrashchivanie-iz-semyan-posadka-v-otkrytyj-grunt-i-ukhod.html",
    source: "Floristics.info",
    specimen: "Helianthus annuus",
    imageKey: ["center · disc florets", "outer rim · ray florets"],
    lookFor: "Each tiny five-pointed tube in the center is one disc floret. The large yellow structures at the edge are ray florets—not petals of one flower.",
    proves: "A composite head, the first strong Asteraceae clue.",
    caution: "A front view does not show the involucre or each floret’s ovary. Add a side view and a removed floret.",
  },
  {
    family: "Asteraceae",
    organ: "Receptacle + fruit",
    title: "Follow one floret down to its own fruit",
    imageUrl: "https://backyardnature.net/n/13/130728sg.jpg",
    sourceUrl: "https://backyardnature.net/n/h/sunflowr.htm",
    source: "Backyard Nature",
    specimen: "Helianthus annuus",
    imageKey: ["pale cups · developing cypselas", "dark gaps · empty floret scars"],
    lookFor: "Empty floret scars repeat across one shared receptacle. Each remaining corolla sits above its own developing cypsela.",
    proves: "The head is a community of flowers, each producing one dry fruit.",
    caution: "The chaffy bracts between florets are not present in every aster head.",
  },
  {
    family: "Asteraceae",
    organ: "Cypsela + pappus",
    title: "The parachute belongs to the fruit",
    imageUrl: "https://idtools.org/seed_families/images/Erigeron%20canadensis_fr_imageID_244031.jpg",
    sourceUrl: "https://idtools.org/seed_families/index.cfm?entityID=57731&packageID=2246",
    source: "USDA IDTools",
    specimen: "Erigeron canadensis",
    imageKey: ["left · cypsela", "right · pappus bristles"],
    lookFor: "The narrow brown body is the one-seeded cypsela; the fine white bristles at its tip are the pappus.",
    proves: "A pappus-bearing cypsela strongly supports Asteraceae when traced back to a head.",
    caution: "Pappus form varies from bristles to scales, awns, a short crown, or nothing visible.",
  },
  {
    family: "Poaceae",
    organ: "Leaf junction",
    title: "Open the collar zone—not the flower plume",
    imageUrl: "https://www.minnesotawildflowers.info/udata/r9ndp23q/pd3/muhlenbergia-schreberi-s6.jpg",
    sourceUrl: "https://www.minnesotawildflowers.info/grass-sedge-rush/nimblewill",
    source: "Minnesota Wildflowers",
    specimen: "Muhlenbergia schreberi",
    imageKey: ["junction · hairy ligule", "below · leaf sheath", "right · culm node"],
    lookFor: "Trace the blade downward. The ligule sits exactly where the blade leaves the sheath; the sheath wraps the round culm below the collar.",
    proves: "A grass-style leaf unit and the best place to collect vegetative ID characters.",
    caution: "Ligules may be membranes, hairs, or a mixture. Their shape helps with species ID but no single form defines all grasses.",
  },
  {
    family: "Poaceae",
    organ: "Spikelet",
    title: "Take the spikelet apart in layers",
    imageUrl: "https://www.minnesotawildflowers.info/udata/r9ndp23q/grass/poa-nemoralis-072319-s2.jpg",
    sourceUrl: "https://www.minnesotawildflowers.info/grass-sedge-rush/wood-bluegrass",
    source: "Minnesota Wildflowers",
    specimen: "Poa nemoralis",
    imageKey: ["far left · glumes", "middle · lemma + palea", "far right · grain"],
    lookFor: "The two basal glumes sit outside the florets. Within each floret, the lemma faces outward and the palea sits against the axis.",
    proves: "Glumes plus lemma-and-palea florets confirm the grass construction.",
    caution: "These parts are only millimeters long. Use a hand lens, mature material, and a scale.",
  },
  {
    family: "Poaceae",
    organ: "Culm + sheath",
    title: "Find the solid node on the jointed culm",
    imageUrl: "https://minnesotawildflowers.info/udata/r9ndp23q/pd3/digitaria-ischaemum-853408-9.jpg",
    sourceUrl: "https://www.minnesotawildflowers.info/grass-sedge-rush/smooth-crabgrass",
    source: "Minnesota Wildflowers",
    specimen: "Digitaria ischaemum",
    imageKey: ["center · swollen node", "above · ligule", "below · open sheath"],
    lookFor: "The node is the swollen joint on the culm. Above it, the blade departs from a sheath with overlapping—not fully fused—margins.",
    proves: "The combined node, open sheath, and ligule suite supports Poaceae.",
    caution: "Some grasses have partly closed sheaths or solid internodes, so confirm with a spikelet when possible.",
  },
  {
    family: "Fabaceae",
    organ: "Leaf base",
    title: "A swollen joint plus a stipule",
    imageUrl: "https://botanycompanion.wordpress.com/wp-content/uploads/2015/03/pulvinus-on-desmodium-1-cropped-and-labeled.jpg?w=600",
    sourceUrl: "https://botanycompanion.wordpress.com/lesson-13-dicots/",
    source: "Botany Companion",
    specimen: "Desmodium sp.",
    imageKey: ["left base · pulvinus", "right flap · stipule"],
    lookFor: "The pulvinus is the swollen, flexible joint at the petiole base. The stipule is a separate leaf-like appendage beside that attachment.",
    proves: "Pulvini plus stipules strongly support Fabaceae when paired with a legume fruit.",
    caution: "Neither feature is exclusive to legumes, and both can be tiny or shed early.",
  },
  {
    family: "Fabaceae",
    organ: "Legume fruit",
    title: "One carpel, two seams, one seed row",
    imageUrl: "https://www.acguanacaste.ac.cr/paginas_especie/magnoliophyta/fabaceae/calliandra_callothyrsus/c_callothyrsus24feb98/calliandra_callothyrsus_2700/98-ACG-PI-d-978_g.jpg",
    sourceUrl: "https://www.acguanacaste.ac.cr/paginas_especie/magnoliophyta/fabaceae/calliandra_callothyrsus/c_callothyrsus24feb98/c_callothyrsus24feb98.html",
    source: "Área de Conservación Guanacaste",
    specimen: "Calliandra callothyrsus",
    imageKey: ["outer walls · two valves", "inside edge · one seed row"],
    lookFor: "The opened fruit has two valves and a single line of seeds along the folded carpel margin.",
    proves: "A true legume formed from one carpel—the most dependable family character.",
    caution: "Some legumes stay closed, split into segments, coil, or become fleshy. An elongated capsule is not automatically a pod.",
  },
  {
    family: "Fabaceae",
    organ: "Whole leaf",
    title: "Photograph the complete jointed leaf",
    imageUrl: "https://botweb.uwsp.edu/anatomy/images/leafmorphology/images_c/anat1111.jpg",
    sourceUrl: "https://botweb.uwsp.edu/anatomy/images/leafmorphology/pages_c/anat1111new.htm",
    source: "University of Wisconsin–Stevens Point",
    specimen: "Fabaceae example",
    imageKey: ["center axis · rachis", "side blades · leaflets", "stem end · stipules"],
    lookFor: "The entire compound leaf runs from the stem node through one petiole and rachis to several leaflets. Small stipules sit beside its stem attachment.",
    proves: "The photograph documents leaf architecture; a single leaflet could otherwise be mistaken for a simple leaf.",
    caution: "Compound leaves occur in many families. Confirm Fabaceae with pulvini, a one-carpel flower, or a true legume.",
  },
  {
    family: "Euphorbiaceae",
    organ: "Cyathium",
    title: "A flower-like cup made of smaller flowers",
    imageUrl: "https://www.life.illinois.edu/help/digitalflowers/picts/Euphorbiaceae/14-Euphorbia%20milii%20cyathium.jpg",
    sourceUrl: "https://www.life.illinois.edu/help/digitalflowers/Euphorbiaceae/14.htm",
    source: "University of Illinois Digital Flowers",
    specimen: "Euphorbia milii",
    imageKey: ["center stalk · female flower", "orange knobs · male flowers", "rim · nectar gland"],
    lookFor: "One stalked female flower rises from the center; several male flowers, each reduced to one stamen, stand inside the gland-bearing cup.",
    proves: "A cyathium confirms Euphorbia and close relatives—not the whole spurge family.",
    caution: "The showy red structures in crown-of-thorns are bracts. Do not treat every colorful part as a petal.",
  },
  {
    family: "Euphorbiaceae",
    organ: "Ovary + styles",
    title: "Count three ovary compartments and split styles",
    imageUrl: "https://fleursauvageyonne.github.io/imag01/euphorbia_amygdaloides5.jpg",
    sourceUrl: "https://fleursauvageyonne.github.io/flsv/vert/euphorbia_amygdaloides.htm",
    source: "Flore Sauvage de l’Yonne",
    specimen: "Euphorbia amygdaloides",
    imageKey: ["center · three-part ovary", "top · forked styles", "left · nectar glands"],
    lookFor: "The central female flower shows a three-part ovary. Above it, three styles divide into paired stigma branches.",
    proves: "The three-carpel construction expected before the fruit divides into three cocci.",
    caution: "Tiny male flowers and nectar glands surround it. Use a lens and avoid irritating sap.",
  },
  {
    family: "Euphorbiaceae",
    organ: "Seed caruncle",
    title: "Inspect the seed’s attachment end",
    imageUrl: "https://www.atlasdesemillasdecanarias.org/fotos/ID_28-2020_03_11-uxgdzzBhtB_lg.jpg",
    sourceUrl: "https://www.atlasdesemillasdecanarias.org/atlas/ficha.php?ID=28",
    source: "Canary Islands Digital Seed Atlas",
    specimen: "Euphorbia serrata",
    imageKey: ["gray body · seed coat", "pale knob · caruncle"],
    lookFor: "The pale knob at one end is a caruncle; the gray seed coat shows a fine sculptured surface under magnification.",
    proves: "A carunculate seed supports Euphorbiaceae and can be diagnostic within local genera.",
    caution: "Caruncles are common, not universal. Never use seed appearance by itself for a family identification.",
  },
  {
    family: "Lamiaceae",
    organ: "Stem + leaves",
    title: "Pair the square stem with opposite leaves",
    imageUrl: "https://storage.googleapis.com/powop-assets/PPA/1400_1424/h1405s_fullsize.jpg",
    sourceUrl: "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:30000097-2/general-information",
    source: "Kew Plants of the World Online",
    specimen: "Lamiaceae example",
    imageKey: ["paired blades · opposite leaves", "center axis · four-angled stem"],
    lookFor: "Leaves occur in opposite pairs at the same node and successive pairs turn ninety degrees. Long ridges make the young stem four-angled.",
    proves: "A familiar mint-family vegetative suite worth testing with flower or fruit.",
    caution: "Many unrelated plants have square stems or opposite leaves. Neither trait proves Lamiaceae alone.",
  },
  {
    family: "Lamiaceae",
    organ: "Corolla + stigma",
    title: "Read the two-lipped flower from the side",
    imageUrl: "https://acorral.es/malpiweb/florayfauna/floryfauima/Salviaverbenaca21c.jpg",
    sourceUrl: "https://acorral.es/malpiweb/florayfauna/salvia.html",
    source: "Flora de Malpica de Tajo",
    specimen: "Salvia pratensis",
    imageKey: ["top hood · upper lip", "lower platform · lower lip", "projecting tips · anther + stigma"],
    lookFor: "The fused corolla forms an upper and lower lip. The two anthers and forked stigma project where a visiting insect contacts them.",
    proves: "Bilabiate corolla plus reduced stamen number supports Salvia within Lamiaceae.",
    caution: "Flower shape and stamen number vary across the family; this is not a universal mint flower.",
  },
  {
    family: "Lamiaceae",
    organ: "Four nutlets",
    title: "Look inside the persistent calyx after flowering",
    imageUrl: "https://missouriplants.com/images/Stachys_pilosa_fruits.jpg",
    sourceUrl: "https://missouriplants.com/Stachys_pilosa_page.html",
    source: "Missouri Plants",
    specimen: "Stachys pilosa",
    imageKey: ["dark center · four nutlets", "green points · persistent calyx teeth"],
    lookFor: "Four separate dark nutlets sit in the base of the five-toothed calyx where the corolla used to be.",
    proves: "The four-lobed ovary has matured into four one-seeded nutlets—a strong mint-family confirmation.",
    caution: "Some Lamiaceae produce fewer nutlets, and woody lineages such as Callicarpa have fleshy fruits.",
  },
  {
    family: "Cyperaceae",
    organ: "Culm + sheath",
    title: "Trace the leaf into a closed sheath",
    imageUrl: "https://newfs.s3.amazonaws.com/taxon-images-1000s1000/Cyperaceae/scirpus-cyperinus-ss-atal.jpg",
    sourceUrl: "https://gobotany.nativeplanttrust.org/species/scirpus/cyperinus/",
    source: "Native Plant Trust Go Botany",
    specimen: "Scirpus cyperinus",
    imageKey: ["upper blade · leaf", "brown-edged tube · closed sheath", "lower axis · culm"],
    lookFor: "The sheath forms a continuous tube around a solid, angled culm instead of two overlapping margins.",
    proves: "Closed sheath plus a solid, often angled culm strongly supports a sedge.",
    caution: "Some sedges have round culms, and a photograph cannot prove that the culm is solid. Pair this with fruit.",
  },
  {
    family: "Cyperaceae",
    organ: "Perigynium + achene",
    title: "Open the little sac around a Carex fruit",
    imageUrl: "https://www.minnesotawildflowers.info/udata/r9ndp23q/grass/carex-bicknellii-062218-s6.jpg",
    sourceUrl: "https://www.minnesotawildflowers.info/grass-sedge-rush/bicknells-sedge",
    source: "Minnesota Wildflowers",
    specimen: "Carex bicknellii",
    imageKey: ["large veined sacs · perigynia", "right brown body · achene", "narrow flap · scale"],
    lookFor: "The perigynium is the veined sac; the smooth, hard body removed from it is the one-seeded achene. A separate scale subtends the unit.",
    proves: "A perigynium identifies Carex and close segregates within Cyperaceae.",
    caution: "Perigynia do not occur across the whole sedge family. Use this feature only for the Carex group.",
  },
  {
    family: "Cyperaceae",
    organ: "Fruiting spike",
    title: "Connect the macro part back to the plant",
    imageUrl: "https://www.sedgesofmarin.org/images/template4.jpg",
    sourceUrl: "https://www.sedgesofmarin.org/how-to.html",
    source: "Sedges of Marin",
    specimen: "Carex morphology guide",
    imageKey: ["a · fruiting spike", "b–d · perigynium views", "e · enclosed achene"],
    lookFor: "The overview links staminate and pistillate spikes to a single perigynium, then to the achene hidden inside it.",
    proves: "The same-plant series preserves where the diagnostic fruit came from.",
    caution: "Spike arrangement differs widely among Carex species; do not copy this one arrangement onto every sedge.",
  },
];

type ArchiveCandidate = {
  family: string;
  specimen: string;
  structure: string;
  visible: string;
  limit: string;
  imageUrl: string;
  imageAlt: string;
  sourceUrl: string;
};

const utArchiveCandidates: ArchiveCandidate[] = [
  {
    family: "Asteraceae",
    specimen: "Tetragonotheca texana",
    structure: "Phyllaries + square involucre",
    visible: "Four broad phyllaries meet around the unopened head, making the square outline unusually clear.",
    limit: "This is a genus-level example, not the normal involucre shape for every aster.",
    imageUrl: assetPath("images/ut-study/tetragonotheca-phyllaries.jpg"),
    imageAlt: "Close view of a square unopened Tetragonotheca texana flower head formed by four green phyllaries.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/ast/tetragonotheca_texana.htm",
  },
  {
    family: "Asteraceae",
    specimen: "Brickellia cylindracea",
    structure: "Fruiting heads + pappus",
    visible: "White pappus bristles flare from several mature heads while unopened and spent heads remain on the same branch.",
    limit: "The individual dry fruit is not isolated clearly enough to study achene shape.",
    imageUrl: assetPath("images/ut-study/brickellia-fruiting-heads.jpg"),
    imageAlt: "Brickellia cylindracea branch with narrow flower heads and white pappus bristles emerging from mature heads.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/ast/brickellia_cylindracea.htm",
  },
  {
    family: "Poaceae",
    specimen: "Arundo donax",
    structure: "Node + open sheath",
    visible: "A swollen culm node sits below the leaf collar; the sheath margins meet as a visible seam instead of a fused tube.",
    limit: "Use the seam as a grass clue, then confirm the plant with a spikelet.",
    imageUrl: assetPath("images/ut-study/arundo-node-open-sheath.jpg"),
    imageAlt: "Arundo donax culm node and overlapping open leaf sheath viewed close up.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/poa/arundo_donax.htm",
  },
  {
    family: "Poaceae",
    specimen: "Bothriochloa laguroides",
    structure: "Awned spikelets",
    visible: "Long slender awns project beyond the silky spikelet clusters at the tip of the flowering branch.",
    limit: "The lemma attachment is described on the source page but is not resolved sharply enough to trace in this frame.",
    imageUrl: assetPath("images/ut-study/bothriochloa-awns.jpg"),
    imageAlt: "Silky Bothriochloa laguroides spikelet cluster with several long slender awns extending beyond it.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/poa/bothriochloa_laguroides.htm",
  },
  {
    family: "Fabaceae",
    specimen: "Medicago polymorpha",
    structure: "Incised stipules",
    visible: "Toothed, leaf-like stipules clasp the stem at the base of each petiole below the three leaflets.",
    limit: "Do not mistake the stipules for another leaflet; trace the full petiole back to the stem node.",
    imageUrl: assetPath("images/ut-study/medicago-stipules.jpg"),
    imageAlt: "Medicago polymorpha stem showing trifoliate leaves and incised stipules at the petiole bases.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/fab/medicago_polymorpha.htm",
  },
  {
    family: "Fabaceae",
    specimen: "Chamaecrista fasciculata",
    structure: "Legume + seed row",
    visible: "Seed bulges form one line along the flat, single-carpel legume while the fruit remains attached to the leafy stem.",
    limit: "The pod is closed, so the two valves and their sutures are inferred from form rather than exposed.",
    imageUrl: assetPath("images/ut-study/chamaecrista-legume.jpg"),
    imageAlt: "Attached Chamaecrista fasciculata legume with a single visible row of seed bulges.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/fab/chamaecrista_fasciculata.htm",
  },
  {
    family: "Euphorbiaceae",
    specimen: "Euphorbia bicolor",
    structure: "Cyathium + pendulous ovary",
    visible: "Each three-lobed ovary hangs on a stalk below a cup-like cyathium with white nectar-gland appendages.",
    limit: "The reduced male flowers inside the cup are too small to count in this image.",
    imageUrl: assetPath("images/ut-study/euphorbia-bicolor-cyathia.jpg"),
    imageAlt: "Two Euphorbia bicolor cyathia with pendulous three-lobed green ovaries and white gland appendages.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/eup/euphorbia_bicolor.htm",
  },
  {
    family: "Euphorbiaceae",
    specimen: "Croton fruticulosus",
    structure: "Developing three-part fruit",
    visible: "The young fruit is visibly divided into three rounded sections, with old style and stigma tissue above it.",
    limit: "The six stigma branches mentioned by the source are not individually countable in this frame.",
    imageUrl: assetPath("images/ut-study/croton-fruit-stigmas.jpg"),
    imageAlt: "Developing three-lobed fruit of Croton fruticulosus among hairy green leaves.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/eup/croton_fruticulosus.htm",
  },
  {
    family: "Lamiaceae",
    specimen: "Monarda citriodora",
    structure: "Bilabiate corolla + stigma",
    visible: "The fused pink corolla opens into an upper hood and a broad lower lip; a slender pale style projects beyond it.",
    limit: "The two stigma lobes are small and partly lost against the background—use magnification before counting them.",
    imageUrl: assetPath("images/ut-study/monarda-bilabiate-corolla.jpg"),
    imageAlt: "Close view of Monarda citriodora flowers showing pink two-lipped corollas and projecting styles.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/lam/monarda_citriodora.htm",
  },
  {
    family: "Lamiaceae",
    specimen: "Trichostema dichotomum",
    structure: "Bilabiate flower + calyx context",
    visible: "One strongly two-lipped flower sits beside green five-toothed calyces that remain after the corolla falls.",
    limit: "The source text says the retained calyx surrounds four nutlets, but this photograph does not reveal or prove those nutlets.",
    imageUrl: assetPath("images/ut-study/trichostema-flower-calyx.jpg"),
    imageAlt: "Trichostema dichotomum flower with one broad lower lip, four upper lobes, and nearby green calyces.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/lam/trichostema_dichotomum.htm",
  },
  {
    family: "Cyperaceae",
    specimen: "Cyperus odoratus",
    structure: "Triangular culm",
    visible: "Several culm faces meet along distinct longitudinal edges directly below the inflorescence.",
    limit: "Perspective can exaggerate an edge; rotate a live stem or view a safe cross-section before calling it triangular.",
    imageUrl: assetPath("images/ut-study/cyperus-triangular-culm.jpg"),
    imageAlt: "Cyperus odoratus culm below the inflorescence with distinct angular edges visible.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/cyp/cyperus_odoratus.htm",
  },
  {
    family: "Cyperaceae",
    specimen: "Cyperus odoratus",
    structure: "Spikelet clusters",
    visible: "Many flattened spikelets radiate in dense branch-end clusters above long leaf-like bracts.",
    limit: "The individual scales and their two-ranked attachment to the rachis are not sharp enough to verify in this overview.",
    imageUrl: assetPath("images/ut-study/cyperus-spikelets.jpg"),
    imageAlt: "Cyperus odoratus inflorescence with dense clusters of flattened green spikelets.",
    sourceUrl: "https://web.biosci.utexas.edu/bio406d/images/pics/cyp/cyperus_odoratus.htm",
  },
];

type VisualMetadata = {
  botanicalTerm: string;
  plainLabel: string;
  codes: string[];
  terms: string[];
};

const utVisualMetadata: Record<string, VisualMetadata> = {
  "Asteraceae|Phyllaries + square involucre": {
    botanicalTerm: "Phyllaries · involucre",
    plainLabel: "the green bracts cupping the flower head",
    codes: ["AST-INVOLUCRE"],
    terms: ["phyllary", "involucre"],
  },
  "Asteraceae|Fruiting heads + pappus": {
    botanicalTerm: "Pappus",
    plainLabel: "the bristles attached to the top of each dry fruit",
    codes: ["AST-PAPPUS", "AST-CYPSELA"],
    terms: ["pappus", "fruiting head"],
  },
  "Poaceae|Node + open sheath": {
    botanicalTerm: "Culm node · open sheath",
    plainLabel: "the joint and overlapping leaf-base seam",
    codes: ["POA-NODES", "POA-SHEATH", "POA-CULM"],
    terms: ["culm", "node", "open sheath", "sheathing"],
  },
  "Poaceae|Awned spikelets": {
    botanicalTerm: "Spikelet · awn",
    plainLabel: "the repeated flowering units and their long bristles",
    codes: [],
    terms: ["spikelet", "awn"],
  },
  "Fabaceae|Incised stipules": {
    botanicalTerm: "Trifoliolate leaf · stipules",
    plainLabel: "three leaflets and the paired appendages at the petiole base",
    codes: ["FAB-STIPULE"],
    terms: ["stipule", "trifoliolate", "compound leaf", "petiole"],
  },
  "Fabaceae|Legume + seed row": {
    botanicalTerm: "Legume · one seed row",
    plainLabel: "the single-carpel pod attached to the stem",
    codes: ["FAB-LEGUME", "FAB-ONECARPEL", "FAB-SEEDROW"],
    terms: ["legume", "one carpel", "superior carpel", "seed row"],
  },
  "Euphorbiaceae|Cyathium + pendulous ovary": {
    botanicalTerm: "Cyathium · three-lobed ovary",
    plainLabel: "the tiny flower-like cup above the hanging ovary",
    codes: ["EUP-CYATH", "EUP-THREE", "EUP-UNISEX"],
    terms: ["cyathium", "three fused carpels", "three-lobed ovary", "unisexual"],
  },
  "Euphorbiaceae|Developing three-part fruit": {
    botanicalTerm: "Three-part schizocarp",
    plainLabel: "the three rounded fruit sections below the old styles",
    codes: ["EUP-SCHIZO", "EUP-COLUMN"],
    terms: ["schizocarp", "three-coccus", "three-part fruit", "style branch", "carpel"],
  },
  "Lamiaceae|Bilabiate corolla + stigma": {
    botanicalTerm: "Bilabiate corolla",
    plainLabel: "the fused upper hood and broad lower lip",
    codes: ["LAM-COROLLA", "LAM-STAMEN"],
    terms: ["bilabiate", "zygomorphic", "sympetalous", "corolla"],
  },
  "Lamiaceae|Bilabiate flower + calyx context": {
    botanicalTerm: "Bilabiate flower · persistent calyx",
    plainLabel: "the two-lipped flower and the green cup left behind",
    codes: [],
    terms: ["bilabiate", "zygomorphic", "calyx", "persistent calyx"],
  },
  "Cyperaceae|Triangular culm": {
    botanicalTerm: "Three-angled culm",
    plainLabel: "the longitudinal corners on the flowering stem",
    codes: ["CYP-ANGLED"],
    terms: ["angled", "triangular culm", "culm"],
  },
  "Cyperaceae|Spikelet clusters": {
    botanicalTerm: "Spikelets",
    plainLabel: "the repeated flattened flowering units",
    codes: ["CYP-SPIKELET"],
    terms: ["spikelet", "inflorescence", "scale", "bract"],
  },
};

const atlasVisualMetadata: Record<string, VisualMetadata> = {
  "Asteraceae|Flower head": {
    botanicalTerm: "Capitulum · ray and disc florets",
    plainLabel: "many small flowers acting like one flower",
    codes: ["AST-HEAD", "AST-RAYDISC", "AST-SYNANTH"],
    terms: ["capitulum", "flower head", "ray floret", "disc floret"],
  },
  "Asteraceae|Receptacle + fruit": {
    botanicalTerm: "Receptacle · cypselas",
    plainLabel: "the shared platform and each floret’s developing fruit",
    codes: ["AST-RECEPT", "AST-OVARY"],
    terms: ["receptacle", "inferior ovary", "floret"],
  },
  "Asteraceae|Cypsela + pappus": {
    botanicalTerm: "Cypsela · pappus",
    plainLabel: "the dry fruit body and bristles at its tip",
    codes: ["AST-CYPSELA", "AST-PAPPUS"],
    terms: ["cypsela", "pappus"],
  },
  "Poaceae|Leaf junction": {
    botanicalTerm: "Ligule · sheath-blade junction",
    plainLabel: "the membrane or hair fringe where blade meets sheath",
    codes: ["POA-LIGULE"],
    terms: ["ligule", "sheath-blade junction", "leaf junction", "sheathing"],
  },
  "Poaceae|Spikelet": {
    botanicalTerm: "Glumes · lemma · palea",
    plainLabel: "the nested bracts of one grass spikelet",
    codes: ["POA-SPIKELET", "POA-GLUMES", "POA-LEMMA", "POA-CARYOPSIS"],
    terms: ["spikelet", "glume", "lemma", "palea", "caryopsis"],
  },
  "Poaceae|Culm + sheath": {
    botanicalTerm: "Culm node · open sheath",
    plainLabel: "the solid joint and overlapping sheath margins",
    codes: ["POA-CULM", "POA-NODES", "POA-SHEATH"],
    terms: ["culm", "node", "open sheath", "sheathing"],
  },
  "Fabaceae|Leaf base": {
    botanicalTerm: "Pulvinus · stipule",
    plainLabel: "the swollen leaf joint and nearby appendage",
    codes: ["FAB-PULVINUS", "FAB-STIPULE"],
    terms: ["pulvinus", "stipule", "petiole"],
  },
  "Fabaceae|Legume fruit": {
    botanicalTerm: "Legume · one carpel",
    plainLabel: "two valves opening around one line of seeds",
    codes: ["FAB-LEGUME", "FAB-ONECARPEL", "FAB-SEEDROW"],
    terms: ["legume", "one carpel", "seed row"],
  },
  "Fabaceae|Whole leaf": {
    botanicalTerm: "Compound leaf · rachis",
    plainLabel: "one complete leaf divided into several leaflets",
    codes: ["FAB-COMPOUND"],
    terms: ["compound", "pinnately compound", "rachis", "leaflet"],
  },
  "Euphorbiaceae|Cyathium": {
    botanicalTerm: "Cyathium",
    plainLabel: "one cup holding several extremely reduced flowers",
    codes: ["EUP-CYATH", "EUP-UNISEX"],
    terms: ["cyathium", "unisexual", "staminate", "pistillate"],
  },
  "Euphorbiaceae|Ovary + styles": {
    botanicalTerm: "Three-carpellate ovary",
    plainLabel: "three ovary sections topped by split styles",
    codes: ["EUP-THREE"],
    terms: ["three fused carpels", "superior ovary", "style branch"],
  },
  "Euphorbiaceae|Seed caruncle": {
    botanicalTerm: "Caruncle",
    plainLabel: "the small appendage at the seed’s attachment end",
    codes: ["EUP-CARUNCLE"],
    terms: ["caruncle", "micropyle", "seed appendage"],
  },
  "Lamiaceae|Stem + leaves": {
    botanicalTerm: "Opposite leaves · four-angled stem",
    plainLabel: "paired leaves on the ridged young stem",
    codes: ["LAM-OPPOSITE", "LAM-SQUARE", "LAM-EXSTIP"],
    terms: ["opposite", "decussate", "four-angled", "square"],
  },
  "Lamiaceae|Corolla + stigma": {
    botanicalTerm: "Bilabiate corolla",
    plainLabel: "a fused flower tube divided into upper and lower lips",
    codes: ["LAM-COROLLA", "LAM-STAMEN"],
    terms: ["bilabiate", "zygomorphic", "sympetalous"],
  },
  "Lamiaceae|Four nutlets": {
    botanicalTerm: "Four nutlets · persistent calyx",
    plainLabel: "the four hard units left inside the green calyx",
    codes: ["LAM-NUTLETS"],
    terms: ["nutlet", "persistent calyx"],
  },
  "Cyperaceae|Culm + sheath": {
    botanicalTerm: "Closed sheath · angled culm",
    plainLabel: "a fused leaf-base tube around the flowering stem",
    codes: ["CYP-CLOSED", "CYP-RANKS"],
    terms: ["closed sheath", "angled", "culm", "sheathing"],
  },
  "Cyperaceae|Perigynium + achene": {
    botanicalTerm: "Perigynium · achene",
    plainLabel: "the sac-like bract and the dry fruit hidden inside",
    codes: ["CYP-PERIG", "CYP-ACHENE"],
    terms: ["perigynium", "achene"],
  },
  "Cyperaceae|Fruiting spike": {
    botanicalTerm: "Fruiting spike · perigynium",
    plainLabel: "the whole spike traced down to one enclosed fruit",
    codes: [],
    terms: ["fruiting spike", "perigynium", "achene", "spikelet"],
  },
};

const visualId = (prefix: string, family: string, label: string) =>
  `${prefix}-${family}-${label}`
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const learningVisuals: LearningVisual[] = [
  ...utArchiveCandidates.map((candidate) => {
    const metadata = utVisualMetadata[`${candidate.family}|${candidate.structure}`];
    return {
      id: visualId("ut", candidate.family, candidate.structure),
      family: candidate.family,
      botanicalTerm: metadata.botanicalTerm,
      plainLabel: metadata.plainLabel,
      imageUrl: candidate.imageUrl,
      imageAlt: candidate.imageAlt,
      sourceUrl: candidate.sourceUrl,
      source: "UT Austin BIO 406D",
      specimen: candidate.specimen,
      lookFor: candidate.visible,
      limit: candidate.limit,
      rights: "private-study" as const,
      codes: metadata.codes,
      terms: metadata.terms,
    };
  }),
  ...diagnosticPhotos.map((photo) => {
    const metadata = atlasVisualMetadata[`${photo.family}|${photo.organ}`];
    return {
      id: visualId("atlas", photo.family, photo.organ),
      family: photo.family,
      botanicalTerm: metadata.botanicalTerm,
      plainLabel: metadata.plainLabel,
      imageUrl: photo.imageUrl,
      imageAlt: `${photo.title}. ${photo.imageKey.join("; ")}.`,
      sourceUrl: photo.sourceUrl,
      source: photo.source,
      specimen: photo.specimen,
      lookFor: photo.lookFor,
      limit: photo.caution,
      rights: "source-linked" as const,
      codes: metadata.codes,
      terms: metadata.terms,
    };
  }),
];

const delegationPrompt = `You are researching botanical identification data and real, diagnostic plant photographs for Hays Botany ID, a family → genus → species field guide for Hays County, Texas.

INPUTS
I will attach Hays_County_Botany_Master_List.xlsx and Hays_Botany_Image_Registry.xlsx, downloaded from the site's Sources and Photos tabs. Read their sheet names, headers, existing records, Photo Shot List, License Policy, and Controlled Lists before collecting anything. If an attachment is missing, ask me for it. Preserve Record IDs, submitted names, existing evidence, and original files.

BONAP FIRST PASS
Open https://bonap.net/tdc, select Texas and Hays County, and inspect its family, genus, and species descriptions, selected characters, biological attributes, and photo gallery for the assigned taxa. Cite the relevant BONAP result or taxon page and access date for every fact used; paraphrase its descriptions. The BONAP county/ZIP key explicitly includes the selected county plus adjacent counties. Label that result "Hays + adjacent county candidate" until a separate record establishes Hays occurrence. Preserve any disagreement with the attached list or other sources instead of silently changing a name or range. If the interactive query cannot be accessed, say so and do not invent an extracted list.

FIRST WORK PACKAGE
Start with Asteraceae and Photo Shot List SHOT-001 through SHOT-008. Research the family-level traits and five representative taxa already in Merged Plant List, including useful Hays County lookalikes. Find up to three genuinely useful image candidates for each of the eight shots. Favor a same-plant series showing habit, leaves, flower head from face and side, individual florets, and fruit. Work one family at a time; finish this batch before moving to the next family. State which shots have no verified candidate.

BOTANICAL EVIDENCE
Check accepted names against Kew WCVP/Plants of the World Online; keep submitted synonyms separately. Use BONAP TDC for regional candidates, descriptions, and character leads; APweb for family structure; Flora of North America and authoritative regional floras or monographs for keys; and UT Plant Resources Center Hays Flora or specimen-backed local records for local comparisons. Cite a direct source URL for each diagnostic claim. Write a simple description alongside the technical term, the part to inspect, the state to look for, exceptions, season, magnification, and the closest lookalike plus a reliable difference. Separate family traits from genus or species traits. Never infer Hays occurrence from Texas-wide distribution or infer nativity from a photograph. Flag uncertain names, IDs, and claims for human review.

PHOTOGRAPH RULES
Use actual photographs, not AI-generated botanical images. Check BONAP's photo gallery alongside individual records at iNaturalist, Wikimedia Commons, CalPhotos, Smithsonian Open Access, or specimen collections. Inspect each image itself and its original source page: the claimed organ must be visible, in focus, and recognizable at useful resolution. A pretty whole-plant image cannot stand in for a ligule, floret, phyllary, fruit, or other close-up. Record the exact organ, view, visible character, crop or annotation needed, taxon confidence, original image URL, source page/observation URL, photographer, image ID, and exact license with its source URL. A photo appearing on BONAP does not establish permission to copy it. A Research Grade observation is still a candidate until the photograph and taxon are checked. Keep images from the same individual linked with a Same-Plant Group ID; do not imply that separate observations show one plant. Do not expose precise coordinates of sensitive plants.

RIGHTS AND STATUS
Follow the workbook's License Policy. Prefer independently verified CC0/Public Domain or CC BY images, with attribution. Flag CC BY-SA for compatibility review; exclude noncommercial, no-derivatives, all-rights-reserved, and unknown-license images from the usable candidate set. Check the license on each individual photograph, not only the observation. Never guess rights, mark an image Display approved or Training approved, or claim that a candidate is already on the site. If you can legally provide the actual image files, use stable filenames tied to Image Record IDs; otherwise provide source links and mark the file as not acquired.

DELIVERABLES
Create four separate tables or downloadable CSV/XLSX sheets: (1) Research Queue additions using that sheet's exact columns and Record IDs; (2) Family Evidence corrections or new rows using its existing columns and Character Codes, with a reason for every correction and no duplicate claims; (3) Image Registry candidate rows using its exact 35 columns, one row per image and Review Status = Candidate or a more cautious existing controlled value; (4) Shot Coverage mapping each Shot ID to candidate Image Record IDs, visible evidence, and remaining gaps. Include a short research log with direct source links, access dates, unresolved taxonomy, license questions, and decisions for Calvin's review. Leave unknown cells blank and explain gaps. Do not overwrite the attached workbooks or silently fill missing evidence. Stop after the Asteraceae batch and report what is ready for review.`;

const questionOrder = [
  "AST-HEAD",
  "FAB-LEGUME",
  "EUP-THREE",
  "POA-LIGULE",
  "CYP-CLOSED",
  "LAM-OPPOSITE",
  "POA-SPIKELET",
  "LAM-SQUARE",
  "FAB-PULVINUS",
  "CYP-ANGLED",
  "AST-INVOLUCRE",
  "EUP-SCHIZO",
  "LAM-NUTLETS",
  "FAB-ONECARPEL",
  "POA-LEMMA",
  "CYP-ACHENE",
  "AST-SYNANTH",
  "EUP-COLUMN",
];

const questions = questionOrder
  .map((code) => evidence.find((row) => row.code === code))
  .filter((row): row is Evidence => Boolean(row));

const answerOptions: Array<{
  value: Answer;
  label: string;
  short: string;
}> = [
  { value: "yes", label: "Yes, I see it", short: "Yes" },
  { value: "no", label: "No, it is absent", short: "No" },
  { value: "unsure", label: "Not sure", short: "Unsure" },
  { value: "hidden", label: "Not visible now", short: "Not visible" },
];

function getLeadLabel(
  score: number,
  support: number,
  gap: number,
  answered: number,
) {
  if (!answered || support === 0) return "Awaiting evidence";
  if (score >= 9 && gap >= 4) return "Strong lead";
  if (score >= 5) return "Promising";
  if (score > 0) return "Worth checking";
  return "Weaker fit";
}

export default function Home() {
  const [tab, setTab] = useState<Tab>("identify");
  const [answers, setAnswers] = useState<Record<string, Answer>>({});
  const [questionIndex, setQuestionIndex] = useState(0);
  const [glossaryQuery, setGlossaryQuery] = useState("");
  const [glossaryGroup, setGlossaryGroup] = useState("All terms");
  const [capturedShots, setCapturedShots] = useState<Record<string, boolean>>({});
  const [promptCopied, setPromptCopied] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    let savedAnswers: Record<string, Answer> | null = null;
    let savedShots: Record<string, boolean> | null = null;
    try {
      const saved = window.localStorage.getItem("hays-botany-observations");
      if (saved) savedAnswers = JSON.parse(saved) as Record<string, Answer>;
      const savedPhotoShots = window.localStorage.getItem("hays-botany-photo-shots");
      if (savedPhotoShots) {
        savedShots = JSON.parse(savedPhotoShots) as Record<string, boolean>;
      }
    } catch {
      // A damaged or blocked local store should never stop field use.
    }

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker
        .register(assetPath("sw.js"), { scope: import.meta.env.BASE_URL })
        .then((registration) => registration.update())
        .catch(() => undefined);
    }

    const frame = window.requestAnimationFrame(() => {
      if (savedAnswers) setAnswers(savedAnswers);
      if (savedShots) setCapturedShots(savedShots);
      setHydrated(true);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    try {
      window.localStorage.setItem(
        "hays-botany-observations",
        JSON.stringify(answers),
      );
    } catch {
      // The identifier continues to work when browser storage is unavailable.
    }
  }, [answers, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    try {
      window.localStorage.setItem(
        "hays-botany-photo-shots",
        JSON.stringify(capturedShots),
      );
    } catch {
      // The field checklist remains usable without browser storage.
    }
  }, [capturedShots, hydrated]);

  const currentQuestion = questions[questionIndex];
  const answeredCount = Object.keys(answers).length;
  const capturedCount = Object.values(capturedShots).filter(Boolean).length;
  const currentVisual = visualForEvidence(learningVisuals, {
    family: currentQuestion.family,
    code: currentQuestion.code,
    organ: currentQuestion.organ,
    state: currentQuestion.state,
    text: currentQuestion.statement,
  });

  const filteredVocabulary = useMemo(() => {
    const needle = glossaryQuery.trim().toLocaleLowerCase();
    return vocabulary.filter((row) => {
      const matchesGroup =
        glossaryGroup === "All terms" || row.group === glossaryGroup;
      const matchesText =
        !needle ||
        [row.term, row.plain, row.fieldCue, row.synonyms, row.group]
          .join(" ")
          .toLocaleLowerCase()
          .includes(needle);
      return matchesGroup && matchesText;
    });
  }, [glossaryGroup, glossaryQuery]);

  const rankings = useMemo(() => {
    const scored = families.map((family) => {
      const rows = evidence.filter((row) => row.family === family.family);
      let score = 0;
      let support = 0;
      let conflict = 0;

      rows.forEach((row) => {
        const answer = answers[row.code];
        if (answer === "yes") {
          score += row.weight;
          support += 1;
        }
        if (answer === "no") {
          score -= row.weight * 0.75;
          conflict += 1;
        }
      });

      return { family, score, support, conflict };
    });

    return scored
      .sort(
        (a, b) =>
          b.score - a.score ||
          b.support - a.support ||
          a.family.order - b.family.order,
      )
      .map((row, index, all) => ({
        ...row,
        gap: index === 0 ? row.score - (all[1]?.score ?? 0) : 0,
      }));
  }, [answers]);

  const lead = rankings[0];
  const leadEvidence = useMemo(
    () =>
      evidence.filter(
        (row) => row.family === lead.family.family && answers[row.code] === "yes",
      ),
    [answers, lead.family.family],
  );
  const leadVisuals = visualsForFamily(
    learningVisuals,
    lead.family.family,
    2,
  );

  const setAnswer = (answer: Answer) => {
    setAnswers((current) => ({
      ...current,
      [currentQuestion.code]: answer,
    }));
  };

  const moveQuestion = (direction: 1 | -1) => {
    setQuestionIndex((current) => {
      const next = current + direction;
      return Math.min(Math.max(next, 0), questions.length - 1);
    });
  };

  const reset = () => {
    setAnswers({});
    setQuestionIndex(0);
  };

  const selectTab = (nextTab: Tab) => {
    setTab(nextTab);
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        document
          .getElementById("workspace-start")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  };

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Hays Botany ID home">
          <span className="brand-mark" aria-hidden="true">
            ✣
          </span>
          <span>
            <strong>Hays Botany ID</strong>
            <small>Field structure lab</small>
          </span>
        </a>
        <nav className="top-nav" aria-label="Primary navigation">
          <button
            className={tab === "identify" ? "active" : ""}
            onClick={() => selectTab("identify")}
          >
            Identify
          </button>
          <button
            className={tab === "families" ? "active" : ""}
            onClick={() => selectTab("families")}
          >
            Family Guide
          </button>
          <button
            className={tab === "glossary" ? "active" : ""}
            onClick={() => selectTab("glossary")}
          >
            Terms
          </button>
          <button
            className={tab === "photos" ? "active" : ""}
            onClick={() => selectTab("photos")}
          >
            Photos
          </button>
          <button
            className={tab === "sources" ? "active" : ""}
            onClick={() => selectTab("sources")}
          >
            Sources
          </button>
        </nav>
      </header>

      <div id="top" className="page-shell">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Hays County · Central Texas</p>
            <h1>
              Read the structure.
              <span>Find the family.</span>
            </h1>
            <p className="hero-deck">
              A Hays County field guide built around visible evidence. Start
              with plain language, learn the botanical term, compare families,
              and keep “not visible” separate from “not present.”
            </p>
            <div className="hero-actions">
              <button className="primary-action" onClick={() => selectTab("identify")}>
                Try the quick family key <span aria-hidden="true">→</span>
              </button>
              <button className="text-action" onClick={() => selectTab("families")}>
                Explore {familyCatalog.length} families
              </button>
            </div>
          </div>

          <div className="field-card" aria-label="Current local study scope">
            <div className="field-card-top">
              <span>FIELD GUIDE · PHASE 02</span>
              <span>{familyEvidenceCatalog.length} CLUES</span>
            </div>
            <div className="specimen-mark" aria-hidden="true">
              <span className="stem" />
              <span className="leaf leaf-one" />
              <span className="leaf leaf-two" />
              <span className="leaf leaf-three" />
              <span className="flower">✺</span>
            </div>
            <div className="field-card-bottom">
              <strong>{evidenceBackedFamilies} evidence-backed families</strong>
              <p>
                {currentEvidenceFamilies} in the current inventory ·{" "}
                {referenceFamilies} reference expansion
              </p>
            </div>
          </div>
        </section>

        <aside className="scope-banner">
          <span aria-hidden="true">◎</span>
          <p>
            <strong>The identification universe is intentionally broad.</strong>
            Native, naturalized, invasive, garden-escape, persistent
            cultivated, and common nursery plants may all belong here.
            Occurrence and nativity are labels—not reasons to hide a lookalike.
          </p>
        </aside>

        {tab === "identify" && (
          <section
            id="workspace-start"
            className="workspace"
            aria-labelledby="identify-title"
          >
            <div className="section-heading">
              <div>
                <p className="eyebrow">Quick key · six deep-dive families</p>
                <h2 id="identify-title">What does your plant show?</h2>
              </div>
              <button className="reset-button" onClick={reset} disabled={!answeredCount}>
                Reset observations
              </button>
            </div>

            <div className="identify-grid">
              <article className="question-panel">
                <div className="progress-row">
                  <span>
                    Character {questionIndex + 1} of {questions.length}
                  </span>
                  <span>{answeredCount} recorded</span>
                </div>
                <div className="progress-track" aria-hidden="true">
                  <span
                    style={{
                      width: `${((questionIndex + 1) / questions.length) * 100}%`,
                    }}
                  />
                </div>

                <div className="question-meta">
                  <span>{currentQuestion.organ}</span>
                  <span>{currentQuestion.visibility}</span>
                  <span>{currentQuestion.reliability} reliability</span>
                </div>
                <p className="question-family">
                  A clue for {currentQuestion.family}
                </p>
                <h3>{currentQuestion.state}</h3>
                <p className="question-copy">{currentQuestion.statement}</p>

                {currentVisual && (
                  <div className="question-learning-visual">
                    <div className="visual-lesson-label">
                      <span aria-hidden="true">◎</span>
                      <p>
                        <strong>See the term before you answer</strong>
                        Use the caption to find the same part on your plant.
                      </p>
                    </div>
                    <LearningPhoto
                      visual={currentVisual}
                      priority
                      showLimit
                    />
                  </div>
                )}

                <div className="answer-grid" role="group" aria-label="Your observation">
                  {answerOptions.map((option) => (
                    <button
                      key={option.value}
                      className={
                        answers[currentQuestion.code] === option.value
                          ? `answer-button selected ${option.value}`
                          : "answer-button"
                      }
                      onClick={() => setAnswer(option.value)}
                      aria-pressed={answers[currentQuestion.code] === option.value}
                    >
                      <span aria-hidden="true">
                        {option.value === "yes"
                          ? "✓"
                          : option.value === "no"
                            ? "×"
                            : option.value === "unsure"
                              ? "?"
                              : "◌"}
                      </span>
                      {option.label}
                    </button>
                  ))}
                </div>

                <details className="exception-note">
                  <summary>Where this clue can mislead</summary>
                  <p>{currentQuestion.limits}</p>
                  <p className="separates">{currentQuestion.separates}</p>
                </details>

                <div className="question-controls">
                  <button
                    onClick={() => moveQuestion(-1)}
                    disabled={questionIndex === 0}
                    aria-label="Previous character"
                  >
                    ← Previous
                  </button>
                  <button
                    onClick={() => moveQuestion(1)}
                    disabled={questionIndex === questions.length - 1}
                  >
                    Next character →
                  </button>
                </div>

                <details className="character-index">
                  <summary>Jump to any visible character</summary>
                  <div className="character-grid">
                    {questions.map((question, index) => (
                      <button
                        key={question.code}
                        className={
                          index === questionIndex
                            ? "current"
                            : answers[question.code]
                              ? "recorded"
                              : ""
                        }
                        onClick={() => setQuestionIndex(index)}
                      >
                        <span>{familyMarks[question.family]}</span>
                        <span>
                          <strong>{question.state}</strong>
                          <small>
                            {answers[question.code]
                              ? answerOptions.find(
                                  (option) =>
                                    option.value === answers[question.code],
                                )?.short
                              : question.organ}
                          </small>
                        </span>
                      </button>
                    ))}
                  </div>
                </details>
              </article>

              <aside className="results-panel" aria-live="polite">
                <div className="results-kicker">
                  <span>LIVE FAMILY RANKING</span>
                  <span>No forced answer</span>
                </div>
                <div className="lead-result">
                  <span className="result-mark" aria-hidden="true">
                    {familyMarks[lead.family.family]}
                  </span>
                  <div>
                    <p>
                      {getLeadLabel(
                        lead.score,
                        lead.support,
                        lead.gap,
                        answeredCount,
                      )}
                    </p>
                    <h3>{lead.family.family}</h3>
                    <span>{lead.family.commonName}</span>
                  </div>
                </div>

                <p className="lead-explanation">
                  {leadEvidence.length
                    ? `Supported by ${leadEvidence
                        .slice(0, 2)
                        .map((row) => row.state.toLowerCase())
                        .join(" and ")}.`
                    : "Record a visible character to begin ranking the families."}
                </p>

                <div className="lead-visuals" aria-label={`${lead.family.family} visual memory anchors`}>
                  {leadVisuals.map((visual) => (
                    <LearningPhoto key={visual.id} visual={visual} compact />
                  ))}
                </div>

                <ol className="ranking-list">
                  {rankings.map((row, index) => (
                    <li key={row.family.family}>
                      <span className="rank">{index + 1}</span>
                      <span className="mini-mark" aria-hidden="true">
                        {familyMarks[row.family.family]}
                      </span>
                      <span className="rank-name">
                        <strong>{row.family.family}</strong>
                        <small>
                          {row.support
                            ? `${row.support} supporting ${
                                row.support === 1 ? "clue" : "clues"
                              }`
                            : "No support yet"}
                        </small>
                      </span>
                      <span
                        className={
                          row.score > 0
                            ? "evidence-state positive"
                            : row.score < 0
                              ? "evidence-state negative"
                              : "evidence-state"
                        }
                      >
                        {row.score > 0 ? "+" : ""}
                        {Math.round(row.score)}
                      </span>
                    </li>
                  ))}
                </ol>

                <div className="next-look">
                  <span aria-hidden="true">⌕</span>
                  <p>
                    <strong>Best next look</strong>
                    {lead.family.confirmation}
                  </p>
                </div>
              </aside>
            </div>
          </section>
        )}

        {tab === "families" && (
          <Suspense
            fallback={
              <section className="family-lab family-loading">
                <span aria-hidden="true">✣</span>
                <p>Opening the family evidence guide…</p>
              </section>
            }
          >
            <FamilyGuide visuals={learningVisuals} />
          </Suspense>
        )}

        {tab === "glossary" && (
          <section
            id="workspace-start"
            className="glossary-lab"
            aria-labelledby="glossary-title"
          >
            <div className="section-heading family-heading">
              <div>
                <p className="eyebrow">Field language</p>
                <h2 id="glossary-title">Botany without the fog</h2>
              </div>
              <p>
                One hundred controlled terms, translated into plain language
                and paired with something you can actually inspect.
              </p>
            </div>

            <div className="glossary-tools">
              <label className="search-field">
                <span aria-hidden="true">⌕</span>
                <span className="sr-only">Search botanical terms</span>
                <input
                  type="search"
                  value={glossaryQuery}
                  onChange={(event) => setGlossaryQuery(event.target.value)}
                  placeholder="Search term, structure, or synonym"
                />
              </label>
              <label className="group-select">
                <span className="sr-only">Filter by character group</span>
                <select
                  value={glossaryGroup}
                  onChange={(event) => setGlossaryGroup(event.target.value)}
                >
                  {glossaryGroups.map((group) => (
                    <option key={group} value={group}>
                      {group}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="glossary-count">
              Showing {filteredVocabulary.length} of {vocabulary.length} terms
            </div>

            <div className="glossary-visual-note">
              <span aria-hidden="true">◎</span>
              <p>
                <strong>Photos now repeat the language.</strong> When a diagnostic
                image matches a term, the card shows the exact part, where to
                look, and a source-linked specimen. Some terms describe states
                that these photographs cannot honestly demonstrate, so those
                remain text-only.
              </p>
            </div>

            <div className="term-grid">
              {filteredVocabulary.map((row) => {
                const visual = visualForTerm(learningVisuals, row);
                return (
                  <article
                    className={`term-card ${visual ? "has-photo" : ""}`}
                    key={row.id}
                  >
                    <div className="term-topline">
                      <span>{row.group}</span>
                      <span>{row.id}</span>
                    </div>
                    <h3>{row.term}</h3>
                    {visual && <LearningPhoto visual={visual} compact />}
                    <p className="plain-definition">{row.plain}</p>
                    <div className="field-cue">
                      <span aria-hidden="true">⌕</span>
                      <p>
                        <strong>Field cue</strong>
                        {row.fieldCue}
                      </p>
                    </div>
                    {row.synonyms && (
                      <p className="term-meta">
                        <strong>Also called:</strong> {row.synonyms}
                      </p>
                    )}
                    {row.caution && (
                      <p className="term-caution">{row.caution}</p>
                    )}
                  </article>
                );
              })}
            </div>

            {!filteredVocabulary.length && (
              <div className="empty-state">
                <span aria-hidden="true">◌</span>
                <h3>No term matches that search.</h3>
                <button
                  onClick={() => {
                    setGlossaryQuery("");
                    setGlossaryGroup("All terms");
                  }}
                >
                  Clear filters
                </button>
              </div>
            )}
          </section>
        )}

        {tab === "photos" && (
          <section
            id="workspace-start"
            className="photos-lab"
            aria-labelledby="photos-title"
          >
            <div className="section-heading family-heading">
              <div>
                <p className="eyebrow">Local reference collection</p>
                <h2 id="photos-title">Photograph the evidence</h2>
              </div>
              <p>
                Build a Hays County image set one diagnostic view at a time.
                Keep every series tied to the same individual plant.
              </p>
            </div>

            <section className="ut-study-shelf" aria-labelledby="ut-study-shelf-title">
              <div className="ut-study-shelf-heading">
                <div>
                  <p className="eyebrow">New private study collection</p>
                  <h3 id="ut-study-shelf-title">12 UT diagnostic photos</h3>
                </div>
                <p>
                  The selected structures are now shown first. Open the detailed
                  cards below for what each photograph proves—and what it does not.
                </p>
              </div>
              <div className="ut-study-strip">
                {utArchiveCandidates.map((candidate, index) => (
                  <a
                    href="#ut-study-details"
                    key={`study-shelf:${candidate.specimen}:${candidate.structure}`}
                    aria-label={`See study notes for ${candidate.specimen}: ${candidate.structure}`}
                  >
                    <img
                      src={candidate.imageUrl}
                      alt={candidate.imageAlt}
                      loading={index < 4 ? "eager" : "lazy"}
                      decoding="async"
                    />
                    <span>{candidate.structure}</span>
                    <em>{candidate.specimen}</em>
                  </a>
                ))}
              </div>
              <p className="ut-study-shelf-rights">
                Owner-only study copies · permission requested · do not share or republish
              </p>
            </section>

            <div className="photo-intro-grid">
              <article className="registry-card">
                <span className="card-kicker">COMPANION WORKBOOK</span>
                <h3>Record the image, organ, name, place, and rights.</h3>
                <p>
                  The registry keeps each image on its own row, checks whether
                  its license permits website display or AI training, and
                  carries the work queue another researcher can pick up.
                </p>
                <a
                  href={assetPath("downloads/Hays_Botany_Image_Registry.xlsx")}
                  download
                >
                  Download image registry <span aria-hidden="true">↓</span>
                </a>
              </article>

              <article className="protocol-card">
                <span className="card-kicker">SAME-PLANT SERIES</span>
                <ol>
                  <li><span>01</span> Habitat and scale</li>
                  <li><span>02</span> Whole plant and growth form</li>
                  <li><span>03</span> Leaves, nodes, and attachment</li>
                  <li><span>04</span> Flower from several angles</li>
                  <li><span>05</span> Fruit and seed when present</li>
                  <li><span>06</span> Diagnostic macro with a scale</li>
                </ol>
              </article>
            </div>

            <div className="scope-method-note">
              <span aria-hidden="true">◎</span>
              <div>
                <h3>Find plant parts with BONAP</h3>
                <p>
                  In BONAP’s Taxonomic Data Center, select Texas, then Hays
                  County. Use its descriptions and photo gallery to find the
                  exact structure on the shot list. The county query also
                  includes adjacent counties, and each photo needs its own
                  credit and reuse check before it can appear here.
                </p>
                <a href="https://bonap.net/tdc" target="_blank" rel="noreferrer">
                  Open BONAP Taxonomic Data Center ↗
                </a>
              </div>
            </div>

            <div className="license-note">
              <span aria-hidden="true">i</span>
              <p>
                <strong>Your own photographs are the cleanest foundation.</strong>
                Record creator, date, locality, identification confidence, and
                a clear license. Never disturb a plant just to expose a trait.
              </p>
            </div>

            <section
              id="ut-study-details"
              className="ut-archive-audit"
              aria-labelledby="ut-audit-title"
            >
              <div className="ut-audit-heading">
                <div>
                  <p className="eyebrow">UT Austin archive audit · 24 Sep 2026</p>
                  <h3 id="ut-audit-title">Private study set collected. Permission pending.</h3>
                </div>
                <p>
                  Every one of the archive’s 381 linked taxon pages was checked:
                  1,960 photographs in total. Twelve of the clearest diagnostic
                  frames are now stored here for Calvin’s owner-only study. None
                  of the index or species pages states a license or grants
                  republication rights, so do not share or republish this set.
                </p>
              </div>

              <div className="ut-audit-stats" aria-label="UT archive review totals">
                <div><strong>381</strong><span>taxon pages reviewed</span></div>
                <div><strong>1,960</strong><span>photographs inventoried</span></div>
                <div><strong>12</strong><span>private-study images collected</span></div>
                <div><strong>0</strong><span>pages with an explicit reuse license</span></div>
              </div>

              <details className="ut-candidate-details" open>
                <summary>
                  <span>View the 12-photo private study set</span>
                  <span aria-hidden="true">+</span>
                </summary>
                <p className="ut-candidate-intro">
                  Each card states what the frame actually shows—and what it
                  does not prove. Every image keeps a direct link to its UT source
                  page. Carex microdonta and Eleocharis obtusa were excluded
                  because the archive filenames themselves signal uncertainty.
                </p>
                <div className="ut-candidate-grid">
                  {utArchiveCandidates.map((candidate) => (
                    <article key={`${candidate.specimen}:${candidate.structure}`}>
                      <div>
                        <span>{candidate.family}</span>
                        <span className="rights-pending">Private study · permission pending</span>
                      </div>
                      <a
                        className="ut-study-image"
                        href={candidate.sourceUrl}
                        target="_blank"
                        rel="noreferrer"
                        aria-label={`Open the UT source page for ${candidate.specimen}: ${candidate.structure}`}
                      >
                        <img
                          src={candidate.imageUrl}
                          alt={candidate.imageAlt}
                          loading="lazy"
                          decoding="async"
                        />
                      </a>
                      <p>{candidate.specimen}</p>
                      <h4>{candidate.structure}</h4>
                      <dl className="ut-visibility-notes">
                        <div>
                          <dt>Visible here</dt>
                          <dd>{candidate.visible}</dd>
                        </div>
                        <div>
                          <dt>Limit</dt>
                          <dd>{candidate.limit}</dd>
                        </div>
                      </dl>
                      <a href={candidate.sourceUrl} target="_blank" rel="noreferrer">
                        UT BIO 406D source page ↗
                      </a>
                    </article>
                  ))}
                </div>
              </details>

              <div className="ut-audit-actions">
                <a
                  href="https://web.biosci.utexas.edu/bio406d/PlantPics_archive.htm"
                  target="_blank"
                  rel="noreferrer"
                >
                  Open the complete UT archive ↗
                </a>
                <p>
                  Permission status: requested, not yet granted. This collection
                  must remain owner-only. Seven other archive pages contain
                  identification uncertainty cues and were not used as exemplars.
                </p>
              </div>
            </section>

            <section className="diagnostic-atlas" aria-labelledby="atlas-title">
              <div className="atlas-heading">
                <div>
                  <p className="eyebrow">Structure atlas · 18 close views</p>
                  <h3 id="atlas-title">See the part before you hunt for it</h3>
                </div>
                <p>
                  These are teaching examples of family structures, not a
                  promise that every local species looks identical. Open the
                  source to inspect the original context.
                </p>
              </div>

              {photoTargets.map((group) => (
                <section className="atlas-family" key={`atlas:${group.family}`}>
                  <div className="atlas-family-heading">
                    <span aria-hidden="true">{familyMarks[group.family]}</span>
                    <div>
                      <h4>{group.family}</h4>
                      <p>{group.note}</p>
                    </div>
                  </div>
                  <div className="diagnostic-photo-grid">
                    {diagnosticPhotos
                      .filter((photo) => photo.family === group.family)
                      .map((photo) => (
                        <article
                          className="diagnostic-photo-card"
                          key={`${photo.family}:${photo.title}`}
                        >
                          <a
                            className="diagnostic-image-link"
                            href={photo.sourceUrl}
                            target="_blank"
                            rel="noreferrer"
                            aria-label={`Open source for ${photo.title}`}
                          >
                            <img
                              src={photo.imageUrl}
                              alt={`${photo.specimen}: ${photo.title}. ${photo.lookFor}`}
                              loading="lazy"
                              decoding="async"
                              referrerPolicy="no-referrer"
                            />
                            <span>{photo.organ}</span>
                          </a>
                          <div className="diagnostic-image-key" aria-label="Parts visible in this photo">
                            <strong>In this frame</strong>
                            <ul>
                              {photo.imageKey.map((item) => (
                                <li key={item}>{item}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="diagnostic-photo-copy">
                            <p className="specimen-label">{photo.specimen}</p>
                            <h5>{photo.title}</h5>
                            <dl>
                              <div>
                                <dt>Find it</dt>
                                <dd>{photo.lookFor}</dd>
                              </div>
                              <div>
                                <dt>Why it matters</dt>
                                <dd>{photo.proves}</dd>
                              </div>
                              <div className="photo-caution">
                                <dt>Do not overcall it</dt>
                                <dd>{photo.caution}</dd>
                              </div>
                            </dl>
                            <a
                              className="photo-source"
                              href={photo.sourceUrl}
                              target="_blank"
                              rel="noreferrer"
                            >
                              View source · {photo.source} ↗
                            </a>
                          </div>
                        </article>
                      ))}
                  </div>
                </section>
              ))}
            </section>

            <div className="photo-progress">
              <div>
                <p className="eyebrow">Your same-plant shot list</p>
                <h3>{capturedCount} of 48 diagnostic views recorded</h3>
              </div>
              <div
                className="progress-track"
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={48}
                aria-valuenow={capturedCount}
              >
                <span style={{ width: `${(capturedCount / 48) * 100}%` }} />
              </div>
            </div>

            <div className="photo-family-grid">
              {photoTargets.map((group) => (
                <article className="photo-family-card" key={group.family}>
                  <div className="photo-family-title">
                    <span>{familyMarks[group.family]}</span>
                    <h3>{group.family}</h3>
                  </div>
                  <p>{group.note}</p>
                  <div className="shot-list">
                    {group.targets.map((target) => {
                      const key = `${group.family}:${target}`;
                      const captured = Boolean(capturedShots[key]);
                      return (
                        <button
                          key={key}
                          className={captured ? "captured" : ""}
                          aria-pressed={captured}
                          onClick={() =>
                            setCapturedShots((current) => ({
                              ...current,
                              [key]: !current[key],
                            }))
                          }
                        >
                          <span aria-hidden="true">{captured ? "✓" : "○"}</span>
                          {target}
                        </button>
                      );
                    })}
                  </div>
                </article>
              ))}
            </div>

            <article className="delegate-card">
              <div>
                <p className="eyebrow">Parallel research</p>
                <h3>Give another AI a photo and research work package.</h3>
                <p>
                  Start with Asteraceae and its eight priority shots. Attach both
                  workbooks, then ask for source-backed traits and photographs
                  that clearly show each plant part. Review candidates before use.
                </p>
              </div>
              <button
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(delegationPrompt);
                    setPromptCopied(true);
                    window.setTimeout(() => setPromptCopied(false), 1800);
                  } catch {
                    setPromptCopied(false);
                  }
                }}
              >
                {promptCopied ? "Prompt copied" : "Copy photo + research prompt"}
              </button>
            </article>
          </section>
        )}

        {tab === "sources" && (
          <section
            id="workspace-start"
            className="sources-lab"
            aria-labelledby="sources-title"
          >
            <div className="section-heading family-heading">
              <div>
                <p className="eyebrow">Evidence & method</p>
                <h2 id="sources-title">What the tool trusts</h2>
              </div>
              <p>
                Names, family characters, and local comparisons do different
                jobs. This tool keeps those evidence layers separate.
              </p>
            </div>

            <div className="method-grid">
              <article>
                <span>01</span>
                <h3>Family structure</h3>
                <p>
                  APweb anchors family circumscription and character suites,
                  including exceptions and uncertain synapomorphies.
                </p>
              </article>
              <article>
                <span>02</span>
                <h3>Regional keys</h3>
                <p>
                  Flora of North America provides the practical North American
                  descriptions, keys, and regional variation.
                </p>
              </article>
              <article>
                <span>03</span>
                <h3>Accepted names</h3>
                <p>
                  Kew’s WCVP and Plants of the World Online supply accepted
                  names, synonyms, ranks, families, and stable identifiers.
                </p>
              </article>
              <article>
                <span>04</span>
                <h3>Hays County lens</h3>
                <p>
                  BONAP’s Texas/Hays query helps find regional candidates;
                  the UT Plant Resources Center and specimen records help
                  confirm local occurrence and comparisons.
                </p>
              </article>
            </div>

            <div className="scope-method-note">
              <span aria-hidden="true">◎</span>
              <div>
                <h3>BONAP’s Hays query includes nearby counties</h3>
                <p>
                  The Taxonomic Data Center offers family, genus, and species
                  descriptions, biological attributes, a character key, and
                  photos. Its county search deliberately includes Hays and
                  adjacent counties. We use those results to find plants to
                  investigate, then check a Hays-specific record before
                  calling one documented in the county.
                </p>
                <a href="https://bonap.net/tdc" target="_blank" rel="noreferrer">
                  Search BONAP ↗
                </a>
              </div>
            </div>

            <div className="evidence-model">
              <div>
                <p className="eyebrow">How the database works</p>
                <h3>
                  {familyEvidenceCatalog.length} clues stay attached to their
                  limits.
                </h3>
              </div>
              <p>
                Core and strong characters carry more weight than supporting
                traits. “No” weakens only the family tied to that character.
                “Not sure” and “Not visible” are neutral. The score is an
                evidence ranking—not a probability and never a final
                determination.
              </p>
            </div>

            <div className="scope-method-note">
              <span aria-hidden="true">◎</span>
              <div>
                <h3>Origin and occurrence are separate from identification.</h3>
                <p>
                  A plant can be native, naturalized, invasive, escaped from a
                  garden, persistent after cultivation, or simply a common
                  nursery lookalike. The guide keeps those possibilities
                  visible and waits for locality evidence before assigning a
                  status.
                </p>
              </div>
            </div>

            <article className="registry-card database-download-card">
              <span className="card-kicker">DATABASE SNAPSHOT · VERSION 4</span>
              <h3>Take the complete research workbook with you.</h3>
              <p>
                The workbook contains the master plant inventory, family
                coverage dashboard, all 742 automation records, the normalized
                model view, and the detailed Euphorbiaceae comparison work.
              </p>
              <a
                href={assetPath("downloads/Hays_County_Botany_Master_List.xlsx")}
                download
              >
                Download master database <span aria-hidden="true">↓</span>
              </a>
            </article>

            <div className="ai-reminder">
              <span className="ai-label">PARKED FOR A LATER PHASE</span>
              <div>
                <h3>Photo-powered plant ID</h3>
                <p>
                  Images will eventually propose visible traits and candidate
                  families. This botanical evidence model will rerank those
                  candidates and request diagnostic follow-up photos instead of
                  forcing a species answer.
                </p>
              </div>
              <span className="ai-state">REMEMBERED</span>
            </div>

            <div className="source-section-heading">
              <div>
                <p className="eyebrow">Source register</p>
                <h3>{sources.length} references carried with the data</h3>
              </div>
              <p>Links open the original source in a new tab.</p>
            </div>

            <div className="source-list">
              {sources.map(([id, title, scope, author, url, date, note]) => (
                <article key={id}>
                  <span className="source-id">{id}</span>
                  <div className="source-main">
                    <a href={url} target="_blank" rel="noreferrer">
                      {title} <span aria-hidden="true">↗</span>
                    </a>
                    <p>{scope}</p>
                    <small>
                      {author} · {date}
                    </small>
                  </div>
                  <p className="source-note">{note}</p>
                </article>
              ))}
            </div>
          </section>
        )}
      </div>

      <footer>
        <span>HAYS BOTANY ID · PHASE 02</span>
        <p>
          A field-learning and comparison tool—not a taxonomic authority.
          Confirm with a regional key, mature material, or a specimen when the
          stakes matter.
        </p>
      </footer>
    </main>
  );
}

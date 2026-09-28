import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";

const requiredFiles = [
  "dist/index.html",
  "dist/favicon.svg",
  "dist/manifest.webmanifest",
  "dist/sw.js",
  "dist/downloads/Hays_Botany_Image_Registry.xlsx",
  "dist/downloads/Hays_County_Botany_Master_List.xlsx",
  "dist/images/ut-study/tetragonotheca-phyllaries.jpg",
  "dist/images/ut-study/cyperus-spikelets.jpg",
];

await Promise.all(requiredFiles.map((file) => access(file)));

const html = await readFile("dist/index.html", "utf8");
assert.match(html, /<title>Hays Botany ID<\/title>/);
assert.match(html, /type="module"/);
assert.doesNotMatch(html, /src="\/assets\//);
assert.doesNotMatch(html, /href="\/assets\//);

console.log(`Verified ${requiredFiles.length} required build files and relative asset paths.`);

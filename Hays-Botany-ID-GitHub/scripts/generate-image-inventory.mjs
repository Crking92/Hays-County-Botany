import { readFile, writeFile } from "node:fs/promises";

const source = await readFile("src/App.tsx", "utf8");

const section = (start, end) => {
  const startIndex = source.indexOf(start);
  const endIndex = source.indexOf(end, startIndex);
  if (startIndex < 0 || endIndex < 0) {
    throw new Error(`Could not find ${start} … ${end}`);
  }
  return source.slice(startIndex, endIndex);
};

const objects = (value) =>
  [...value.matchAll(/\{\n([\s\S]*?)\n\s*\},?/g)].map((match) => match[1]);

const textField = (value, name) =>
  value.match(new RegExp(`${name}:\\s*"([^"]*)"`))?.[1] ?? "";

const pathField = (value) =>
  value.match(/imageUrl:\s*assetPath\("([^"]+)"\)/)?.[1] ??
  textField(value, "imageUrl");

const rows = [];

for (const block of objects(section("const diagnosticPhotos", "type ArchiveCandidate"))) {
  const imageUrl = pathField(block);
  if (!imageUrl) continue;
  rows.push({
    group: "Diagnostic teaching photograph",
    family: textField(block, "family"),
    specimen: textField(block, "specimen"),
    structure: textField(block, "organ"),
    display: "Remote source-linked image",
    image: imageUrl,
    source: textField(block, "source"),
    sourcePage: textField(block, "sourceUrl"),
    status: "Exact image rights require review before public publication",
  });
}

for (const block of objects(section("const utArchiveCandidates", "const learningVisuals"))) {
  const imageUrl = pathField(block);
  if (!imageUrl) continue;
  rows.push({
    group: "UT BIO 406D private study photograph",
    family: textField(block, "family"),
    specimen: textField(block, "specimen"),
    structure: textField(block, "structure"),
    display: "Included local file",
    image: imageUrl,
    source: "UT BIO 406D PlantPics archive",
    sourcePage: textField(block, "sourceUrl"),
    status: "Permission pending; private study only; do not publish",
  });
}

const columns = [
  "group",
  "family",
  "specimen",
  "structure",
  "display",
  "image",
  "source",
  "sourcePage",
  "status",
];
const csv = [
  columns.join(","),
  ...rows.map((row) =>
    columns
      .map((column) => `"${String(row[column]).replaceAll('"', '""')}"`)
      .join(","),
  ),
].join("\n");

await writeFile("IMAGE-SOURCES.csv", `${csv}\n`);
console.log(`Wrote ${rows.length} photograph records to IMAGE-SOURCES.csv.`);

import { useMemo, useState } from "react";
import { priorityFamilies as deepRows } from "./botany-data.mjs";
import {
  familyCatalog as catalogRows,
  familyEvidenceCatalog as evidenceRows,
} from "./family-evidence-data.mjs";
import LearningPhoto from "./learning-photo";
import {
  type LearningVisual,
  visualForEvidence,
  visualsForFamily,
} from "./learning-visuals";

type FamilyScope =
  | "evidence"
  | "all"
  | "current"
  | "expansion"
  | "pending"
  | "deep";

type DeepFamily = {
  family: string;
  commonName: string;
  recognition: string;
  fastestLook: string;
  confirmation: string;
  exceptions: string;
  confusions: string;
  localGenera: string;
};

type CatalogFamily = {
  family: string;
  plantCount: number;
  inventoryScope: "Current master inventory" | "Reference expansion";
  evidenceStatus: "Detailed pilot" | "Source-backed draft" | "Research queued";
  evidenceCount: number;
  fieldReady: number;
  humanReview: number;
};

type CatalogEvidence = {
  family: string;
  code: string;
  scopeClass: string;
  organ: string;
  state: string;
  role: string;
  weight: number;
  reliability: string;
  visibility: string;
  season: string;
  plain: string;
  limits: string;
  separates: string;
  hays: string;
  uncertainty: string;
  humanReview: boolean;
  reviewReason: string;
  lookalikes: string;
  apweb: string;
  flora: string;
  powo: string;
  reviewStatus: string;
  fieldReady: boolean;
};

const familyCatalog = catalogRows as CatalogFamily[];
const familyEvidence = evidenceRows as CatalogEvidence[];
const deepFamilies = deepRows as DeepFamily[];
const deepFamilyMap = new Map(
  deepFamilies.map((family) => [family.family, family]),
);
const evidenceByFamily = new Map<string, CatalogEvidence[]>();

familyEvidence.forEach((row) => {
  const rows = evidenceByFamily.get(row.family) ?? [];
  rows.push(row);
  evidenceByFamily.set(row.family, rows);
});
evidenceByFamily.forEach((rows) =>
  rows.sort(
    (a, b) =>
      Number(b.fieldReady) - Number(a.fieldReady) ||
      b.weight - a.weight ||
      Number(a.humanReview) - Number(b.humanReview) ||
      a.code.localeCompare(b.code),
  ),
);

const familyMarks: Record<string, string> = {
  Asteraceae: "✺",
  Poaceae: "⌁",
  Fabaceae: "◒",
  Euphorbiaceae: "⬡",
  Lamiaceae: "✦",
  Cyperaceae: "△",
};
const getFamilyMark = (family: string) =>
  familyMarks[family] ?? family.slice(0, 1).toUpperCase();
const firstUrl = (value: string) =>
  value.match(/https?:\/\/[^\s;]+/)?.[0] ?? "";
const sourceLinks = (row: CatalogEvidence) => {
  const candidates = [
    ["APweb", firstUrl(row.apweb)],
    ["Practical flora", firstUrl(row.flora)],
    ["POWO / WCVP", firstUrl(row.powo)],
  ] as const;
  const seen = new Set<string>();
  return candidates.filter(([, url]) => {
    if (!url || seen.has(url)) return false;
    seen.add(url);
    return true;
  });
};

const currentEvidenceFamilies = familyCatalog.filter(
  (row) =>
    row.inventoryScope === "Current master inventory" &&
    row.evidenceCount > 0,
).length;
const referenceFamilies = familyCatalog.filter(
  (row) => row.inventoryScope === "Reference expansion",
).length;
const pendingFamilies = familyCatalog.filter(
  (row) => row.evidenceCount === 0,
).length;
const reviewClues = familyEvidence.filter((row) => row.humanReview).length;

export default function FamilyGuide({
  visuals,
}: {
  visuals: LearningVisual[];
}) {
  const [query, setQuery] = useState("");
  const [scope, setScope] = useState<FamilyScope>("evidence");
  const [activeFamily, setActiveFamily] = useState("Asteraceae");
  const [compareFamily, setCompareFamily] = useState("");
  const [showAllEvidence, setShowAllEvidence] = useState(false);

  const filteredFamilies = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase();
    return familyCatalog.filter((row) => {
      const matchesScope =
        scope === "all" ||
        (scope === "evidence" && row.evidenceCount > 0) ||
        (scope === "current" &&
          row.inventoryScope === "Current master inventory") ||
        (scope === "expansion" &&
          row.inventoryScope === "Reference expansion") ||
        (scope === "pending" && row.evidenceCount === 0) ||
        (scope === "deep" && deepFamilyMap.has(row.family));
      if (!matchesScope) return false;
      if (!needle) return true;
      return (
        row.family.toLocaleLowerCase().includes(needle) ||
        (evidenceByFamily.get(row.family) ?? []).some((evidence) =>
          [
            evidence.organ,
            evidence.state,
            evidence.plain,
            evidence.separates,
            evidence.lookalikes,
          ]
            .join(" ")
            .toLocaleLowerCase()
            .includes(needle),
        )
      );
    });
  }, [query, scope]);

  const summary =
    familyCatalog.find((row) => row.family === activeFamily) ??
    familyCatalog[0];
  const deepFamily = deepFamilyMap.get(activeFamily);
  const activeEvidence = evidenceByFamily.get(activeFamily) ?? [];
  const visibleEvidence = showAllEvidence
    ? activeEvidence
    : activeEvidence.filter((row) => row.fieldReady);
  const comparison = familyCatalog.find(
    (row) => row.family === compareFamily,
  );
  const comparisonEvidence = (
    evidenceByFamily.get(compareFamily) ?? []
  ).filter((row) => row.fieldReady);
  const familyVisuals = visualsForFamily(visuals, activeFamily, 3);

  return (
    <section
      id="workspace-start"
      className="family-lab"
      aria-labelledby="families-title"
    >
      <div className="section-heading family-heading">
        <div>
          <p className="eyebrow">Searchable family field guide</p>
          <h2 id="families-title">
            {familyCatalog.length} families · {familyEvidence.length} evidence
            records
          </h2>
        </div>
        <p>
          Plain-language recognition comes first. Botanical terms, exceptions,
          visibility, and sources stay attached to the same clue.
        </p>
      </div>

      <div className="coverage-strip" aria-label="Family guide coverage">
        <div>
          <strong>{currentEvidenceFamilies}</strong>
          <span>current families covered</span>
        </div>
        <div>
          <strong>{referenceFamilies}</strong>
          <span>reference-expansion families</span>
        </div>
        <div>
          <strong>{pendingFamilies}</strong>
          <span>families still queued</span>
        </div>
        <div>
          <strong>{reviewClues}</strong>
          <span>clues needing review</span>
        </div>
      </div>

      <div className="family-catalog-tools">
        <label className="search-field family-search">
          <span aria-hidden="true">⌕</span>
          <span className="sr-only">Search family evidence</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search family, organ, structure, or lookalike"
          />
        </label>
        <label className="group-select">
          <span className="sr-only">Filter family coverage</span>
          <select
            value={scope}
            onChange={(event) =>
              setScope(event.target.value as FamilyScope)
            }
          >
            <option value="evidence">Evidence ready</option>
            <option value="all">All indexed families</option>
            <option value="current">Current master inventory</option>
            <option value="expansion">Reference expansion</option>
            <option value="pending">Research queued</option>
            <option value="deep">Six deep-dive families</option>
          </select>
        </label>
      </div>

      <div className="family-catalog-count">
        Showing {filteredFamilies.length} of {familyCatalog.length} indexed
        families
      </div>

      <div className="family-catalog-layout">
        <div className="family-index" aria-label="Family index">
          {filteredFamilies.map((family) => (
            <button
              className={
                activeFamily === family.family
                  ? "family-index-row active"
                  : "family-index-row"
              }
              key={family.family}
              onClick={() => {
                setActiveFamily(family.family);
                setShowAllEvidence(false);
                setCompareFamily("");
              }}
            >
              <span className="catalog-mark" aria-hidden="true">
                {getFamilyMark(family.family)}
              </span>
              <span className="catalog-name">
                <strong>{family.family}</strong>
                <small>
                  {family.evidenceCount
                    ? `${family.evidenceCount} evidence records`
                    : "Research queued"}
                </small>
              </span>
              <span className="catalog-count">
                <strong>{family.plantCount}</strong>
                <small>plant names</small>
              </span>
            </button>
          ))}
          {!filteredFamilies.length && (
            <div className="family-index-empty">
              <span aria-hidden="true">◌</span>
              <p>No family or character matches this search.</p>
              <button
                onClick={() => {
                  setQuery("");
                  setScope("evidence");
                }}
              >
                Clear search
              </button>
            </div>
          )}
        </div>

        <article className="family-dossier">
          <header className="dossier-header">
            <div className="dossier-title-row">
              <span className="dossier-mark" aria-hidden="true">
                {getFamilyMark(summary.family)}
              </span>
              <div>
                <p>
                  {summary.inventoryScope} · {summary.evidenceStatus}
                </p>
                <h3>{summary.family}</h3>
                <span>{deepFamily?.commonName ?? "Botanical family dossier"}</span>
              </div>
            </div>
            <div className="dossier-numbers">
              <div>
                <strong>{summary.plantCount}</strong>
                <span>plant names</span>
              </div>
              <div>
                <strong>{summary.evidenceCount}</strong>
                <span>evidence rows</span>
              </div>
              <div>
                <strong>{summary.fieldReady}</strong>
                <span>field-ready clues</span>
              </div>
            </div>
          </header>

          {familyVisuals.length > 0 && (
            <section className="dossier-visual-section" aria-label={`${summary.family} visual memory anchors`}>
              <div className="dossier-visual-heading">
                <div>
                  <p className="eyebrow">Visual memory anchors</p>
                  <h4>See the structure, say the term, find it again</h4>
                </div>
                <p>
                  These views repeat below beside the evidence they help you
                  inspect. A photograph is a location guide, not proof by itself.
                </p>
              </div>
              <div className="dossier-visual-grid">
                {familyVisuals.map((visual) => (
                  <LearningPhoto key={visual.id} visual={visual} compact showLimit />
                ))}
              </div>
            </section>
          )}

          {deepFamily && (
            <div className="deep-profile">
              <div className="recognition-callout">
                <span>Recognition in one breath</span>
                <p>{deepFamily.recognition}</p>
              </div>
              <div className="family-detail-grid">
                <div>
                  <h4>Fastest field look</h4>
                  <p>{deepFamily.fastestLook}</p>
                </div>
                <div>
                  <h4>Confirm it</h4>
                  <p>{deepFamily.confirmation}</p>
                </div>
                <div>
                  <h4>Expect variation</h4>
                  <p>{deepFamily.exceptions}</p>
                </div>
                <div>
                  <h4>Common confusions</h4>
                  <p>{deepFamily.confusions}</p>
                </div>
              </div>
              <div className="local-strip">
                <span>LOCAL GENERA</span>
                <p>{deepFamily.localGenera}</p>
              </div>
            </div>
          )}

          {activeEvidence.length ? (
            <>
              <div className="dossier-controls">
                <div>
                  <p className="eyebrow">Evidence cards</p>
                  <h4>
                    {showAllEvidence
                      ? "Every source-backed record"
                      : "Clues you can usually inspect in the field"}
                  </h4>
                </div>
                <div className="dossier-control-actions">
                  <button
                    className={showAllEvidence ? "" : "active"}
                    onClick={() => setShowAllEvidence(false)}
                  >
                    Field-ready
                  </button>
                  <button
                    className={showAllEvidence ? "active" : ""}
                    onClick={() => setShowAllEvidence(true)}
                  >
                    All evidence
                  </button>
                </div>
              </div>

              <div className="evidence-card-list">
                {visibleEvidence.map((row) => {
                  const evidenceVisual = visualForEvidence(visuals, {
                    family: row.family,
                    code: row.code,
                    organ: row.organ,
                    state: row.state,
                    text: row.plain,
                  });
                  return (
                    <article
                      className={`evidence-card ${
                        row.humanReview ? "review-needed" : ""
                      } ${evidenceVisual ? "has-visual" : ""}`}
                      key={`${row.family}:${row.code}`}
                    >
                      <div className="evidence-topline">
                        <span>{row.organ}</span>
                        <span>{row.scopeClass}</span>
                        <span>
                          Weight {row.weight} · {row.role}
                        </span>
                      </div>
                      {evidenceVisual && (
                        <div className="evidence-learning-visual">
                          <LearningPhoto visual={evidenceVisual} compact showLimit />
                        </div>
                      )}
                      <p className="evidence-plain">{row.plain}</p>
                      <div className="technical-translation">
                        <span>Botanical wording</span>
                        <p>{row.state}</p>
                      </div>
                      <div className="evidence-meta">
                        <span>⌕ {row.visibility}</span>
                        <span>◷ {row.season}</span>
                        <span>Reliability: {row.reliability}</span>
                        {row.humanReview && (
                          <span className="review-flag">
                            Human review needed
                          </span>
                        )}
                      </div>
                      <details>
                        <summary>
                          How to use it, exceptions, and Hays County notes
                        </summary>
                        <div className="evidence-detail-grid">
                          <div>
                            <strong>What it helps separate</strong>
                            <p>{row.separates || "Not yet recorded."}</p>
                          </div>
                          <div>
                            <strong>Where it can mislead</strong>
                            <p>{row.limits || "No exception recorded."}</p>
                          </div>
                          <div>
                            <strong>Hays County use</strong>
                            <p>{row.hays || "Local application pending."}</p>
                          </div>
                          <div>
                            <strong>Review state</strong>
                            <p>
                              {row.reviewReason ||
                                `${row.reviewStatus}; uncertainty ${row.uncertainty.toLowerCase()}.`}
                            </p>
                          </div>
                        </div>
                        <div className="evidence-source-links">
                          {sourceLinks(row).map(([label, url]) => (
                            <a
                              href={url}
                              key={`${row.code}:${label}`}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {label} ↗
                            </a>
                          ))}
                        </div>
                      </details>
                    </article>
                  );
                })}
              </div>

              {!visibleEvidence.length && (
                <div className="pending-dossier compact">
                  <span aria-hidden="true">⌕</span>
                  <div>
                    <h4>No field-ready shortcut is stored yet.</h4>
                    <p>
                      The current records require dissection, magnification,
                      reference checking, or human review.
                    </p>
                    <button onClick={() => setShowAllEvidence(true)}>
                      Show all evidence
                    </button>
                  </div>
                </div>
              )}

              <section className="comparison-builder">
                <div>
                  <p className="eyebrow">Side-by-side check</p>
                  <h4>Compare the strongest visible clues</h4>
                </div>
                <label className="group-select compare-select">
                  <span className="sr-only">Choose a family to compare</span>
                  <select
                    value={compareFamily}
                    onChange={(event) => setCompareFamily(event.target.value)}
                  >
                    <option value="">Choose another family</option>
                    {familyCatalog
                      .filter(
                        (row) =>
                          row.family !== activeFamily &&
                          row.evidenceCount > 0,
                      )
                      .map((row) => (
                        <option key={row.family} value={row.family}>
                          {row.family}
                        </option>
                      ))}
                  </select>
                </label>
              </section>

              {comparison && (
                <div className="family-comparison">
                  {[
                    {
                      summary,
                      rows: activeEvidence.filter((row) => row.fieldReady),
                    },
                    {
                      summary: comparison,
                      rows: comparisonEvidence,
                    },
                  ].map((column) => (
                    <div key={column.summary.family}>
                      <div className="comparison-title">
                        <span aria-hidden="true">
                          {getFamilyMark(column.summary.family)}
                        </span>
                        <h5>{column.summary.family}</h5>
                      </div>
                      {column.rows.slice(0, 5).map((row) => (
                        <article key={row.code}>
                          <strong>{row.organ}</strong>
                          <p>{row.plain}</p>
                          <small>{row.state}</small>
                        </article>
                      ))}
                      {!column.rows.length && (
                        <p className="comparison-empty">
                          No field-ready clue has been reviewed into this family
                          yet.
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="pending-dossier">
              <span aria-hidden="true">◌</span>
              <div>
                <h4>This family is indexed, but its dossier is still empty.</h4>
                <p>
                  The current inventory carries {summary.plantCount} plant name
                  {summary.plantCount === 1 ? "" : "s"} in this family. Family
                  characters, exceptions, lookalikes, and citations remain in
                  the research queue.
                </p>
              </div>
            </div>
          )}
        </article>
      </div>
    </section>
  );
}

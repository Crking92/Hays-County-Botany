export type LearningVisual = {
  id: string;
  family: string;
  botanicalTerm: string;
  plainLabel: string;
  imageUrl: string;
  imageAlt: string;
  sourceUrl: string;
  source: string;
  specimen: string;
  lookFor: string;
  limit: string;
  rights: "private-study" | "source-linked";
  codes: string[];
  terms: string[];
};

type EvidenceLike = {
  family: string;
  code?: string;
  organ?: string;
  state?: string;
  text?: string;
};

const evidenceVisualOverrides: Record<
  string,
  Partial<
    Pick<
      LearningVisual,
      "botanicalTerm" | "plainLabel" | "lookFor" | "limit"
    >
  >
> = {
  "AST-SYNANTH": {
    botanicalTerm: "Disc florets · anther-tube location",
    plainLabel: "the tiny central florets that require a closer view",
    lookFor:
      "Start in the center of the head, where the tubular disc florets are packed together. Remove one mature floret and use a hand lens to see whether its anthers form a tube around the style.",
    limit:
      "This overview shows where to inspect, but the joined anthers themselves are not resolved. Do not record ‘yes’ from this photograph alone.",
  },
  "EUP-COLUMN": {
    botanicalTerm: "Three-part fruit · columella location",
    plainLabel: "the fruit center that may remain after the sections split",
    lookFor:
      "This young fruit shows the three rounded sections. Revisit a mature, opened fruit and look between the separated sections for the persistent central axis called the columella.",
    limit:
      "The columella is not exposed in this young fruit. Use this as a location guide, then confirm it on a mature opened capsule.",
  },
};

const stopWords = new Set([
  "and",
  "the",
  "with",
  "from",
  "into",
  "often",
  "usually",
  "flower",
  "flowers",
  "fruit",
  "leaf",
  "leaves",
  "stem",
  "plant",
  "structure",
]);

const normalizedTokens = (value: string) =>
  value
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter((token) => token.length > 3 && !stopWords.has(token))
    .map((token) =>
      token.endsWith("ies")
        ? `${token.slice(0, -3)}y`
        : token.endsWith("es")
          ? token.slice(0, -2)
          : token.endsWith("s")
            ? token.slice(0, -1)
            : token,
    );

const scoreVisual = (visual: LearningVisual, evidence: EvidenceLike) => {
  if (visual.family !== evidence.family) return -1;
  if (evidence.code && visual.codes.includes(evidence.code)) return 100;

  const haystack = [evidence.organ, evidence.state, evidence.text]
    .filter(Boolean)
    .join(" ")
    .toLocaleLowerCase();
  const haystackTokens = new Set(normalizedTokens(haystack));

  return visual.terms.reduce((score, term) => {
    const normalizedTerm = term.toLocaleLowerCase();
    if (haystack.includes(normalizedTerm)) return score + 12;
    const termTokens = normalizedTokens(term);
    const overlap = termTokens.filter((token) => haystackTokens.has(token)).length;
    return score + overlap * 3;
  }, 0);
};

export function visualForEvidence(
  visuals: LearningVisual[],
  evidence: EvidenceLike,
) {
  const ranked = visuals
    .map((visual, order) => ({
      visual,
      order,
      score: scoreVisual(visual, evidence),
    }))
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score || a.order - b.order);
  const best = ranked[0]?.visual;
  if (!best) return undefined;
  const override = evidence.code
    ? evidenceVisualOverrides[evidence.code]
    : undefined;
  return override ? { ...best, ...override } : best;
}

export function visualsForFamily(
  visuals: LearningVisual[],
  family: string,
  limit = 3,
) {
  const familyVisuals = visuals.filter((visual) => visual.family === family);
  const selected: LearningVisual[] = [];
  const usedTerms = new Set<string>();

  for (const visual of familyVisuals) {
    const term = visual.botanicalTerm.toLocaleLowerCase();
    if (usedTerms.has(term)) continue;
    selected.push(visual);
    usedTerms.add(term);
    if (selected.length === limit) break;
  }

  return selected;
}

export function visualForTerm(
  visuals: LearningVisual[],
  term: { term: string; plain?: string; fieldCue?: string },
) {
  const needle = term.term.toLocaleLowerCase();
  return visuals.find((visual) =>
    visual.terms.some((alias) => {
      const normalizedAlias = alias.toLocaleLowerCase();
      return (
        normalizedAlias === needle ||
        normalizedAlias.startsWith(`${needle} `) ||
        needle.startsWith(`${normalizedAlias} `)
      );
    }),
  );
}

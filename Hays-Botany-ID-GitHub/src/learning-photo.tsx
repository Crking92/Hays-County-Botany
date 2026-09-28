import type { LearningVisual } from "./learning-visuals";

type LearningPhotoProps = {
  visual: LearningVisual;
  compact?: boolean;
  priority?: boolean;
  showLimit?: boolean;
};

export default function LearningPhoto({
  visual,
  compact = false,
  priority = false,
  showLimit = false,
}: LearningPhotoProps) {
  return (
    <figure className={`learning-photo ${compact ? "compact" : ""}`}>
      <a
        className="learning-photo-frame"
        href={visual.sourceUrl}
        target="_blank"
        rel="noreferrer"
        aria-label={`Open the source for ${visual.botanicalTerm} shown on ${visual.specimen}`}
      >
        <img
          src={visual.imageUrl}
          alt={visual.imageAlt}
          loading={priority ? "eager" : "lazy"}
          decoding="async"
        />
        <span className="learning-term-chip">{visual.botanicalTerm}</span>
      </a>
      <figcaption>
        <div className="learning-photo-heading">
          <span>LOOK HERE</span>
          <strong>{visual.plainLabel}</strong>
        </div>
        <p>{visual.lookFor}</p>
        {showLimit && <p className="learning-photo-limit">Check: {visual.limit}</p>}
        <div className="learning-photo-source">
          <span>
            <i>{visual.specimen}</i> · {visual.source}
          </span>
          {visual.rights === "private-study" ? (
            <em>Private study · permission pending</em>
          ) : (
            <em>Source-linked teaching reference</em>
          )}
        </div>
      </figcaption>
    </figure>
  );
}

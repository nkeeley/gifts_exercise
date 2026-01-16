import { SegmentStatistics } from "@/types/api";

interface SegmentFilterProps {
  segments: SegmentStatistics[];
  selectedSegment: string | null;
  onSegmentChange: (segment: string | null) => void;
}

export const SegmentFilter = ({
  segments,
  selectedSegment,
  onSegmentChange,
}: SegmentFilterProps) => {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm font-medium text-muted-foreground mr-2">Filter by segment:</span>
      <button
        onClick={() => onSegmentChange(null)}
        className={`segment-filter-chip ${selectedSegment === null ? "active" : ""}`}
      >
        All Segments
      </button>
      {segments.map((seg) => (
        <button
          key={seg.segment}
          onClick={() => onSegmentChange(seg.segment)}
          className={`segment-filter-chip ${selectedSegment === seg.segment ? "active" : ""}`}
        >
          {seg.segment}
        </button>
      ))}
    </div>
  );
};

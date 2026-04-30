import type { IndicatorMeta } from "@/types/schema";

interface Props {
  meta: IndicatorMeta;
}

export default function SourceAttribution({ meta }: Props) {
  return (
    <p className="text-xs text-gray-500">
      Data:{" "}
      <a
        href={meta.methodology_url}
        target="_blank"
        rel="noopener noreferrer"
        className="underline hover:text-gray-700"
      >
        {meta.source}
      </a>
      . Sample data shown for demonstration.{" "}
      <a href="/methodology" className="underline hover:text-gray-700">
        Methodology
      </a>
    </p>
  );
}

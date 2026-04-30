"use client";

import { useMemo } from "react";
import { legendSteps, NO_DATA_COLOR } from "@/lib/colors";
import type { IndicatorMeta } from "@/types/schema";

interface Props {
  meta: IndicatorMeta;
  values: number[];
}

export default function Legend({ meta, values }: Props) {
  const steps = useMemo(() => legendSteps(meta, values), [meta, values]);

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
      <div className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
        {meta.name}
      </div>

      {/* Color gradient row */}
      <div className="flex items-center gap-1">
        {steps.map((step, i) => (
          <div
            key={i}
            className="flex-1 h-4 rounded-sm"
            style={{ backgroundColor: step.color }}
            aria-label={step.label}
          />
        ))}
      </div>

      {/* Labels */}
      <div className="flex justify-between text-xs text-gray-500">
        <span>{steps[0]?.label ?? ""}</span>
        <span>{steps[steps.length - 1]?.label ?? ""}</span>
      </div>

      {/* No data swatch */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <div
          className="h-3 w-5 rounded-sm border border-gray-300"
          style={{ backgroundColor: NO_DATA_COLOR }}
        />
        <span>No data</span>
      </div>

      {/* Source attribution */}
      <div className="text-xs text-gray-400">
        Source:{" "}
        <a
          href={meta.methodology_url}
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-gray-600"
        >
          {meta.source}
        </a>
      </div>
    </div>
  );
}

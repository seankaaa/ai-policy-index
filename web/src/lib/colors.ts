import {
  scaleSequential,
  scaleDiverging,
} from "d3-scale";
import {
  interpolateYlOrRd,
  interpolateRdBu,
} from "d3-scale-chromatic";
import type { IndicatorMeta } from "@/types/schema";

export const NO_DATA_COLOR = "#e5e7eb";
export const HOVER_DARKEN = 0.85;

export function buildColorScale(
  meta: IndicatorMeta,
  values: number[]
): (v: number | null | undefined) => string {
  if (!values.length) return () => NO_DATA_COLOR;

  const nonNull = values.filter((v) => v != null && isFinite(v));
  if (!nonNull.length) return () => NO_DATA_COLOR;

  const min = Math.min(...nonNull);
  const max = Math.max(...nonNull);

  if (meta.scale_type === "diverging") {
    const absMax = Math.max(Math.abs(min), Math.abs(max));
    const scale = scaleDiverging([-absMax, 0, absMax], interpolateRdBu);
    return (v) => (v == null || !isFinite(v) ? NO_DATA_COLOR : scale(v));
  }

  // Sequential heat map: yellow (low) → orange → red (high)
  const scale = scaleSequential([min, max], interpolateYlOrRd);
  return (v) => (v == null || !isFinite(v) ? NO_DATA_COLOR : scale(v));
}

/** 5-bucket legend steps for a sequential scale */
export function legendSteps(
  meta: IndicatorMeta,
  values: number[]
): Array<{ color: string; label: string }> {
  const nonNull = values.filter((v) => v != null && isFinite(v));
  if (!nonNull.length) return [];

  const min = Math.min(...nonNull);
  const max = Math.max(...nonNull);
  const n = 5;
  const colorFn = buildColorScale(meta, nonNull);

  return Array.from({ length: n }, (_, i) => {
    const v = min + (i / (n - 1)) * (max - min);
    return {
      color: colorFn(v),
      label: formatValue(v, meta.unit),
    };
  });
}

export function formatValue(v: number, unit: string): string {
  if (unit === "score_0_100") return v.toFixed(1);
  if (unit === "rank") return `#${Math.round(v)}`;
  if (unit === "count") return Math.round(v).toString();
  return v.toFixed(2);
}

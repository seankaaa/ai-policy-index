"use client";

import type { IndicatorMeta } from "@/types/schema";

interface Props {
  indicators: IndicatorMeta[];
  selected: string;
  onChange: (id: string) => void;
}

// Groups for display
const GROUPS: { label: string; prefixes: string[] }[] = [
  { label: "Government Readiness", prefixes: ["oxford_readiness", "girai", "oecd_ai"] },
  { label: "Policy Density", prefixes: ["iapp", "policy_count"] },
  { label: "Public Opinion", prefixes: ["ipsos", "wrp", "pew", "zhang", "kelley"] },
  { label: "Composite", prefixes: ["composite"] },
];

function groupIndicators(
  indicators: IndicatorMeta[]
): Array<{ label: string; items: IndicatorMeta[] }> {
  const assigned = new Set<string>();
  const groups: Array<{ label: string; items: IndicatorMeta[] }> = [];

  for (const group of GROUPS) {
    const items = indicators.filter((ind) => {
      const matched = group.prefixes.some((p) => ind.id.startsWith(p));
      if (matched) assigned.add(ind.id);
      return matched;
    });
    if (items.length > 0) groups.push({ label: group.label, items });
  }

  // Ungrouped
  const other = indicators.filter((ind) => !assigned.has(ind.id));
  if (other.length > 0) groups.push({ label: "Other", items: other });

  return groups;
}

export default function IndicatorPicker({ indicators, selected, onChange }: Props) {
  const groups = groupIndicators(indicators);

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor="indicator-select" className="text-xs font-medium text-gray-600">
        Indicator
      </label>
      <select
        id="indicator-select"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {groups.map((group) => (
          <optgroup key={group.label} label={group.label}>
            {group.items.map((ind) => (
              <option key={ind.id} value={ind.id}>
                {ind.name}
                {ind.coverage_count > 0 ? ` (${ind.coverage_count} countries)` : ""}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}

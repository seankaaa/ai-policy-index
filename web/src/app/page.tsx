"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import type { IndicatorRow, MetaFile, IndicatorMeta } from "@/types/schema";
import {
  loadIndicators,
  loadMeta,
  buildValueMap,
  indicatorYears,
  indicatorValues,
} from "@/lib/data";
import IndicatorPicker from "@/components/IndicatorPicker";
import YearSlider from "@/components/YearSlider";
import SourceAttribution from "@/components/SourceAttribution";
import Legend from "@/components/Legend";

// WorldMap uses d3-geo which requires a browser; dynamically import to skip SSR
const WorldMap = dynamic(() => import("@/components/WorldMap"), { ssr: false });

export default function HomePage() {
  const [indicators, setIndicators] = useState<IndicatorRow[]>([]);
  const [meta, setMeta] = useState<MetaFile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [selectedIndicatorId, setSelectedIndicatorId] = useState<string>("");
  const [selectedYear, setSelectedYear] = useState<number>(2023);

  useEffect(() => {
    Promise.all([loadIndicators(), loadMeta()])
      .then(([rows, metaFile]) => {
        setIndicators(rows);
        setMeta(metaFile);
        if (metaFile.indicators.length > 0) {
          setSelectedIndicatorId(metaFile.indicators[0].id);
        }
        const years = metaFile.years;
        if (years.length > 0) setSelectedYear(years[years.length - 1]);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const currentMeta: IndicatorMeta | null = useMemo(
    () => meta?.indicators.find((m) => m.id === selectedIndicatorId) ?? null,
    [meta, selectedIndicatorId]
  );

  const availableYears = useMemo(
    () => (selectedIndicatorId ? indicatorYears(indicators, selectedIndicatorId) : []),
    [indicators, selectedIndicatorId]
  );

  const valueMap = useMemo(
    () =>
      selectedIndicatorId
        ? buildValueMap(indicators, selectedIndicatorId, selectedYear)
        : new Map<string, number>(),
    [indicators, selectedIndicatorId, selectedYear]
  );

  const allValues = useMemo(
    () => (selectedIndicatorId ? indicatorValues(indicators, selectedIndicatorId) : []),
    [indicators, selectedIndicatorId]
  );

  // If selected year not available for new indicator, snap to closest
  useEffect(() => {
    if (availableYears.length > 0 && !availableYears.includes(selectedYear)) {
      setSelectedYear(availableYears[availableYears.length - 1]);
    }
  }, [availableYears, selectedYear]);

  if (loading) {
    return (
      <main className="flex h-screen items-center justify-center">
        <div className="text-gray-500 text-sm animate-pulse">Loading map data…</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex h-screen items-center justify-center">
        <div className="text-red-600 text-sm">Error: {error}</div>
      </main>
    );
  }

  return (
    <main className="flex h-screen flex-col overflow-hidden bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3 shadow-sm">
        <div>
          <h1 className="text-lg font-bold text-gray-900">AI Policy Index</h1>
          <p className="text-xs text-gray-500">
            Global AI governance, readiness &amp; public opinion
          </p>
        </div>
        <nav className="flex gap-4 text-sm text-gray-600">
          <a href="/compare" className="hover:text-gray-900">Compare</a>
          <a href="/methodology" className="hover:text-gray-900">Methodology</a>
          <a
            href="https://github.com/seankaaa/ai-policy-index"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-gray-900"
          >
            GitHub
          </a>
        </nav>
      </header>

      {/* Controls bar */}
      <div className="flex flex-wrap items-end gap-6 border-b border-gray-200 bg-white px-6 py-3">
        {meta && (
          <IndicatorPicker
            indicators={meta.indicators}
            selected={selectedIndicatorId}
            onChange={setSelectedIndicatorId}
          />
        )}
        <div className="w-48">
          <YearSlider
            years={availableYears}
            value={selectedYear}
            onChange={setSelectedYear}
          />
        </div>
        {currentMeta && (
          <p className="text-xs text-gray-500 max-w-sm hidden lg:block">
            {currentMeta.description}
          </p>
        )}
      </div>

      {/* Map + legend */}
      <div className="relative flex-1 overflow-hidden">
        {currentMeta && (
          <WorldMap
            valueMap={valueMap}
            meta={currentMeta}
            year={selectedYear}
          />
        )}

        {/* Legend overlay */}
        {currentMeta && (
          <div className="absolute bottom-4 left-4 w-52">
            <Legend meta={currentMeta} values={allValues} />
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white px-6 py-2">
        {currentMeta && <SourceAttribution meta={currentMeta} />}
      </footer>
    </main>
  );
}

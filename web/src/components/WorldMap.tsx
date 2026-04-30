"use client";

import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import * as topojson from "topojson-client";
import { geoEqualEarth, geoPath } from "d3-geo";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { FeatureCollection, Geometry } from "geojson";
import type { IndicatorMeta } from "@/types/schema";
import { numericToAlpha3, getCountryName } from "@/lib/countries";
import {
  buildColorScale,
  NO_DATA_COLOR,
  formatValue,
} from "@/lib/colors";
import { useRouter } from "next/navigation";

interface Props {
  valueMap: Map<string, number>;
  meta: IndicatorMeta;
  year: number;
  onCountryHover?: (iso3: string | null) => void;
}

interface TooltipState {
  x: number;
  y: number;
  iso3: string;
  value: number | null;
}

// Antarctica numeric id
const ANTARCTICA_ID = "010";

export default function WorldMap({ valueMap, meta, year, onCountryHover }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 960, height: 500 });
  const [topology, setTopology] = useState<Topology | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const router = useRouter();

  // Responsive resize
  useEffect(() => {
    const obs = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        const w = entry.contentRect.width;
        setDimensions({ width: w, height: Math.round(w * 0.52) });
      }
    });
    if (containerRef.current) obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Load TopoJSON once
  useEffect(() => {
    fetch("/geo/world-110m.json")
      .then((r) => r.json())
      .then(setTopology)
      .catch(console.error);
  }, []);

  const colorScale = useMemo(
    () => buildColorScale(meta, [...valueMap.values()]),
    [meta, valueMap]
  );

  const { paths } = useMemo(() => {
    if (!topology) return { paths: [] };

    const { width, height } = dimensions;
    const projection = geoEqualEarth().fitSize([width, height], {
      type: "Sphere",
    });
    const pathGen = geoPath(projection);

    const countries = topojson.feature(
      topology,
      (topology as unknown as { objects: { countries: GeometryCollection } })
        .objects.countries
    ) as unknown as FeatureCollection<Geometry, { name?: string }>;

    const paths = countries.features
      .filter((f) => {
        const id = String(f.id).padStart(3, "0");
        return id !== ANTARCTICA_ID;
      })
      .map((f) => {
        const numericId = String(f.id).padStart(3, "0");
        const iso3 = numericToAlpha3[numericId] ?? null;
        const value = iso3 ? (valueMap.get(iso3) ?? null) : null;
        const fill = colorScale(value);
        const d = pathGen(f) ?? "";
        return { iso3, numericId, value, fill, d };
      })
      .filter((p) => p.d);

    return { paths };
  }, [topology, dimensions, valueMap, colorScale]);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<SVGPathElement>, iso3: string | null, value: number | null) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect || !iso3) return;
      setTooltip({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        iso3,
        value,
      });
      onCountryHover?.(iso3);
    },
    [onCountryHover]
  );

  const handleMouseLeave = useCallback(() => {
    setTooltip(null);
    onCountryHover?.(null);
  }, [onCountryHover]);

  const handleClick = useCallback(
    (iso3: string | null) => {
      if (iso3) router.push(`/country/${iso3}`);
    },
    [router]
  );

  return (
    <div ref={containerRef} className="relative w-full select-none">
      <svg
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        width="100%"
        style={{ display: "block" }}
        aria-label="World map showing AI policy indicators by country"
      >
        {/* Ocean background */}
        <rect width={dimensions.width} height={dimensions.height} fill="#dbeafe" />

        {paths.map((p) => (
          <path
            key={p.numericId}
            d={p.d}
            fill={p.fill}
            stroke="#fff"
            strokeWidth={0.4}
            tabIndex={p.iso3 ? 0 : -1}
            role={p.iso3 ? "button" : undefined}
            aria-label={
              p.iso3
                ? `${getCountryName(p.iso3)}: ${
                    p.value != null
                      ? formatValue(p.value, meta.unit)
                      : "no data"
                  }`
                : undefined
            }
            style={{ cursor: p.iso3 ? "pointer" : "default" }}
            onMouseMove={(e) => handleMouseMove(e, p.iso3, p.value)}
            onMouseLeave={handleMouseLeave}
            onClick={() => handleClick(p.iso3)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") handleClick(p.iso3);
            }}
          />
        ))}
      </svg>

      {tooltip && (
        <div
          className="pointer-events-none absolute z-10 rounded-md bg-gray-900 px-3 py-2 text-sm text-white shadow-lg"
          style={{
            left: tooltip.x + 14,
            top: tooltip.y - 10,
            transform: tooltip.x > dimensions.width * 0.7 ? "translateX(-100%)" : undefined,
          }}
        >
          <div className="font-semibold">{getCountryName(tooltip.iso3)}</div>
          <div className="text-gray-300 text-xs">{tooltip.iso3}</div>
          <div className="mt-1">
            {tooltip.value != null ? (
              <span>
                {formatValue(tooltip.value, meta.unit)}{" "}
                <span className="text-gray-400">({meta.unit})</span>
              </span>
            ) : (
              <span className="text-gray-400">No data</span>
            )}
          </div>
          <div className="mt-1 text-xs text-gray-400">
            {meta.source} · {year}
          </div>
        </div>
      )}
    </div>
  );
}

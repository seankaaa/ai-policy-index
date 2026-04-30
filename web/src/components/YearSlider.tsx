"use client";

interface Props {
  years: number[];
  value: number;
  onChange: (year: number) => void;
}

export default function YearSlider({ years, value, onChange }: Props) {
  if (years.length <= 1) {
    return (
      <div className="flex flex-col gap-1">
        <span className="text-xs font-medium text-gray-600">Year</span>
        <span className="text-sm font-semibold text-gray-800">{value}</span>
      </div>
    );
  }

  const min = years[0];
  const max = years[years.length - 1];

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor="year-slider" className="text-xs font-medium text-gray-600">
        Year: <span className="font-semibold text-gray-800">{value}</span>
      </label>
      <input
        id="year-slider"
        type="range"
        min={min}
        max={max}
        step={1}
        value={value}
        onChange={(e) => {
          const v = Number(e.target.value);
          // Snap to nearest available year
          const closest = years.reduce((a, b) =>
            Math.abs(b - v) < Math.abs(a - v) ? b : a
          );
          onChange(closest);
        }}
        className="w-full accent-blue-600"
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        aria-label={`Year: ${value}`}
      />
      <div className="flex justify-between text-xs text-gray-400">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

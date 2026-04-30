import type {
  IndicatorRow,
  PolicyRow,
  PublicOpinionRow,
  MetaFile,
} from "@/types/schema";
import { isValidIso3 } from "@/lib/countries";

// ---------- loaders ----------

export async function loadMeta(): Promise<MetaFile> {
  const res = await fetch("/data/meta.json");
  if (!res.ok) throw new Error(`Failed to load meta.json: ${res.status}`);
  return res.json();
}

export async function loadIndicators(): Promise<IndicatorRow[]> {
  const res = await fetch("/data/indicators.json");
  if (!res.ok) throw new Error(`Failed to load indicators.json: ${res.status}`);
  const data = await res.json();
  validateIndicators(data);
  return data;
}

export async function loadPolicies(): Promise<PolicyRow[]> {
  const res = await fetch("/data/policies.json");
  if (!res.ok) throw new Error(`Failed to load policies.json: ${res.status}`);
  const data = await res.json();
  validatePolicies(data);
  return data;
}

export async function loadOpinion(): Promise<PublicOpinionRow[]> {
  const res = await fetch("/data/opinion.json");
  if (!res.ok) throw new Error(`Failed to load opinion.json: ${res.status}`);
  const data = await res.json();
  validateOpinion(data);
  return data;
}

// ---------- validators ----------

export function validateIndicators(data: unknown): asserts data is IndicatorRow[] {
  if (!Array.isArray(data)) throw new Error("indicators.json must be an array");
  for (const row of data as IndicatorRow[]) {
    if (!isValidIso3(row.country_iso3))
      throw new Error(`Invalid iso3: ${row.country_iso3}`);
    if (row.value == null)
      throw new Error(`Null value in indicators for ${row.country_iso3}/${row.indicator_id}`);
    if (row.year < 2015 || row.year > 2026)
      throw new Error(`Implausible year ${row.year} in indicators`);
  }
}

export function validatePolicies(data: unknown): asserts data is PolicyRow[] {
  if (!Array.isArray(data)) throw new Error("policies.json must be an array");
  for (const row of data as PolicyRow[]) {
    if (!isValidIso3(row.country_iso3))
      throw new Error(`Invalid iso3: ${row.country_iso3}`);
    if (!row.policy_id) throw new Error("Missing policy_id");
    if (!row.policy_name) throw new Error("Missing policy_name");
  }
}

export function validateOpinion(data: unknown): asserts data is PublicOpinionRow[] {
  if (!Array.isArray(data)) throw new Error("opinion.json must be an array");
  for (const row of data as PublicOpinionRow[]) {
    if (!isValidIso3(row.country_iso3))
      throw new Error(`Invalid iso3: ${row.country_iso3}`);
    if (row.value == null)
      throw new Error(`Null value in opinion for ${row.country_iso3}/${row.question_id}`);
    if (row.year < 2015 || row.year > 2026)
      throw new Error(`Implausible year ${row.year} in opinion`);
  }
}

// ---------- helpers ----------

/** Build a country → value lookup for a specific indicator + year */
export function buildValueMap(
  rows: IndicatorRow[],
  indicatorId: string,
  year: number
): Map<string, number> {
  const map = new Map<string, number>();
  for (const row of rows) {
    if (row.indicator_id === indicatorId && row.year === year) {
      map.set(row.country_iso3, row.value);
    }
  }
  return map;
}

/** Get all values for a given indicator across all years/countries */
export function indicatorValues(
  rows: IndicatorRow[],
  indicatorId: string
): number[] {
  return rows
    .filter((r) => r.indicator_id === indicatorId)
    .map((r) => r.value);
}

/** Available years for a given indicator */
export function indicatorYears(
  rows: IndicatorRow[],
  indicatorId: string
): number[] {
  return [
    ...new Set(
      rows.filter((r) => r.indicator_id === indicatorId).map((r) => r.year)
    ),
  ].sort();
}

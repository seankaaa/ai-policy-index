/**
 * build-data.ts — Convert parquet files from ../data/processed/ to static JSON
 * in public/data/. Falls back to public/data/sample/ if processed data is absent.
 *
 * Run: npx tsx scripts/build-data.ts
 */

import fs from "fs";
import path from "path";

const PROCESSED_DIR = path.resolve(__dirname, "../../data/processed");
const SAMPLE_DIR = path.resolve(__dirname, "../public/data/sample");
const OUT_DIR = path.resolve(__dirname, "../public/data");
const MAX_JSON_BYTES = 5 * 1024 * 1024; // 5 MB warning threshold

function warn(msg: string) {
  console.warn(`[build-data] WARN: ${msg}`);
}
function info(msg: string) {
  console.log(`[build-data] ${msg}`);
}
function fail(msg: string): never {
  console.error(`[build-data] ERROR: ${msg}`);
  process.exit(1);
}

function copySample() {
  info("Falling back to sample data from public/data/sample/");
  for (const file of fs.readdirSync(SAMPLE_DIR)) {
    const src = path.join(SAMPLE_DIR, file);
    const dst = path.join(OUT_DIR, file);
    fs.copyFileSync(src, dst);
    info(`  Copied sample/${file}`);
  }
}

async function readParquet(filePath: string): Promise<unknown[]> {
  try {
    const { tableFromIPC, RecordBatchReader } = await import("apache-arrow");
    const buf = fs.readFileSync(filePath);
    const table = tableFromIPC(buf);
    return table.toArray().map((r: unknown) => {
      const row = r as Record<string, unknown>;
      const obj: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(row)) {
        // Convert BigInt to number, nulls stay null
        obj[k] = typeof v === "bigint" ? Number(v) : v;
      }
      return obj;
    });
  } catch (e) {
    warn(`Could not read parquet ${filePath}: ${e}`);
    return [];
  }
}

function writeJson(name: string, data: unknown[]) {
  const outPath = path.join(OUT_DIR, name);
  const json = JSON.stringify(data);
  const bytes = Buffer.byteLength(json, "utf8");
  if (bytes > MAX_JSON_BYTES) {
    warn(
      `${name} is ${(bytes / 1024 / 1024).toFixed(1)} MB — consider DuckDB-WASM to query parquet directly in the browser`
    );
  }
  fs.writeFileSync(outPath, json);
  info(`  Wrote ${name} (${data.length} rows, ${(bytes / 1024).toFixed(0)} KB)`);
}

function buildMeta(indicators: unknown[], policies: unknown[], opinion: unknown[]) {
  const rows = indicators as Array<{
    indicator_id: string;
    indicator_name: string;
    unit: string;
    source: string;
    methodology_url: string;
    year: number;
    country_iso3: string;
  }>;

  const byId = new Map<
    string,
    { name: string; unit: string; source: string; url: string; years: Set<number>; countries: Set<string> }
  >();

  for (const r of rows) {
    if (!byId.has(r.indicator_id)) {
      byId.set(r.indicator_id, {
        name: r.indicator_name,
        unit: r.unit,
        source: r.source,
        url: r.methodology_url,
        years: new Set(),
        countries: new Set(),
      });
    }
    const entry = byId.get(r.indicator_id)!;
    entry.years.add(r.year);
    entry.countries.add(r.country_iso3);
  }

  const indMeta = [...byId.entries()].map(([id, v]) => ({
    id,
    name: v.name,
    description: `${v.name} from ${v.source}.`,
    unit: v.unit,
    source: v.source,
    methodology_url: v.url,
    years_available: [...v.years].sort(),
    coverage_count: v.countries.size,
    scale_type: v.unit === "rank" ? "diverging" : "sequential",
  }));

  const allYears = [...new Set(rows.map((r) => r.year))].sort();
  const allSources = [...new Set(rows.map((r) => r.source))];

  const meta = {
    generated_at: new Date().toISOString(),
    indicators: indMeta,
    years: allYears,
    sources: allSources,
  };

  const outPath = path.join(OUT_DIR, "meta.json");
  fs.writeFileSync(outPath, JSON.stringify(meta, null, 2));
  info(`  Wrote meta.json (${indMeta.length} indicators)`);
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  if (!fs.existsSync(PROCESSED_DIR)) {
    warn(
      `../data/processed/ not found — run the Python pipeline first, or place parquets there manually.`
    );
    copySample();
    return;
  }

  const indicatorsPath = path.join(PROCESSED_DIR, "indicators.parquet");
  const policiesPath = path.join(PROCESSED_DIR, "policies.parquet");
  const opinionPath = path.join(PROCESSED_DIR, "public_opinion.parquet");

  const missing = [indicatorsPath, policiesPath, opinionPath].filter(
    (p) => !fs.existsSync(p)
  );
  if (missing.length > 0) {
    warn(`Missing parquet files: ${missing.join(", ")}`);
    copySample();
    return;
  }

  info("Reading parquet files…");
  const [indicators, policies, opinion] = await Promise.all([
    readParquet(indicatorsPath),
    readParquet(policiesPath),
    readParquet(opinionPath),
  ]);

  // Basic validation
  if (!Array.isArray(indicators))
    fail("indicators.parquet did not produce an array");

  for (const row of indicators as Array<{ country_iso3?: unknown; year?: unknown }>) {
    if (typeof row.country_iso3 !== "string" || row.country_iso3.length !== 3)
      fail(`Invalid country_iso3: ${JSON.stringify(row.country_iso3)}`);
    const y = Number(row.year);
    if (y < 2015 || y > 2026)
      fail(`Year out of range: ${y}`);
  }

  info(`Validated ${indicators.length} indicator rows`);

  writeJson("indicators.json", indicators);
  writeJson("policies.json", policies);
  writeJson("opinion.json", opinion);
  buildMeta(indicators, policies, opinion);

  info("Done.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

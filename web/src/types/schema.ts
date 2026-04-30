// Mirrors ../src/common/schema.py — keep in sync

export type PolicyType =
  | "strategy"
  | "legislation"
  | "regulation"
  | "guideline"
  | "principle"
  | "funding"
  | "other";

export type PolicyStatus = "proposed" | "enacted" | "enforced" | "superseded";

export interface PolicyRow {
  country_iso3: string;
  country_name: string;
  policy_id: string;
  policy_name: string;
  policy_type: PolicyType;
  policy_status: PolicyStatus;
  target_sector: string | null;
  risk_focus: string[];
  enacted_date: string | null;
  source_url: string;
  source: string;
  retrieved_at: string;
}

export interface IndicatorRow {
  country_iso3: string;
  country_name?: string;
  year: number;
  indicator_id: string;
  indicator_name: string;
  value: number;
  unit: string;
  source: string;
  methodology_url: string;
  retrieved_at: string;
}

export interface PublicOpinionRow {
  country_iso3: string;
  year: number;
  survey: string;
  question_id: string;
  question_text: string;
  response_category: string;
  value: number;
  n: number | null;
  weighted: boolean;
  source_url: string;
  retrieved_at: string;
}

export interface IndicatorMeta {
  id: string;
  name: string;
  description: string;
  unit: string;
  source: string;
  methodology_url: string;
  years_available: number[];
  coverage_count: number;
  scale_type: "sequential" | "diverging";
}

export interface MetaFile {
  generated_at: string;
  indicators: IndicatorMeta[];
  years: number[];
  sources: string[];
}

// Map from ISO numeric (as string) → ISO alpha-3
// Used to join world-atlas TopoJSON (which uses numeric codes) with our data
export type NumericToAlpha3 = Record<string, string>;

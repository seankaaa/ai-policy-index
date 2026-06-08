import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Policy Brief — AI Policy Index",
  description:
    "The Fragmentation of AI Governance Data and the Case for Open, Joinable Infrastructure. Evidence from a 14-source, 195-country consolidation effort.",
};

const NAVY = "#1f3a5f";

const STATS = [
  { value: "195", label: "Countries" },
  { value: "14", label: "Sources" },
  { value: "18", label: "Indicators" },
  { value: "2023–25", label: "Years" },
];

const KEY_FINDINGS = [
  "Authoritative AI-governance datasets are published in incompatible formats with inconsistent country identifiers, making cross-source comparison costly and error-prone.",
  "A single open pipeline can consolidate 14 sources into a 195-country, 18-indicator panel for 2023–2025, demonstrating that the bottleneck is institutional rather than technical.",
  "Government readiness scores correlate weakly with public trust; private investment appears to lead, not lag, national policy activity.",
  "Sub-Saharan Africa is missing from 9 of 18 indicators, reflecting persistent under-coverage in global AI-governance data.",
  "Five recommendations for producers, funders, statistical agencies, and the research community follow.",
];

const SOURCE_TABLE = [
  ["Oxford Insights GAIRI", "Gated CSV", "Mid-series taxonomy change"],
  ["Stanford HAI 2026", "Narrative PDF", "No machine-readable release"],
  ["Ipsos AI Monitor 2024", "Press toplines", "32-country subset"],
  ["OECD AI Policy Observatory", "JS portal", "Requires headless scrape"],
  ["UNESCO RAM", "Country reports", "Heterogeneous structure"],
];

const FINDINGS = [
  {
    lead: "Readiness does not track public trust.",
    body: "Across the 32 countries with both Oxford readiness scores and Ipsos opinion data, rank correlation with public trust is r = −0.18.",
  },
  {
    lead: "Law adoption is concentrated.",
    body: "Roughly 71 percent of cumulative AI laws across 2023–2025 sit in five jurisdictions.",
  },
  {
    lead: "Investment leads policy.",
    body: "Private investment predicts next-year national law count (β = 0.41 in a lag-1 OLS specification).",
  },
  {
    lead: "Equatorial under-coverage persists.",
    body: "Sub-Saharan Africa is missing from 9 of 18 indicators in the consolidated panel.",
  },
  {
    lead: "Excitement exceeds nervousness.",
    body: "In 19 of the 32 countries surveyed by Ipsos, respondents express more excitement than nervousness about AI.",
  },
];

const RECOMMENDATIONS = [
  {
    lead: "Producers should ship a CSV companion.",
    body: "Every governance index should release a machine-readable file keyed on ISO-3 plus year, under an open licence such as CC BY 4.0. The marginal cost is hours per release; the externality of not releasing is days of duplicated extraction effort across every downstream user.",
  },
  {
    lead: "Funders should fund infrastructure, not only analyses.",
    body: "A modest pooled fund, on the order of a few hundred thousand US dollars per year, dedicated to open extractors and consolidation pipelines would unlock more comparative research than an equivalent single-analysis grant.",
  },
  {
    lead: "Statistical agencies should adopt ISO-3 plus year as the minimum key.",
    body: "Country names and regional groupings should be carried as attributes, not used as primary keys. This is a low-cost change for producers and a high-value one for downstream users.",
  },
  {
    lead: "The research community should cite the data layer.",
    body: "Comparative papers should cite the consolidated dataset and version, not only the upstream sources, so that replication targets a fixed snapshot rather than a moving set of producer releases.",
  },
  {
    lead: "The Index should federate, not centralise.",
    body: "Add the next ten sources as independent modules under monthly continuous-integration auto-refresh, keeping the project forkable and resistant to single-maintainer failure.",
  },
];

const REFERENCES = [
  "Oxford Insights. Government AI Readiness Index 2023, 2024, 2025. Oxford Insights, London.",
  "Stanford HAI. Artificial Intelligence Index Report 2026. Stanford Institute for Human-Centered AI.",
  "Ipsos. AI Monitor 2024: A 32-country Ipsos Global Advisor Survey. Ipsos Public Affairs.",
  "OECD. AI Policy Observatory: Live Repository of AI Strategies and Policies. Paris: OECD.",
  "UNESCO. Readiness Assessment Methodology (RAM) Country Reports. UNESCO, Paris.",
  "European Commission. Special Eurobarometer on AI, 2024.",
  "Lloyd’s Register Foundation. World Risk Poll, 2023.",
  "Pew Research Center. Public Views of AI, 2024.",
  "Natural Earth. 1:50m Admin 0 Countries. Public domain.",
];

const NOTES = [
  "Repository: github.com/seankaaa/ai-policy-index. Live dashboard: ai-policy-index.vercel.app. Licence: open source.",
  "Static JSON release; no API server. Distribution is via the project’s public directory.",
  "Country tables in the Stanford HAI source are hand-extracted from narrative figures.",
  "Pipeline graph: fetch → normalize → validate → merge → serve.",
  "Federated module structure: each source is independently runnable via the shared CLI.",
  "Total source code: approximately 6,400 lines across pipeline and front-end.",
];

function SectionHeading({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <h2 className="mt-10 text-lg font-semibold text-gray-900" style={{ color: NAVY }}>
      <span className="text-gray-400">{n}.</span> {children}
    </h2>
  );
}

export default function BriefPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <a href="/" className="text-sm text-blue-600 hover:underline">
        ← Back to map
      </a>

      {/* Title block */}
      <header className="mt-4 border-t-4 pt-5" style={{ borderColor: NAVY }}>
        <p
          className="text-xs font-semibold uppercase tracking-[0.18em]"
          style={{ color: NAVY }}
        >
          Policy Brief · Methodology and Recommendations
        </p>
        <h1 className="mt-3 text-2xl font-bold leading-snug text-gray-900">
          The Fragmentation of AI Governance Data and the Case for Open, Joinable
          Infrastructure
        </h1>
        <p className="mt-2 text-sm italic text-gray-600">
          Evidence from a 14-source, 195-country consolidation effort, and what it
          implies for funders, statistical agencies, and the research community.
        </p>
        <p className="mt-3 text-xs text-gray-500">
          Anna Siamionava ·{" "}
          <a href="mailto:annase2004@gmail.com" className="text-blue-600 hover:underline">
            annase2004@gmail.com
          </a>{" "}
          ·{" "}
          <a
            href="https://github.com/seankaaa/ai-policy-index"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            github.com/seankaaa/ai-policy-index
          </a>
        </p>
      </header>

      {/* Stat cards */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {STATS.map((s) => (
          <div
            key={s.label}
            className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-4 text-center"
          >
            <div className="text-2xl font-bold" style={{ color: NAVY }}>
              {s.value}
            </div>
            <div className="mt-1 text-[11px] font-medium uppercase tracking-wide text-gray-500">
              {s.label}
            </div>
          </div>
        ))}
      </div>

      {/* Key findings callout */}
      <div
        className="mt-6 rounded-lg border-t-4 bg-[#f4f1ea] p-5"
        style={{ borderColor: NAVY }}
      >
        <h2
          className="text-xs font-semibold uppercase tracking-[0.18em]"
          style={{ color: NAVY }}
        >
          Key Findings
        </h2>
        <ul className="mt-3 space-y-2 text-sm text-gray-700">
          {KEY_FINDINGS.map((f, i) => (
            <li key={i} className="flex gap-2">
              <span style={{ color: NAVY }}>▪</span>
              <span>{f}</span>
            </li>
          ))}
        </ul>
      </div>

      <article className="text-sm leading-relaxed text-gray-700">
        <SectionHeading n={1}>Executive Summary</SectionHeading>
        <p className="mt-3">
          Comparative AI-governance research is bottlenecked by data fragmentation.
          Authoritative producers, including Oxford Insights, Stanford HAI, Ipsos, the
          OECD, and UNESCO, publish in incompatible formats and use inconsistent country
          identifiers, so no single producer ships a file that another producer’s data can
          be merged against without manual reconciliation. The result is a comparative
          literature constrained less by analytic capacity than by extraction overhead.
        </p>
        <p className="mt-3">
          This brief reports on the AI Policy Index, an open-source consolidation of 14
          such sources into a single ISO-3166-keyed panel covering 195 countries and 18
          indicators across 2023–2025, distributed as static JSON under an open licence.
          The exercise demonstrates that cross-source consolidation is feasible at
          single-developer scale and that the principal obstacle to comparative
          AI-governance research is institutional, not technical.
        </p>
        <p className="mt-3">
          Five recommendations follow, addressed to data producers, funders, statistical
          agencies, the research community, and the Index project itself.
        </p>

        <SectionHeading n={2}>The Problem: Fragmentation by Default</SectionHeading>
        <p className="mt-3">
          Each major producer of AI-governance data optimises for its own publication
          channel. Oxford Insights publishes the Government AI Readiness Index as an annual
          launch report with a gated CSV companion. Stanford HAI’s AI Index Report is a
          300-page narrative volume from which country-level tables must be hand-extracted.
          Ipsos releases a 32-country AI Monitor in press-formatted toplines. The OECD AI
          Policy Observatory presents an interactive portal whose underlying data resists
          straightforward download.
        </p>
        <p className="mt-3">Three frictions follow from these choices.</p>
        <h3 className="mt-4 font-semibold text-gray-900">Identifier drift</h3>
        <p className="mt-1">
          Country names appear as “Korea, Rep.”, “South Korea”, and “Republic of Korea”
          across three sources tested. Without a canonical key, even straightforward joins
          require a reconciliation step that producers do not provide.
        </p>
        <h3 className="mt-4 font-semibold text-gray-900">Format tax</h3>
        <p className="mt-1">
          In the consolidation pipeline reported here, roughly 62 percent of effort was
          absorbed by extraction and identifier reconciliation rather than analysis, a
          share that should be considered indicative of single-developer projects rather
          than precisely measured.
        </p>
        <h3 className="mt-4 font-semibold text-gray-900">Comparative blindness</h3>
        <p className="mt-1">
          Cross-source questions, such as whether high-readiness states have high public
          trust, or whether private investment leads or lags national policy, cannot be
          answered inside any single dataset. They require a joinable panel that no producer
          ships.
        </p>

        <SectionHeading n={3}>Approach</SectionHeading>
        <p className="mt-3">
          The Index treats consolidation as an engineering problem with an explicit schema.
          Each source is wrapped in a Python module that emits a standard tuple of (iso3,
          year, indicator, value, source, note), and per-source Parquet caches sit between
          fetch and merge so a single source revision does not require re-running the full
          pipeline. The merge produces three long tables (indicators, policies,
          public_opinion) plus a wide country-year panel suitable for regression. The
          front-end is a static Next.js site; there is no database and no API server, and
          distribution is via the project’s public directory.
        </p>
        <p className="mt-3">
          Source modules are independently runnable through a shared command-line
          interface, which keeps the project federated rather than centralised: a
          contributor can add a fifteenth source without touching the existing fourteen.
        </p>
        <h3 className="mt-4 font-semibold text-gray-900">Source landscape</h3>
        <p className="mt-1">
          The five most heavily used sources, and the friction each presents, are
          summarised below.
        </p>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr style={{ backgroundColor: NAVY }} className="text-white">
                <th className="px-3 py-2 font-semibold">Source</th>
                <th className="px-3 py-2 font-semibold">Format</th>
                <th className="px-3 py-2 font-semibold">Friction</th>
              </tr>
            </thead>
            <tbody>
              {SOURCE_TABLE.map((row) => (
                <tr key={row[0]} className="border-b border-gray-200">
                  <td className="px-3 py-2 font-medium text-gray-900">{row[0]}</td>
                  <td className="px-3 py-2 text-gray-700">{row[1]}</td>
                  <td className="px-3 py-2 text-gray-700">{row[2]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <SectionHeading n={4}>Findings</SectionHeading>
        <p className="mt-3">
          The findings below are computed against the panel as of the cited project
          version. They are intended as indicative results from a single-developer
          consolidation rather than as audited statistics; values will drift as upstream
          sources update, and replication should target a fixed snapshot.
        </p>
        <ul className="mt-3 space-y-3">
          {FINDINGS.map((f) => (
            <li key={f.lead}>
              <span className="font-semibold text-gray-900">{f.lead}</span> {f.body}
            </li>
          ))}
        </ul>

        <SectionHeading n={5}>Methodology and Limitations</SectionHeading>
        <p className="mt-3">
          Cross-source consolidation at single-developer scale required approximately 180
          hours of work, of which an estimated 70 percent was extraction and identifier
          reconciliation. These figures are author estimates rather than logged effort and
          should be read as order-of-magnitude indicators.
        </p>
        <h3 className="mt-4 font-semibold text-gray-900">Oxford 2025 re-derivation</h3>
        <p className="mt-1">
          Where a source revises its taxonomy mid-series, as Oxford did in 2025 when it
          moved from three to six pillars, overall scores are re-derived via dimension-count
          weighted averaging and validated against the 2024 baseline at a mean absolute
          error of approximately 1.4 points. Users are encouraged to filter to
          approximation_flag = false when strict comparisons are required.
        </p>
        <h3 className="mt-4 font-semibold text-gray-900">Limitations</h3>
        <p className="mt-1">
          The panel is unbalanced: 32 countries for opinion data, 15 for investment, and 14
          G20 jurisdictions for laws. The 1.4-point Oxford approximation error is small
          relative to inter-country variance but is non-trivial for borderline rankings.
          Where producers disagree on the status of disputed territories, the Index
          documents the disagreement at producer level rather than attempting to resolve it.
        </p>
        <h3 className="mt-4 font-semibold text-gray-900">A note on figures</h3>
        <p className="mt-1">
          Effort estimates, the funding range cited in Recommendation 2, and the share of
          effort attributed to extraction are author estimates intended to inform
          institutional debate rather than to serve as audited measurements. All substantive
          panel statistics are reproducible against the cited project version.
        </p>

        <SectionHeading n={6}>Recommendations</SectionHeading>
        <p className="mt-3">
          The recommendations below are addressed to the institutional actors whose
          decisions shape the cost of comparative AI-governance research.
        </p>
        <ol className="mt-3 space-y-3">
          {RECOMMENDATIONS.map((r) => (
            <li key={r.lead}>
              <span className="font-semibold text-gray-900">{r.lead}</span> {r.body}
            </li>
          ))}
        </ol>

        <SectionHeading n={7}>Conclusion</SectionHeading>
        <p className="mt-3">
          The case for open, joinable AI-governance data is institutional rather than
          technical. The technical work is straightforward and has been done. The cost of
          treating machine-readable release as an afterthought is paid by the comparative
          literature as a whole, in papers never written because the merge was too
          expensive.
        </p>

        <h2 className="mt-10 text-lg font-semibold" style={{ color: NAVY }}>
          References
        </h2>
        <ol className="mt-3 list-decimal space-y-1 pl-5 text-gray-600">
          {REFERENCES.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ol>

        <h2 className="mt-8 text-lg font-semibold" style={{ color: NAVY }}>
          Notes
        </h2>
        <ol className="mt-3 list-decimal space-y-1 pl-5 text-gray-600">
          {NOTES.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ol>

        <div className="mt-10 border-t-2 pt-4" style={{ borderColor: NAVY }}>
          <h2 className="text-base font-semibold" style={{ color: NAVY }}>
            About the author
          </h2>
          <p className="mt-2 text-gray-600">
            Anna Siamionava is an undergraduate researcher working at the intersection of AI
            governance and international security. Correspondence:{" "}
            <a href="mailto:annase2004@gmail.com" className="text-blue-600 hover:underline">
              annase2004@gmail.com
            </a>
            .
          </p>
        </div>
      </article>
    </main>
  );
}

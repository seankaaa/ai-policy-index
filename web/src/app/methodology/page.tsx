export default function MethodologyPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <a href="/" className="text-sm text-blue-600 hover:underline">← Back to map</a>
      <h1 className="mt-4 text-2xl font-bold text-gray-900">Methodology</h1>

      <section className="mt-6 space-y-4 text-sm text-gray-700 leading-relaxed">
        <h2 className="text-lg font-semibold text-gray-900">Data Sources</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li>
            <a href="https://oxfordinsights.com/ai-readiness/ai-readiness-index/" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Oxford Insights Government AI Readiness Index
            </a>{" "}
            — annual readiness scores across pillar dimensions.
            2023: 193 countries (3 pillars); 2024: 188 countries (3 pillars);
            2025: 195 countries (6 pillars — Policy Capacity, AI Infrastructure,
            Governance, Public Sector Adoption, Development &amp; Diffusion, Resilience).
          </li>
          <li>
            <a href="https://www.ipsos.com/en/ipsos-ai-monitor-2024" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Ipsos AI Monitor 2024
            </a>{" "}
            — public opinion survey on AI attitudes across 32 countries, covering nervousness,
            excitement, expected life impact, and trust in data protection.
          </li>
          <li>
            <a href="https://hai.stanford.edu/ai-index/2026-ai-index-report" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Stanford HAI 2026 AI Index Report
            </a>{" "}
            — country-level data on generative AI adoption (30 countries), private AI investment
            (15 countries), AI job postings share (22 countries), and cumulative AI laws passed
            (14 G20 countries), all for 2025.
          </li>
        </ul>

        <h2 className="mt-6 text-lg font-semibold text-gray-900">Country Boundaries</h2>
        <p>
          Country boundaries are drawn from the{" "}
          <a href="https://github.com/topojson/world-atlas" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
            world-atlas
          </a>{" "}
          package (Natural Earth, 110m resolution). Boundary depictions reflect the
          source dataset and do not represent endorsement of any political position.
          Disputed territories (Kosovo, Taiwan, Western Sahara, Palestine, Crimea)
          are rendered as provided by the source data.
        </p>

        <h2 className="mt-6 text-lg font-semibold text-gray-900">Known Limitations</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li>Coverage varies by indicator; missing data is shown in gray.</li>
          <li>Oxford Insights 2025 overall scores are approximated from 6 pillar scores weighted by dimension count (mean absolute error ~1.4 points vs. stated values).</li>
          <li>Oxford Insights data is not yet available for 2026.</li>
          <li>Ipsos public opinion data covers 32 countries (primarily high- and upper-middle-income).</li>
        </ul>

        <h2 className="mt-6 text-lg font-semibold text-gray-900">Report an Issue</h2>
        <p>
          <a
            href="https://github.com/seankaaa/ai-policy-index/issues"
            className="text-blue-600 underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Open an issue on GitHub
          </a>
        </p>
      </section>
    </main>
  );
}

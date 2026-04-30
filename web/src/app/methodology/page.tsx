export default function MethodologyPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <a href="/" className="text-sm text-blue-600 hover:underline">← Back to map</a>
      <h1 className="mt-4 text-2xl font-bold text-gray-900">Methodology</h1>

      <section className="mt-6 space-y-4 text-sm text-gray-700 leading-relaxed">
        <h2 className="text-lg font-semibold text-gray-900">Data Sources</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li>
            <a href="https://oxfordinsights.com/ai-readiness/" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Oxford Insights Government AI Readiness Index
            </a>{" "}
            — annual readiness scores for 193 countries across Government, Technology
            Sector, and Data &amp; Infrastructure pillars.
          </li>
          <li>
            <a href="https://oecd.ai/en/dashboards" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              OECD.AI Policy Navigator
            </a>{" "}
            — national AI policies, strategies, and initiatives.
          </li>
          <li>
            <a href="https://www.ipsos.com/en/ai-monitor" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Ipsos AI Monitor
            </a>{" "}
            — annual public opinion survey across 28 countries.
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
          <li>Oxford Insights 2024 data is partial (26/188 countries).</li>
          <li>Public opinion data is primarily from high-income countries.</li>
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

import { getCountryName, getFlagEmoji } from "@/lib/countries";

interface Props {
  params: Promise<{ iso3: string }>;
}

export default async function CountryPage({ params }: Props) {
  const { iso3 } = await params;
  const name = getCountryName(iso3.toUpperCase());
  const flag = getFlagEmoji(iso3.toUpperCase());

  return (
    <main className="mx-auto max-w-4xl px-6 py-8">
      <a href="/" className="text-sm text-blue-600 hover:underline">← Back to map</a>
      <div className="mt-4 flex items-center gap-3">
        <span className="text-4xl" role="img" aria-label={`Flag of ${name}`}>{flag}</span>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{name}</h1>
          <p className="text-sm text-gray-500">{iso3.toUpperCase()}</p>
        </div>
      </div>

      <div className="mt-8 rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-500">
        Country detail pages will show indicator sparklines, policy tables, and
        public opinion charts once the full pipeline data is available.
      </div>
    </main>
  );
}

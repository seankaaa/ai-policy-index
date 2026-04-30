// Single source of truth for ISO numeric → alpha-3 mapping.
// world-atlas TopoJSON uses numeric codes; our data uses alpha-3.

export const numericToAlpha3: Record<string, string> = {
  "004": "AFG", "008": "ALB", "012": "DZA", "024": "AGO", "032": "ARG",
  "036": "AUS", "040": "AUT", "050": "BGD", "056": "BEL", "064": "BTN",
  "068": "BOL", "070": "BIH", "072": "BWA", "076": "BRA", "096": "BRN",
  "100": "BGR", "104": "MMR", "108": "BDI", "112": "BLR", "116": "KHM",
  "120": "CMR", "124": "CAN", "132": "CPV", "140": "CAF", "144": "LKA",
  "148": "TCD", "152": "CHL", "156": "CHN", "170": "COL", "174": "COM",
  "178": "COG", "180": "COD", "188": "CRI", "191": "HRV", "192": "CUB",
  "196": "CYP", "203": "CZE", "204": "BEN", "208": "DNK", "214": "DOM",
  "218": "ECU", "222": "SLV", "226": "GNQ", "231": "ETH", "232": "ERI",
  "233": "EST", "242": "FJI", "246": "FIN", "250": "FRA", "266": "GAB",
  "268": "GEO", "270": "GMB", "276": "DEU", "288": "GHA", "300": "GRC",
  "304": "GRL", "320": "GTM", "324": "GIN", "328": "GUY", "332": "HTI",
  "334": "HMD", "340": "HND", "348": "HUN", "352": "ISL", "356": "IND",
  "360": "IDN", "364": "IRN", "368": "IRQ", "372": "IRL", "376": "ISR",
  "380": "ITA", "384": "CIV", "388": "JAM", "392": "JPN", "398": "KAZ",
  "400": "JOR", "404": "KEN", "408": "PRK", "410": "KOR", "414": "KWT",
  "417": "KGZ", "418": "LAO", "422": "LBN", "426": "LSO", "428": "LVA",
  "430": "LBR", "434": "LBY", "440": "LTU", "442": "LUX", "450": "MDG",
  "454": "MWI", "458": "MYS", "466": "MLI", "474": "MTQ", "478": "MRT",
  "480": "MUS", "484": "MEX", "496": "MNG", "498": "MDA", "504": "MAR",
  "508": "MOZ", "516": "NAM", "524": "NPL", "528": "NLD", "540": "NCL",
  "548": "VUT", "554": "NZL", "558": "NIC", "562": "NER", "566": "NGA",
  "578": "NOR", "585": "PLW", "586": "PAK", "591": "PAN", "598": "PNG",
  "600": "PRY", "604": "PER", "608": "PHL", "616": "POL", "620": "PRT",
  "626": "TLS", "630": "PRI", "634": "QAT", "642": "ROU", "643": "RUS",
  "646": "RWA", "659": "KNA", "662": "LCA", "670": "VCT", "678": "STP",
  "682": "SAU", "686": "SEN", "694": "SLE", "703": "SVK", "704": "VNM",
  "705": "SVN", "706": "SOM", "710": "ZAF", "716": "ZWE", "724": "ESP",
  "729": "SDN", "740": "SUR", "748": "SWZ", "752": "SWE", "756": "CHE",
  "760": "SYR", "762": "TJK", "764": "THA", "768": "TGO", "780": "TTO",
  "784": "ARE", "788": "TUN", "792": "TUR", "795": "TKM", "798": "TUV",
  "800": "UGA", "804": "UKR", "818": "EGY", "826": "GBR", "834": "TZA",
  "840": "USA", "854": "BFA", "858": "URY", "860": "UZB", "862": "VEN",
  "882": "WSM", "887": "YEM", "894": "ZMB",
};

export const alpha3ToName: Record<string, string> = {
  AFG: "Afghanistan", ALB: "Albania", DZA: "Algeria", AGO: "Angola",
  ARG: "Argentina", AUS: "Australia", AUT: "Austria", BGD: "Bangladesh",
  BEL: "Belgium", BOL: "Bolivia", BRA: "Brazil", BGR: "Bulgaria",
  KHM: "Cambodia", CMR: "Cameroon", CAN: "Canada", LKA: "Sri Lanka",
  CHL: "Chile", CHN: "China", COL: "Colombia", COG: "Congo",
  COD: "DR Congo", CRI: "Costa Rica", HRV: "Croatia", CUB: "Cuba",
  CYP: "Cyprus", CZE: "Czech Republic", DNK: "Denmark", ECU: "Ecuador",
  EGY: "Egypt", SLV: "El Salvador", ETH: "Ethiopia", FIN: "Finland",
  FRA: "France", GAB: "Gabon", DEU: "Germany", GHA: "Ghana",
  GRC: "Greece", GTM: "Guatemala", HTI: "Haiti", HND: "Honduras",
  HUN: "Hungary", IND: "India", IDN: "Indonesia", IRN: "Iran",
  IRQ: "Iraq", IRL: "Ireland", ISR: "Israel", ITA: "Italy",
  JAM: "Jamaica", JPN: "Japan", JOR: "Jordan", KEN: "Kenya",
  PRK: "North Korea", KOR: "South Korea", KWT: "Kuwait", LAO: "Laos",
  LBN: "Lebanon", LBR: "Liberia", LBY: "Libya", LUX: "Luxembourg",
  MDG: "Madagascar", MWI: "Malawi", MYS: "Malaysia", MEX: "Mexico",
  MNG: "Mongolia", MAR: "Morocco", MOZ: "Mozambique", NAM: "Namibia",
  NPL: "Nepal", NLD: "Netherlands", NZL: "New Zealand", NIC: "Nicaragua",
  NGA: "Nigeria", NOR: "Norway", PAK: "Pakistan", PAN: "Panama",
  PER: "Peru", PHL: "Philippines", POL: "Poland", PRT: "Portugal",
  QAT: "Qatar", ROU: "Romania", RUS: "Russia", SAU: "Saudi Arabia",
  SEN: "Senegal", SLE: "Sierra Leone", SVK: "Slovakia", SVN: "Slovenia",
  SOM: "Somalia", ZAF: "South Africa", ESP: "Spain", SDN: "Sudan",
  SWE: "Sweden", CHE: "Switzerland", SYR: "Syria", THA: "Thailand",
  TUR: "Turkey", UGA: "Uganda", UKR: "Ukraine", ARE: "UAE",
  GBR: "United Kingdom", USA: "United States", URY: "Uruguay",
  VEN: "Venezuela", VNM: "Vietnam", YEM: "Yemen", ZMB: "Zambia",
  ZWE: "Zimbabwe", XKX: "Kosovo", TWN: "Taiwan", PSE: "Palestine",
  BLR: "Belarus", BIH: "Bosnia and Herzegovina", MKD: "North Macedonia",
  MDA: "Moldova", GEO: "Georgia", ARM: "Armenia", AZE: "Azerbaijan",
  KAZ: "Kazakhstan", UZB: "Uzbekistan", TJK: "Tajikistan",
  KGZ: "Kyrgyzstan", TKM: "Turkmenistan", ISL: "Iceland",
  LTU: "Lithuania", LVA: "Latvia", EST: "Estonia", BWA: "Botswana",
  RWA: "Rwanda", TZA: "Tanzania", CIV: "Côte d'Ivoire", BFA: "Burkina Faso",
  MLI: "Mali", NER: "Niger", TGO: "Togo", BEN: "Benin", GIN: "Guinea",
  GMB: "Gambia", MRT: "Mauritania", SUR: "Suriname", GUY: "Guyana",
  TTO: "Trinidad and Tobago", PNG: "Papua New Guinea", FJI: "Fiji",
  TLS: "Timor-Leste", SWZ: "Eswatini", LSO: "Lesotho", SGP: "Singapore",
  HKG: "Hong Kong",
};

export function getCountryName(iso3: string): string {
  return alpha3ToName[iso3] ?? iso3;
}

export function isValidIso3(code: string): boolean {
  return /^[A-Z]{3}$/.test(code);
}

const alpha3ToAlpha2: Record<string, string> = {
  AFG: "AF", ALB: "AL", DZA: "DZ", AGO: "AO", ARG: "AR", AUS: "AU",
  AUT: "AT", BGD: "BD", BEL: "BE", BOL: "BO", BRA: "BR", BGR: "BG",
  KHM: "KH", CMR: "CM", CAN: "CA", LKA: "LK", CHL: "CL", CHN: "CN",
  COL: "CO", COG: "CG", COD: "CD", CRI: "CR", HRV: "HR", CUB: "CU",
  CYP: "CY", CZE: "CZ", DNK: "DK", ECU: "EC", EGY: "EG", SLV: "SV",
  ETH: "ET", FIN: "FI", FRA: "FR", GAB: "GA", DEU: "DE", GHA: "GH",
  GRC: "GR", GTM: "GT", HTI: "HT", HND: "HN", HUN: "HU", IND: "IN",
  IDN: "ID", IRN: "IR", IRQ: "IQ", IRL: "IE", ISR: "IL", ITA: "IT",
  JAM: "JM", JPN: "JP", JOR: "JO", KEN: "KE", PRK: "KP", KOR: "KR",
  KWT: "KW", LAO: "LA", LBN: "LB", LBR: "LR", LBY: "LY", LUX: "LU",
  MDG: "MG", MWI: "MW", MYS: "MY", MEX: "MX", MNG: "MN", MAR: "MA",
  MOZ: "MZ", NAM: "NA", NPL: "NP", NLD: "NL", NZL: "NZ", NIC: "NI",
  NGA: "NG", NOR: "NO", PAK: "PK", PAN: "PA", PER: "PE", PHL: "PH",
  POL: "PL", PRT: "PT", QAT: "QA", ROU: "RO", RUS: "RU", SAU: "SA",
  SEN: "SN", SLE: "SL", SVK: "SK", SVN: "SI", SOM: "SO", ZAF: "ZA",
  ESP: "ES", SDN: "SD", SWE: "SE", CHE: "CH", SYR: "SY", THA: "TH",
  TUR: "TR", UGA: "UG", UKR: "UA", ARE: "AE", GBR: "GB", USA: "US",
  URY: "UY", VEN: "VE", VNM: "VN", YEM: "YE", ZMB: "ZM", ZWE: "ZW",
  BLR: "BY", BIH: "BA", MKD: "MK", MDA: "MD", GEO: "GE", ARM: "AM",
  AZE: "AZ", KAZ: "KZ", UZB: "UZ", TJK: "TJ", KGZ: "KG", TKM: "TM",
  ISL: "IS", LTU: "LT", LVA: "LV", EST: "EE", BWA: "BW", RWA: "RW",
  TZA: "TZ", CIV: "CI", BFA: "BF", MLI: "ML", NER: "NE", TGO: "TG",
  BEN: "BJ", GIN: "GN", GMB: "GM", MRT: "MR", SUR: "SR", GUY: "GY",
  TTO: "TT", PNG: "PG", FJI: "FJ", TLS: "TL", SWZ: "SZ", LSO: "LS",
  TWN: "TW", SGP: "SG",
};

export function getFlagEmoji(iso3: string): string {
  const alpha2 = alpha3ToAlpha2[iso3];
  if (!alpha2) return "🌐";
  return Array.from(alpha2)
    .map((c) => String.fromCodePoint(0x1f1e6 - 65 + c.charCodeAt(0)))
    .join("");
}

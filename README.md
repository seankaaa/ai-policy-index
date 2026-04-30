# AI Policy Index

A unified, country-indexed dataset combining global AI policy, governmental AI readiness indices, and public opinion on AI regulation. All tables are keyed on `country_iso3` (ISO 3166-1 alpha-3) + `year`.

**Coverage:** 193 countries · 2015–2026 · 14 sources  
**Update cadence:** Monthly refresh on the 30th of each month (GitHub Actions)  
**Contact:** annase2004@gmail.com

---

## Quick start

```bash
# Install dependencies
uv sync

# Fetch + normalize + validate a specific source
uv run python -m src.cli run oxford_readiness

# Run all sources and merge
uv run python -m src.cli run-all

# Merge only (from cached interim data)
uv run python -m src.cli merge

# Run tests
uv run pytest
```

---

## Output tables

All processed tables are in `data/processed/`.

### `policies.parquet`

AI laws, strategies, regulations, and guidelines.

| Column | Type | Description |
|--------|------|-------------|
| `country_iso3` | str | ISO 3166-1 alpha-3 |
| `country_name` | str | English country name |
| `policy_id` | str | Source-namespaced ID (e.g. `iapp:eu_ai_act`) |
| `policy_name` | str | Official policy name |
| `policy_type` | str | `legislation`, `regulation`, `strategy`, `guideline`, `principle`, `funding`, `other` |
| `policy_status` | str | `proposed`, `enacted`, `enforced`, `superseded` |
| `target_sector` | str \| null | Sector (health, finance, …) or null for cross-sector |
| `risk_focus` | list[str] | Risk categories addressed |
| `enacted_date` | str \| null | ISO 8601 date or null |
| `source_url` | str | Canonical URL for this policy |
| `source` | str | Source module name |
| `retrieved_at` | str | ISO 8601 UTC timestamp |

### `indicators.parquet`

Quantitative readiness and governance scores.

| Column | Type | Description |
|--------|------|-------------|
| `country_iso3` | str | ISO 3166-1 alpha-3 |
| `country_name` | str | English country name |
| `year` | int | Reference year (2015–2026) |
| `indicator_id` | str | Namespaced ID (e.g. `oxford_readiness.overall`) |
| `indicator_name` | str | Human-readable name |
| `value` | float | Score or count |
| `unit` | str | `score_0_100`, `score_0_10`, `count`, `rank`, … |
| `source` | str | Source module name |
| `methodology_url` | str | Link to methodology documentation |
| `retrieved_at` | str | ISO 8601 UTC timestamp |

### `public_opinion.parquet`

Survey toplines on AI attitudes.

| Column | Type | Description |
|--------|------|-------------|
| `country_iso3` | str | ISO 3166-1 alpha-3 |
| `year` | int | Survey year |
| `survey` | str | Survey programme name |
| `question_id` | str | Namespaced question ID |
| `question_text` | str | Full question wording |
| `response_category` | str | Response label (e.g. "agree", "very concerned") |
| `value` | float | Percentage (0–100) |
| `n` | int \| null | Respondents for this cell |
| `weighted` | bool | Whether value is weighted |
| `source_url` | str | Report URL |
| `retrieved_at` | str | ISO 8601 UTC timestamp |

### `country_year_panel.parquet`

Wide-format panel for regression analysis. Pivoted from `indicators` using a curated set of cross-source indicators. One row per (country, year).

---

## Sources

| # | Source | Tier | Table(s) | Countries | Years |
|---|--------|------|----------|-----------|-------|
| 1 | Oxford Insights Government AI Readiness Index | 1 | indicators | 193 | 2019–2024 |
| 2 | OECD.AI Policy Navigator | 1 | policies, indicators | 50+ | 2016–2025 |
| 3 | Global Index on Responsible AI (GIRAI) | 1 | indicators | 138 | 2023–2024 |
| 4 | Stanford HAI AI Index | 1 | indicators, public_opinion | 30+ | 2017–2024 |
| 5 | AIMS Survey (Sentience Institute) | 1 | public_opinion | 17 | 2023 |
| 6 | Zhang & Dafoe GovAI 2019 | 1 | public_opinion | 1 (USA) | 2019 |
| 7 | Kelley et al. 8-Country AI Perception | 1 | public_opinion | 8 | 2019 |
| 8 | World Risk Poll (Lloyd's Register Foundation) | 1 | public_opinion | 140 | 2019–2022 |
| 9 | IAPP Global AI Law and Policy Tracker | 2 | policies | 60+ | 2016–2025 |
| 10 | Pew Research AI surveys | 2 | public_opinion | 1 (USA) | 2022–2023 |
| 11 | UNESCO RAM country reports | 3 | indicators | 25+ | 2022–2024 |
| 12 | Ipsos AI Monitor (toplines) | 3 | public_opinion | 28 | 2022–2024 |
| 13 | Local US Officials AI Survey (arXiv:2501.09606) | 3 | public_opinion | 1 (USA) | 2024 |
| 14 | Eurobarometer microdata (GESIS) | 4* | public_opinion | 27 EU | 2019–2022 |

*Tier 4 sources require manual registration/download. See `data/raw/eurobarometer/ACCESS_REQUIRED.md`.

### Tier definitions

| Tier | Meaning |
|------|---------|
| 1 | Direct download / public API |
| 2 | HTML scrape of public table |
| 3 | PDF extraction or hardcoded published toplines |
| 4 | Requires registration or commercial license — not auto-fetched |

---

## Coverage matrix

```
             oxford girai oecd stanford ipsos pew kelley zhang world_risk  local_us
USA            ✓      ✓    ✓      ✓      ✓    ✓    ✓     ✓       ✓          ✓
GBR            ✓      ✓    ✓      ✓      ✓         ✓             ✓
DEU            ✓      ✓    ✓      ✓      ✓         ✓
FRA            ✓      ✓    ✓      ✓      ✓         ✓
CHN            ✓      ✓    ✓      ✓      ✓
IND            ✓      ✓    ✓      ✓      ✓         ✓             ✓
BRA            ✓      ✓    ✓      ✓      ✓         ✓             ✓
[188 more]     ✓      ✓    ✓
```

---

## APA citations

1. Oxford Insights. (2023). *Government AI Readiness Index 2023*. https://oxfordinsights.com/ai-readiness/

2. OECD. (2025). *OECD.AI Policy Navigator* [Data set]. https://oecd.ai/dashboards

3. GIRAI. (2024). *Global Index on Responsible AI*. https://www.global-index.ai/

4. Maslej, N., Fattorini, L., Brynjolfsson, E., Etchemendy, J., Ligett, K., Lyons, T., Manyika, J., Ngo, H., Niebles, J. C., Parli, V., Shoham, Y., Wald, R., Clark, J., & Perrault, R. (2024). *Artificial Intelligence Index Report 2024*. Stanford University Human-Centered Artificial Intelligence. https://hai.stanford.edu/ai-index/

5. Sentience Institute. (2023). *AI Moral Status Survey (AIMS)*. OSF. https://osf.io/

6. Zhang, B., & Dafoe, A. (2019). *Artificial Intelligence: American Attitudes and Trends*. Center for the Governance of AI, Future of Humanity Institute, University of Oxford. https://osf.io/

7. Kelley, P. G., Yang, Y., Heldreth, C., Moessner, C., Sedlins, A., Woodruff, A., & Woodruff, M. (2021). *Exciting, worrying, and ambivalent: Public attitudes to AI in 8 countries* [Preprint]. arXiv:2001.00081.

8. Lloyd's Register Foundation. (2022). *World Risk Poll 2022*. https://wrp.lrfoundation.org.uk/

9. IAPP. (2024). *Global AI Law and Policy Tracker*. https://iapp.org/resources/article/global-ai-legislation-tracker/

10. Pew Research Center. (2023). *Public Awareness and Concern About Artificial Intelligence*. https://www.pewresearch.org/

11. UNESCO. (2023). *Readiness Assessment Methodology (RAM)*. https://www.unesco.org/ethics-ai/en/ram

12. Ipsos. (2024). *AI Monitor 2024*. https://www.ipsos.com/en/ai-monitor

13. Liu, E., Shin, D., & Johnson, J. (2025). *Local Government Officials and AI* [Preprint]. arXiv:2501.09606.

14. European Commission / GESIS. (2019). *Standard Eurobarometer 91.3: Robots and Artificial Intelligence* [Data set]. GESIS Study No. ZA7576. https://search.gesis.org/research_data/ZA7576

---

## Example queries (Polars)

```python
import polars as pl

indicators = pl.read_parquet("data/processed/indicators.parquet")
public_opinion = pl.read_parquet("data/processed/public_opinion.parquet")

# Top 10 countries by Oxford AI Readiness 2023
(indicators
    .filter((pl.col("indicator_id") == "oxford_readiness.overall") & (pl.col("year") == 2023))
    .sort("value", descending=True)
    .head(10)
    .select(["country_iso3", "value"])
)

# Countries with the highest % supporting AI regulation
(public_opinion
    .filter(pl.col("question_id").str.contains("regulation") | pl.col("question_id").str.contains("support"))
    .sort("value", descending=True)
    .select(["country_iso3", "year", "survey", "question_text", "value"])
    .head(10)
)

# Join readiness scores with public opinion
panel = pl.read_parquet("data/processed/country_year_panel.parquet")
(panel
    .select(["country_iso3", "year", "oxford_readiness.overall", "oxford_readiness.government_pillar"])
    .sort(["country_iso3", "year"])
    .head(20)
)
```

---

## Known gaps and limitations

- **Oxford Readiness 2019–2022**: Form-gated download at oxfordinsights.com; 2024 partial (26/188 countries from Exa highlights). Place `YYYY-detailed-scores.csv` files in `data/raw/oxford_readiness/` to ingest.
- **IAPP tracker**: JavaScript-rendered page; static HTML scrape may be empty. Visit the URL and save page HTML manually to `data/raw/iapp_tracker/tracker.html`.
- **Ipsos AI Monitor**: Free toplines parsed; microdata requires commercial license. See `data/raw/ipsos_ai_monitor_microdata/ACCESS_REQUIRED.md`.
- **Eurobarometer**: GESIS registration required. See `data/raw/eurobarometer/ACCESS_REQUIRED.md`.
- **AIMS Survey / World Risk Poll**: OSF/LRF direct URLs may redirect to registration pages. Check ACCESS_NOTE.txt files in the respective raw directories.
- **UNESCO RAM**: Requires individual country PDF downloads; scores are extracted from PDF text which may fail for non-standard layouts.

---

## Project structure

```
ai-policy-index/
├── config/
│   └── sources.yaml          # Source registry
├── data/
│   ├── raw/                  # Cached HTTP responses, per-source
│   ├── interim/              # Per-source normalized parquets
│   └── processed/            # Merged output tables
├── src/
│   ├── cli.py                # CLI: fetch / normalize / validate / run / merge / run-all
│   ├── merge.py              # Cross-source merge + panel builder
│   ├── common/
│   │   ├── countries.py      # ISO 3166-1 alpha-3 normalization
│   │   ├── http.py           # Rate-limited HTTP client with caching
│   │   ├── pdf.py            # pdfplumber utilities
│   │   └── schema.py         # Pydantic row models
│   └── sources/              # One module per source
├── tests/                    # pytest test suite
├── .github/workflows/
│   └── monthly-refresh.yml   # Automated monthly refresh
└── pyproject.toml
```

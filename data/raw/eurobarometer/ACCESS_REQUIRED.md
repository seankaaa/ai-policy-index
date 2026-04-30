# Eurobarometer Microdata — Access Required

**Source:** European Commission Standard Eurobarometer surveys  
**Provider:** GESIS – Leibniz Institute for the Social Sciences  
**URL:** https://search.gesis.org/research_data/ZA8779  
**Tier:** 4 (access-controlled, not auto-fetched)

## Why this is not auto-fetched

GESIS requires free registration and acceptance of their Terms of Service before
microdata can be downloaded.  Automated bulk download violates those terms.

## Data available

Relevant surveys containing AI/technology perception items:

| Study ID | Wave | Year | AI-relevant questions |
|----------|------|------|----------------------|
| ZA8779   | EB 97.0 | 2022 | "AI will fundamentally change daily life" (Q3); trust in AI (Q4) |
| ZA8740   | EB 96.1 | 2021 | Digital society attitudes |
| ZA7576   | EB 91.3 | 2019 | "Robots and AI" battery (QB1–QB7) — 27 EU countries |
| ZA6861   | EB 85.2 | 2016 | Digitisation and automation attitudes |

The 2019 wave (ZA7576) is the most relevant: it has a dedicated 7-question AI
battery covering benefit, risk, job displacement, and regulation across all 27 EU
member states + UK.

## How to download manually

1. Go to https://search.gesis.org/research_data/ZA7576
2. Register for a free GESIS account (academic or public researcher)
3. Accept the data use agreement
4. Download the SPSS (.sav) or CSV file
5. Place the file in this directory:  `data/raw/eurobarometer/ZA7576.csv`
6. Run: `python -m src.cli normalize eurobarometer`

## Expected schema after normalization

The normalizer will produce `public_opinion` rows:

```
country_iso3 | year | survey            | question_id  | question_text | response_category | value | n    | weighted
AUT          | 2019 | eurobarometer_91  | eb.ai_benefit| "AI will...   | agree             | 67.0  | 1029 | true
...
```

Coverage: 27 EU countries (+ GBR pre-Brexit in 2019 wave), ~1,000 respondents each.

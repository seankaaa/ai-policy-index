# Oxford Insights Government AI Readiness Index — Access Notes

## Status per edition

| Year | Countries | Status |
|------|-----------|--------|
| 2023 | 193/193 | ✅ Complete — extracted from public PDF (Annex II) |
| 2024 | 26/188 | ⚠️ Partial — full data requires form-based download at oxfordinsights.com |
| 2022 | 0/183 | ❌ Blocked — public Google Sheet (goo.gl/spreadsheets/…) returns 403 to scripts |
| 2019–2021 | 0/194 | ❌ Blocked — Oxford Insights wp-content URLs return 403; PDF appendices needed |

## To get full historical depth

1. Visit https://oxfordinsights.com/ai-readiness/ai-readiness-index/
2. Complete the download form (name + email — no paywall)
3. Download each year's Excel file
4. Place in data/raw/oxford_readiness/ as `YYYY-<any-name>.xlsx`
5. Run: `python -m src.cli normalize oxford_readiness`

The normalize() function handles xlsx automatically.

# Ipsos AI Monitor Microdata — Access Required

**Source:** Ipsos AI Monitor (annual global survey)  
**URL:** https://www.ipsos.com/en/ai-monitor  
**Tier:** 4 (commercial license required for microdata)

## Why this is not auto-fetched

Ipsos microdata (individual-level responses with demographic breakdowns) is
available only under a commercial data-sharing agreement with Ipsos.  Academic
researchers may apply for data access; commercial users must purchase a license.

The **`ipsos_ai_monitor`** source (Tier 3) already fetches and parses the free
public topline PDFs, which contain country-level aggregate percentages.

## What the microdata adds (vs. toplines)

- Cross-tabulations by age, gender, education, income
- Country-level response distributions (not just toplines)
- Trend lines at the question-by-country-by-demographic level
- Access to all ~30 questions (toplines only show a subset)

## Data available (toplines — already ingested by Tier 3 source)

| Edition | Year | Countries | Free PDF |
|---------|------|-----------|----------|
| AI Monitor 2024 | 2024 | 28 | https://www.ipsos.com/sites/default/files/ct/news/documents/2024-01/Ipsos-AI-Monitor-2024-Report.pdf |
| AI Monitor 2023 | 2023 | 28 | https://www.ipsos.com/sites/default/files/ct/news/documents/2023-07/Ipsos-AI-Monitor-2023.pdf |
| AI Monitor 2022 | 2022 | 28 | (check ipsos.com/en/ai-monitor for archived link) |

## How to request microdata access

Academic institutions: Contact research@ipsos.com with your institutional
affiliation and research purpose.  Some waves are available via ICPSR or ROPER
for academic users.

Commercial users: Contact your Ipsos account manager.

## Once you have access

Place the microdata CSV in this directory:  
`data/raw/ipsos_ai_monitor_microdata/ipsos_ai_monitor_YYYY.csv`

A future normalizer stub at `src/sources/ipsos_ai_monitor_microdata.py` can then
process the full individual-level data into the `public_opinion` table with
demographic breakdowns.

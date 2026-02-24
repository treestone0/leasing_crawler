# Phase 2 – LeasingmarktAdapter

## Summary

Phase 2 implements crawling of leasingmarkt.de for both `/deals` and `/listing` pages, with politeness (robots.txt, delay, retries) and HTML parsing.

---

## Implementation Steps

### 1. PoliteHttpClient (`src/core/crawler.py`)

- **robots.txt**: Uses `urllib.robotparser` to check paths before fetching
- **Delay**: Configurable delay between requests (default 1.5s via `CRAWLER_DELAY` env)
- **Retries**: Max 3 attempts with exponential backoff on failure
- **User-Agent**: Configurable, non-aggressive identifier

### 2. LeasingmarktAdapter (`src/adapters/leasingmarkt.py`)

- Implements `BaseAdapter.fetch_offers(filter)` and `supports_source(source)`
- **`/deals`**: Fetches curated deals (single page, ~15–62 offers)
- **`/listing`**: Paginates up to 5 pages (15 offers/page)
- **Parsing**: Extracts from HTML offer cards:
  - Brand, model, variant (from URL slug and link text)
  - km/year, laufzeit (months)
  - Price per month (Rate), einmalige Kosten
  - Link to offer

### 3. CLI Integration (`src/cli.py`)

- Loads filters from input JSON
- Uses `LeasingmarktAdapter` to fetch offers per filter
- Writes results to `output/` (JSON format)

---

## How to Run the CLI

### Prerequisites

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# From project root – use sample input
python main.py input/sample.json
```

### Output Path

```bash
# Custom output base path (writes result.json and later result.xlsx)
python main.py input/sample.json -o output/my_run
```

### Faster Crawling (testing only)

```bash
# Shorter delay between requests (default 1.5s)
CRAWLER_DELAY=0.5 python main.py input/sample.json
```

### Output Location

- **Default**: `output/result.json`
- **With `-o`**: `{output_path}.json` (e.g. `output/my_run.json`)

---

## Output Format (JSON)

Results are written to `output/result.json` (or the path from `-o`) and include some metadata:

```json
{
  "generated_at": "2026-02-24T12:40:39.333318+00:00",
  "input_json": "input/sample.json",
  "output": {
    "json": "output/result.json",
    "excel_planned": "output/result.xlsx"
  },
  "crawler": {
    "request_delay_seconds": 1.5,
    "user_agent": "LeasingCrawler/1.0 (+https://github.com/leasing-crawler)",
    "max_retries": 3,
    "respect_robots_txt": true
  },
  "filters": [
    {
      "id": "filter_1",
      "source": "deals",
      "filter": {
        "id": "filter_1",
        "source": "deals",
        "brand": "Volkswagen",
        "model": "Golf"
      },
      "total_offers": 15,
      "offers": [
        {
          "brand": "Smart",
          "model": "1",
          "variant": "Pure",
          "km_per_year": 10000,
          "laufzeit_months": 36,
          "price_per_month": 133.95,
          "einmalige_kosten": 6000.0,
          "link": "https://www.leasingmarkt.de/leasing/pkw/smart-1/...",
          "notes": ""
        }
      ]
    }
  ]
}
```

---

## Status

- [x] PoliteHttpClient with politeness
- [x] LeasingmarktAdapter for deals and listing
- [x] CLI fetches and writes JSON to output_dir
- [ ] Excel output (Phase 3)
- [ ] In-code filtering (Phase 4)

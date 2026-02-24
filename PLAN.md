# Germany Private Leasing Car Crawler – Project Plan

## 1. Project Summary

A CLI tool that crawls German private leasing car sites (MVP: leasingmarkt.de), accepts JSON filters, and outputs an Excel file with car data. Later extensible via adapters for other sites.

---

## 2. Answers to Clarification Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Runtime | **CLI only** – run manually: `python main.py input.json` |
| 2 | Data scope | **Both** – `/deals` and `/listing` (configurable per filter) |
| 3 | "Price for handler" | **Einmalige Kosten** – one-time upfront cost before leasing (Anzahlung + Überführungskosten + Zulassungskosten = Gesamt, einmalig) |
| 4 | Excel output | **One file** – summary sheet + one sheet per filter |
| 5 | Politeness | **Respect robots.txt**, 1–2 sec delay between requests |

---

## 3. Default Settings & Infrastructure

### 3.1 Tech Stack (Defaults)

- **Language**: Python 3.11+
- **HTTP**: `httpx` or `requests` + `BeautifulSoup` (or `parsel`) for HTML parsing
- **Excel**: `openpyxl` or `xlsxwriter`
- **Config**: `pydantic` for JSON schema validation
- **Logging**: `structlog` or stdlib `logging`

### 3.2 Project Structure

```
leasing_crawler_v2/
├── src/
│   ├── adapters/           # Site-specific adapters
│   │   ├── base.py         # Abstract base adapter
│   │   └── leasingmarkt.py # leasingmarkt.de adapter
│   ├── core/
│   │   ├── filters.py      # Filter model (brand, model, blacklist, etc.)
│   │   ├── crawler.py      # Crawling logic + politeness
│   │   └── excel.py        # Excel writer (summary + per-filter sheets)
│   ├── cli.py              # Entry point
│   └── config.py           # Default settings
├── input/                  # Sample input JSONs
├── output/                 # Generated Excel files
├── tests/
├── CODE_CHANGE_RESTRICTION.md
├── PLAN.md                 # This plan (saved for later)
├── requirements.txt
└── README.md
```

### 3.3 Politeness & Crawling Defaults

- **Delay**: 1.5 seconds between requests (configurable via env/config)
- **robots.txt**: Use `urllib.robotparser` or `robotexclusionrulesparser`
- **User-Agent**: Identifiable but non-aggressive
- **Retries**: Max 3 with exponential backoff

### 3.4 API vs Crawling

- **leasingmarkt.de**: No public REST API for listings; we will crawl HTML.
- **Strategy**: Fetch HTML from `/deals` and `/listing`, parse offer cards. If the site loads data via XHR/fetch, we will inspect network calls and prefer internal APIs if they are stable and documentable.

---

## 4. Input JSON Schema

```json
[
  {
    "id": "filter_1",
    "source": "deals",
    "brand": "Volkswagen",
    "model": "Golf",
    "brand_blank_ok": false,
    "model_blank_ok": true,
    "km_per_year_min": 10000,
    "km_per_year_max": 15000,
    "price_per_month_max": 250,
    "einmalige_kosten_max": 1500,
    "blacklist_brands": ["Opel", "Dacia"],
    "blacklist_models": ["Polo"]
  },
  {
    "id": "filter_2",
    "source": "listing",
    "brand": "",
    "model": "",
    "brand_blank_ok": true,
    "model_blank_ok": true,
    "price_per_month_max": 200
  }
]
```

- **source**: `"deals"` | `"listing"`
- **brand** / **model**: Empty string = all; `brand_blank_ok` / `model_blank_ok` allow blank = all.
- **blacklist_brands** / **blacklist_models**: Excluded from results.
- **km_per_year_min** / **km_per_year_max**: Filter by km/year.
- **price_per_month_max**: Max monthly rate.
- **einmalige_kosten_max**: Max one-time upfront cost.
- **id**: Used as Excel sheet name and filter identification.

---

## 5. Output Excel Structure

| Sheet | Content |
|-------|---------|
| **Summary** | One row per filter: filter_id, source, total_matches, top_3_links, timestamp |
| **filter_1** | All matching cars for filter 1 (columns below) |
| **filter_2** | All matching cars for filter 2 |
| … | … |

**Per-car columns** (per-filter sheets):

- Brand, Model, Variant
- km/year, Laufzeit (months)
- Price/month (Rate), Einmalige Kosten (one-time cost)
- Link to offer
- Notes (for manual input, e.g. "Anfrage gesendet", "Händler kontaktiert")

---

## 6. Adapter Pattern (Extensibility)

```mermaid
flowchart TB
    subgraph core [Core]
        CLI[CLI]
        Crawler[Crawler]
        Excel[Excel Writer]
    end

    subgraph adapters [Adapters]
        Base[BaseAdapter]
        LM[LeasingmarktAdapter]
    end

    CLI --> Crawler
    Crawler --> Base
    Base <|-- LM
    Crawler --> Excel
```

- **BaseAdapter** defines: `fetch_offers(filter) -> List[Offer]`, `supports_source(source: str) -> bool`.
- **LeasingmarktAdapter** implements both `deals` and `listing`.
- New sites: add `adapters/newsite.py`, register in config.

---

## 7. Implementation Phases

1. **Phase 1 – Foundation**: Project setup, config, CLI skeleton, input JSON parsing, `BaseAdapter`.
2. **Phase 2 – LeasingmarktAdapter**: Implement `/deals` and `/listing` crawling with politeness.
3. **Phase 3 – Excel**: Summary sheet + per-filter sheets, columns as above.
4. **Phase 4 – Filtering**: Apply brand/model, blacklist, km/year, price, einmalige Kosten in code.
5. **Phase 5 – Polish**: Logging, error handling, `README`, `CODE_CHANGE_RESTRICTION.md`.

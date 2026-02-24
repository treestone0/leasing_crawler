# Germany Private Leasing Car Crawler

CLI tool that crawls German private leasing car sites (MVP: [leasingmarkt.de](https://leasingmarkt.de)), accepts JSON filters, and outputs results as **JSON** (Excel export planned in Phase 3).

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py input.json
python main.py input.json -o output/my_results
python main.py input.json -o output/my_results.xlsx
```

- **input.json** – Path to a JSON file with filter definitions (see [Input format](#input-format))
- **-o, --output** – Output base path (e.g. `output/result`) or Excel path (e.g. `output/result.xlsx`). JSON is written next to it.

### Output

- **JSON (current)**: `output/result.json` by default
- **Excel (planned)**: `output/result.xlsx` (Phase 3)

## Input Format

The input JSON is an array of filter objects:

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
  }
]
```

| Field | Description |
|-------|-------------|
| `id` | Filter ID, used as Excel sheet name |
| `source` | `"deals"` or `"listing"` |
| `brand` / `model` | Search terms (empty = all) |
| `brand_blank_ok` / `model_blank_ok` | Allow blank = all |
| `km_per_year_min` / `km_per_year_max` | Filter by km/year |
| `price_per_month_max` | Max monthly rate (EUR) |
| `einmalige_kosten_max` | Max one-time upfront cost (EUR) |
| `blacklist_brands` / `blacklist_models` | Excluded from results |

A sample file is in `input/sample.json`.

## Project Structure

```
├── src/
│   ├── adapters/        # Site-specific adapters
│   │   ├── base.py      # BaseAdapter, Offer model
│   │   └── leasingmarkt.py  (Phase 2)
│   ├── core/
│   │   ├── filters.py   # Filter model, JSON loading
│   │   ├── crawler.py   (Phase 2)
│   │   └── excel.py     (Phase 3)
│   ├── cli.py           # CLI entry point
│   └── config.py        # Configuration
├── input/               # Sample input JSONs
├── output/              # Generated Excel files
│                        # (Phase 2 writes JSON here as well)
├── main.py              # Entry point
├── PLAN.md              # Full project plan
├── docs/
│   └── PHASE2.md         # Phase 2 implementation notes
└── CODE_CHANGE_RESTRICTION.md
```

## Status

- **Phase 1** – Foundation (done): CLI, config, input parsing, BaseAdapter
- **Phase 2** – LeasingmarktAdapter: crawling
- **Phase 3** – Excel output
- **Phase 4** – In-code filtering
- **Phase 5** – Logging, error handling

See `PLAN.md` for details.

"""CLI entry point for the leasing crawler."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from src.adapters.leasingmarkt import LeasingmarktAdapter
from src.config import AppConfig
from src.core.crawler import PoliteHttpClient
from src.core.filters import load_filters_from_file


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Crawl German private leasing sites and output results."
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to input JSON file with filter definitions",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help=(
            "Output base path (e.g. output/result) or Excel path (e.g. output/result.xlsx). "
            "JSON will be written next to it."
        ),
    )
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point. Returns exit code."""
    parsed = parse_args(args)
    config = AppConfig.from_env()

    if not parsed.input_json.exists():
        print(f"Error: Input file not found: {parsed.input_json}", file=sys.stderr)
        return 1

    try:
        filters = load_filters_from_file(parsed.input_json)
    except Exception as e:
        print(f"Error loading filters: {e}", file=sys.stderr)
        return 1

    base_path = parsed.output or (Path(config.output_dir) / "result")
    if base_path.suffix in (".xlsx", ".json"):
        base_path = base_path.with_suffix("")
    base_path.parent.mkdir(parents=True, exist_ok=True)

    excel_path = base_path.with_suffix(".xlsx")
    json_path = base_path.with_suffix(".json")

    adapter = LeasingmarktAdapter(http_client=PoliteHttpClient(config.crawler))
    print(f"Loaded {len(filters)} filter(s). Output will go to {json_path} (JSON)")

    results: list[dict] = []
    for f in filters:
        if not adapter.supports_source(f.source):
            print(f"  - {f.id}: unsupported source {f.source}", file=sys.stderr)
            continue
        try:
            offers = adapter.fetch_offers(f)
        except Exception as e:
            print(f"  - {f.id}: source={f.source}, error: {e}", file=sys.stderr)
            continue
        print(f"  - {f.id}: source={f.source}, fetched {len(offers)} offers")

        results.append(
            {
                "id": f.id,
                "source": f.source,
                "filter": f.model_dump(),
                "total_offers": len(offers),
                "offers": [asdict(o) for o in offers],
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_json": str(parsed.input_json),
        "output": {
            "json": str(json_path),
            "excel_planned": str(excel_path),
        },
        "crawler": {
            "request_delay_seconds": config.crawler.request_delay_seconds,
            "user_agent": config.crawler.user_agent,
            "max_retries": config.crawler.max_retries,
            "respect_robots_txt": config.crawler.respect_robots_txt,
        },
        "filters": results,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote JSON results to {json_path}")

    return 0

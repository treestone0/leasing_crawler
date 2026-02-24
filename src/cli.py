"""CLI entry point for the leasing crawler."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from src.config import AppConfig
from src.core.filters import load_filters_from_file


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Crawl German private leasing sites and output Excel."
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
        help="Output Excel file path (default: output/result.xlsx)",
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

    output_path = parsed.output or Path(config.output_dir) / "result.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # TODO Phase 2: Select adapter, fetch offers, write Excel
    print(f"Loaded {len(filters)} filter(s). Output will go to {output_path}")
    for f in filters:
        print(f"  - {f.id}: source={f.source}, brand={f.brand or '(all)'}, model={f.model or '(all)'}")

    return 0

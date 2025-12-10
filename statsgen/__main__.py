#!/usr/bin/env python3
"""
CLI entry point for statsgen
run with: python -m statsgen
"""

import argparse
import asyncio
import sys

from .runner import ProfileCardsRunner


def parse_args():
    """parses command line arguments"""
    parser = argparse.ArgumentParser(
        prog="statsgen",
        description="Generate beautiful profile cards for your GitHub README"
    )

    parser.add_argument(
        "--config", "-c",
        default=".github/config/profile.yml",
        help="path to configuration file (default: .github/config/profile.yml)"
    )

    parser.add_argument(
        "--theme", "-t",
        choices=["dark", "light", "all"],
        default="all",
        help="which theme to generate (default: all)"
    )

    parser.add_argument(
        "--output", "-o",
        default="cards",
        help="output directory for generated cards (default: cards)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be generated without actually creating files"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser.parse_args()


async def main():
    """main entry point"""
    args = parse_args()

    runner = ProfileCardsRunner(
        config_path=args.config,
        output_dir=args.output,
        theme=args.theme,
        dry_run=args.dry_run
    )

    success = await runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

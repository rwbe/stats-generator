#!/usr/bin/env python3
"""
statsgen - Profile Cards Generator
run with: python main.py or python -m statsgen
"""

import asyncio
import os
import sys


async def main():
    """placeholder for the full runner"""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("ACCESS_TOKEN")
    if not token:
        print("error: GITHUB_TOKEN or ACCESS_TOKEN is required")
        sys.exit(1)

    print("statsgen - Profile Cards Generator")
    print("=" * 40)
    print("setup complete, waiting for more modules...")


if __name__ == "__main__":
    asyncio.run(main())

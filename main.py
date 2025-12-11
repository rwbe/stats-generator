#!/usr/bin/env python3
"""
statsgen - Profile cards generator
run with: python main.py or python -m statsgen
"""

import asyncio
from statsgen.runner import ProfileCardsRunner


async def main():
    """quick entry point for generating profile cards"""
    runner = ProfileCardsRunner()
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())

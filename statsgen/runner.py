#!/usr/bin/env python3
"""
main runner that orchestrates the entire card generation process
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

from .config_loader import ConfigLoader
from .github_client import GitHubClient
from .stats_collector import StatsCollector
from .card_renderer import CardRenderer
from .models import ProfileConfig


class ProfileCardsRunner:
    """orchestrates the complete card generation workflow"""

    def __init__(
        self,
        config_path: str = ".github/config/profile.yml",
        output_dir: str = "cards",
        theme: str = "all",
        dry_run: bool = False
    ):
        self.config_path = config_path
        self.output_dir = output_dir
        self.theme = theme
        self.dry_run = dry_run

    async def run(self) -> bool:
        """executes the full generation pipeline"""
        print("statsgen - Profile Cards Generator")
        print("=" * 40)

        config = self._load_config()
        if not config.username:
            print("error: no username found in config or environment")
            return False

        print(f"generating cards for: {config.username}")

        themes = self._resolve_themes(config)
        print(f"themes: {', '.join(themes)}")

        if self.dry_run:
            print("\n[dry run] would generate:")
            for t in themes:
                print(f"  - {self.output_dir}/overview{'-' + t if t != 'dark' else ''}.svg")
                print(f"  - {self.output_dir}/languages{'-' + t if t != 'dark' else ''}.svg")
            return True

        async with GitHubClient() as client:
            collector = StatsCollector(client, config)

            print("\nfetching stats from GitHub...")
            stats = await collector.collect()

            print(f"\nprofile: {stats.display_name}")
            print(f"stars: {stats.stars:,}")
            print(f"forks: {stats.forks:,}")
            print(f"contributions: {stats.contributions:,}")
            print(f"repos: {stats.repos_count}")
            print(f"lines changed: {stats.lines_changed:,}")
            print(f"views (14 days): {stats.views:,}")
            print(f"languages: {len(stats.languages)}")

            renderer = CardRenderer(output_dir=self.output_dir)

            print("\ngenerating cards...")
            for t in themes:
                suffix = f"-{t}" if t != "dark" else ""

                overview = renderer.render_overview(stats, t)
                overview_path = renderer.save(overview, f"overview{suffix}.svg")
                print(f"  created: {overview_path}")

                languages = renderer.render_languages(stats, t)
                lang_path = renderer.save(languages, f"languages{suffix}.svg")
                print(f"  created: {lang_path}")

        print("\n" + "=" * 40)
        print("done! cards are ready in the output folder")

        return True

    def _load_config(self) -> ProfileConfig:
        """loads configuration from file or environment"""
        loader = ConfigLoader(self.config_path)
        return loader.load()

    def _resolve_themes(self, config: ProfileConfig) -> List[str]:
        """determines which themes to generate"""
        if self.theme == "all":
            return config.themes
        return [self.theme]

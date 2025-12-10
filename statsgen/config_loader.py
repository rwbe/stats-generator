#!/usr/bin/env python3
"""
loads and validates configuration from YAML files
"""

import os
from pathlib import Path
from typing import Optional

import yaml

from .models import ProfileConfig, CardConfig


class ConfigLoader:
    """handles loading profile configuration from various sources"""

    def __init__(self, config_path: str = ".github/config/profile.yml"):
        self.config_path = Path(config_path)

    def load(self) -> ProfileConfig:
        """loads config from file, falls back to env vars if file doesn't exist"""
        if self.config_path.exists():
            return self._load_from_file()
        return self._load_from_env()

    def _load_from_file(self) -> ProfileConfig:
        """parses YAML config file"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        profile = data.get("profile", {})
        display = data.get("display", {})
        filters = data.get("filters", {})
        cards = data.get("cards", {})

        username = self._resolve_env(profile.get("username", ""))
        if not username:
            username = os.getenv("GITHUB_REPOSITORY_OWNER", "")

        return ProfileConfig(
            username=username,
            themes=display.get("themes", ["dark", "light"]),
            max_languages=display.get("max_languages", 8),
            exclude_repos=filters.get("exclude_repos", []),
            exclude_languages=filters.get("exclude_languages", []),
            exclude_forks=filters.get("exclude_forks", False),
            overview_card=self._parse_card_config(cards.get("overview", {})),
            languages_card=self._parse_card_config(cards.get("languages", {}))
        )

    def _load_from_env(self) -> ProfileConfig:
        """builds config from environment variables"""
        username = os.getenv("GITHUB_REPOSITORY_OWNER", os.getenv("GITHUB_ACTOR", ""))

        exclude_repos = []
        if excluded := os.getenv("EXCLUDED", ""):
            exclude_repos = [r.strip() for r in excluded.split(",") if r.strip()]

        exclude_langs = []
        if excluded_langs := os.getenv("EXCLUDED_LANGS", ""):
            exclude_langs = [l.strip() for l in excluded_langs.split(",") if l.strip()]

        exclude_forks = os.getenv("EXCLUDE_FORKED_REPOS", "").lower() == "true"

        return ProfileConfig(
            username=username,
            exclude_repos=exclude_repos,
            exclude_languages=exclude_langs,
            exclude_forks=exclude_forks
        )

    def _parse_card_config(self, data: dict) -> CardConfig:
        """converts dict to CardConfig"""
        return CardConfig(
            enabled=data.get("enabled", True),
            style=data.get("style", "default"),
            options={k: v for k, v in data.items() if k not in ("enabled", "style")}
        )

    def _resolve_env(self, value: str) -> str:
        """resolves ${VAR} patterns to environment variables"""
        if value.startswith("${") and value.endswith("}"):
            var_name = value[2:-1]
            return os.getenv(var_name, "")
        return value

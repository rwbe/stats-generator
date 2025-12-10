#!/usr/bin/env python3
"""
renders profile cards using Jinja2 templates
supports multiple themes and card types
"""

import os
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import ProfileStats


class CardRenderer:
    """generates SVG cards from templates and stats"""

    def __init__(
        self,
        templates_dir: str = "assets/templates",
        output_dir: str = "cards"
    ):
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)

        self._env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["svg", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True
        )

        self._env.filters["format_number"] = self._format_number

    def render_overview(self, stats: ProfileStats, theme: str = "dark") -> str:
        """renders the overview stats card"""
        template_name = f"overview-{theme}.svg" if theme != "dark" else "overview.svg"

        if not (self.templates_dir / template_name).exists():
            template_name = "overview.svg"

        template = self._env.get_template(template_name)

        return template.render(
            name=stats.display_name,
            username=stats.username,
            stars=self._format_number(stats.stars),
            forks=self._format_number(stats.forks),
            contributions=self._format_number(stats.contributions),
            lines_changed=self._format_number(stats.lines_changed),
            views=self._format_number(stats.views),
            repos=self._format_number(stats.repos_count)
        )

    def render_languages(self, stats: ProfileStats, theme: str = "dark") -> str:
        """renders the languages breakdown card"""
        template_name = f"languages-{theme}.svg" if theme != "dark" else "languages.svg"

        if not (self.templates_dir / template_name).exists():
            template_name = "languages.svg"

        template = self._env.get_template(template_name)

        languages = stats.top_languages
        progress_bar = self._build_progress_bar(languages)
        lang_list = self._build_language_list(languages)

        return template.render(
            progress_bar=progress_bar,
            lang_list=lang_list,
            languages=languages
        )

    def save(self, content: str, filename: str) -> Path:
        """saves rendered content to file"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def _build_progress_bar(self, languages: List) -> str:
        """creates the stacked progress bar SVG elements"""
        parts = []
        x_offset = 0
        total_width = 300

        for lang in languages[:8]:
            width = (lang.percentage / 100) * total_width
            if width < 1:
                width = 1
            parts.append(
                f'<rect x="{x_offset}" y="0" width="{width}" height="8" fill="{lang.color}"/>'
            )
            x_offset += width

        return "".join(parts)

    def _build_language_list(self, languages: List) -> str:
        """creates the language legend SVG elements"""
        parts = []
        col1_x, col2_x = 20, 175
        start_y = 70
        row_height = 18

        for i, lang in enumerate(languages[:8]):
            col = i % 2
            row = i // 2
            x = col1_x if col == 0 else col2_x
            y = start_y + (row * row_height)

            parts.append(f'''
  <g transform="translate({x}, {y})">
    <circle cx="5" cy="5" r="5" fill="{lang.color}"/>
    <text class="lang-name" x="14" y="8">{lang.name}</text>
    <text class="lang-percent" x="90" y="8">{lang.percentage:.1f}%</text>
  </g>''')

        return "".join(parts)

    @staticmethod
    def _format_number(n: int) -> str:
        """formats numbers with comma separators"""
        return f"{n:,}"

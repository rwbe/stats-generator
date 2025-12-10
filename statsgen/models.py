#!/usr/bin/env python3
"""
data models for profile statistics
using dataclasses for clean, typed data structures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LanguageStats:
    """stats for a single programming language"""
    name: str
    size: int
    color: str
    percentage: float = 0.0


@dataclass
class ProfileStats:
    """aggregated profile statistics"""
    username: str
    display_name: str
    stars: int = 0
    forks: int = 0
    contributions: int = 0
    repos_count: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    views: int = 0
    languages: List[LanguageStats] = field(default_factory=list)

    @property
    def lines_changed(self) -> int:
        """total lines added + deleted"""
        return self.lines_added + self.lines_deleted

    @property
    def top_languages(self) -> List[LanguageStats]:
        """returns top 8 languages by size"""
        return sorted(self.languages, key=lambda x: x.size, reverse=True)[:8]


@dataclass
class CardConfig:
    """configuration for a single card type"""
    enabled: bool = True
    style: str = "default"
    options: Dict = field(default_factory=dict)


@dataclass
class ProfileConfig:
    """complete profile configuration"""
    username: str
    themes: List[str] = field(default_factory=lambda: ["dark", "light"])
    max_languages: int = 8
    exclude_repos: List[str] = field(default_factory=list)
    exclude_languages: List[str] = field(default_factory=list)
    exclude_forks: bool = False
    overview_card: CardConfig = field(default_factory=CardConfig)
    languages_card: CardConfig = field(default_factory=CardConfig)

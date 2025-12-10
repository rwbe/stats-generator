#!/usr/bin/env python3
"""
collects GitHub profile statistics using the API client
aggregates data from repos, contributions, and traffic
"""

from typing import List, Optional, Set

from .github_client import GitHubClient
from .models import ProfileStats, LanguageStats, ProfileConfig
from .colors import get_color


class StatsCollector:
    """fetches and aggregates GitHub profile statistics"""

    def __init__(self, client: GitHubClient, config: ProfileConfig):
        self.client = client
        self.config = config
        self._repos: Set[str] = set()

    async def collect(self) -> ProfileStats:
        """fetches all stats and returns aggregated ProfileStats"""
        stats = ProfileStats(
            username=self.config.username,
            display_name=self.config.username
        )

        await self._collect_repos(stats)
        await self._collect_contributions(stats)
        await self._collect_code_stats(stats)
        await self._collect_traffic(stats)

        self._calculate_percentages(stats)

        return stats

    async def _collect_repos(self, stats: ProfileStats) -> None:
        """fetches repository data including stars, forks, and languages"""
        owned_cursor = None
        contrib_cursor = None
        languages_map = {}

        while True:
            query = self._build_repos_query(owned_cursor, contrib_cursor)
            result = await self.client.graphql(query)
            viewer = result.get("data", {}).get("viewer", {})

            if not stats.display_name or stats.display_name == self.config.username:
                stats.display_name = viewer.get("name") or viewer.get("login", self.config.username)

            owned = viewer.get("repositories", {})
            contrib = viewer.get("repositoriesContributedTo", {})

            repos = owned.get("nodes", [])
            if not self.config.exclude_forks:
                repos += contrib.get("nodes", [])

            for repo in repos:
                if not repo:
                    continue

                name = repo.get("nameWithOwner")
                if name in self._repos or name in self.config.exclude_repos:
                    continue

                self._repos.add(name)
                stats.stars += repo.get("stargazerCount", 0)
                stats.forks += repo.get("forkCount", 0)

                for edge in repo.get("languages", {}).get("edges", []):
                    lang_name = edge.get("node", {}).get("name", "Other")
                    if lang_name.lower() in {l.lower() for l in self.config.exclude_languages}:
                        continue

                    size = edge.get("size", 0)
                    api_color = edge.get("node", {}).get("color")
                    color = get_color(lang_name, api_color or "#858585")

                    if lang_name in languages_map:
                        languages_map[lang_name].size += size
                    else:
                        languages_map[lang_name] = LanguageStats(
                            name=lang_name,
                            size=size,
                            color=color
                        )

            has_more_owned = owned.get("pageInfo", {}).get("hasNextPage", False)
            has_more_contrib = contrib.get("pageInfo", {}).get("hasNextPage", False)

            if has_more_owned or has_more_contrib:
                owned_cursor = owned.get("pageInfo", {}).get("endCursor", owned_cursor)
                contrib_cursor = contrib.get("pageInfo", {}).get("endCursor", contrib_cursor)
            else:
                break

        stats.repos_count = len(self._repos)
        stats.languages = list(languages_map.values())

    async def _collect_contributions(self, stats: ProfileStats) -> None:
        """fetches contribution counts across all years"""
        years_query = "{ viewer { contributionsCollection { contributionYears } } }"
        result = await self.client.graphql(years_query)
        years = (
            result.get("data", {})
            .get("viewer", {})
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )

        if not years:
            return

        yearly_query = self._build_yearly_query(years)
        result = await self.client.graphql(yearly_query)
        viewer = result.get("data", {}).get("viewer", {})

        for key, value in viewer.items():
            if key.startswith("y"):
                stats.contributions += (
                    value.get("contributionCalendar", {})
                    .get("totalContributions", 0)
                )

    async def _collect_code_stats(self, stats: ProfileStats) -> None:
        """fetches lines added/deleted from contributor stats"""
        for repo in self._repos:
            result = await self.client.rest(f"/repos/{repo}/stats/contributors")
            if not isinstance(result, list):
                continue

            for contrib in result:
                if not isinstance(contrib, dict):
                    continue
                author = contrib.get("author", {})
                if not isinstance(author, dict):
                    continue
                if author.get("login") != self.config.username:
                    continue

                for week in contrib.get("weeks", []):
                    stats.lines_added += week.get("a", 0)
                    stats.lines_deleted += week.get("d", 0)

    async def _collect_traffic(self, stats: ProfileStats) -> None:
        """fetches view counts from traffic API"""
        for repo in self._repos:
            result = await self.client.rest(f"/repos/{repo}/traffic/views")
            if isinstance(result, dict):
                for view in result.get("views", []):
                    stats.views += view.get("count", 0)

    def _calculate_percentages(self, stats: ProfileStats) -> None:
        """calculates language percentages based on size"""
        total = sum(lang.size for lang in stats.languages)
        if total > 0:
            for lang in stats.languages:
                lang.percentage = (lang.size / total) * 100

    def _build_repos_query(
        self,
        owned_cursor: Optional[str] = None,
        contrib_cursor: Optional[str] = None
    ) -> str:
        """constructs GraphQL query for repositories"""
        owned_after = f'"{owned_cursor}"' if owned_cursor else "null"
        contrib_after = f'"{contrib_cursor}"' if contrib_cursor else "null"

        return f"""{{
  viewer {{
    login
    name
    repositories(first: 100, orderBy: {{field: UPDATED_AT, direction: DESC}}, isFork: false, after: {owned_after}) {{
      pageInfo {{ hasNextPage endCursor }}
      nodes {{
        nameWithOwner
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
          edges {{ size node {{ name color }} }}
        }}
      }}
    }}
    repositoriesContributedTo(first: 100, includeUserRepositories: false, orderBy: {{field: UPDATED_AT, direction: DESC}}, contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY, PULL_REQUEST_REVIEW], after: {contrib_after}) {{
      pageInfo {{ hasNextPage endCursor }}
      nodes {{
        nameWithOwner
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
          edges {{ size node {{ name color }} }}
        }}
      }}
    }}
  }}
}}"""

    def _build_yearly_query(self, years: List[int]) -> str:
        """constructs query for fetching contributions per year"""
        parts = []
        for year in years:
            parts.append(f"""
    y{year}: contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year + 1}-01-01T00:00:00Z") {{
      contributionCalendar {{ totalContributions }}
    }}""")
        return "{ viewer {" + "".join(parts) + " } }"

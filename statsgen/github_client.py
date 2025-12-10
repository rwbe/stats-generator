#!/usr/bin/env python3
"""
GitHub API client with rate limiting and retry logic
handles both GraphQL and REST endpoints
"""

import asyncio
import os
from typing import Any, Dict, Optional

import aiohttp


class RateLimitError(Exception):
    """raised when we hit GitHub's rate limit"""
    pass


class GitHubClient:
    """async client for GitHub API with automatic retry and rate limit handling"""

    GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
    REST_ENDPOINT = "https://api.github.com"

    def __init__(
        self,
        token: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        max_concurrent: int = 10,
        retry_count: int = 3
    ):
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("ACCESS_TOKEN")
        self._session = session
        self._owns_session = session is None
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._retry_count = retry_count

    async def __aenter__(self):
        if self._owns_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self._owns_session and self._session:
            await self._session.close()

    def _headers(self, use_bearer: bool = True) -> Dict[str, str]:
        """builds auth headers"""
        prefix = "Bearer" if use_bearer else "token"
        return {"Authorization": f"{prefix} {self.token}"}

    async def graphql(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """executes a GraphQL query with retry logic"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        async with self._semaphore:
            for attempt in range(self._retry_count):
                try:
                    async with self._session.post(
                        self.GRAPHQL_ENDPOINT,
                        headers=self._headers(use_bearer=True),
                        json=payload
                    ) as resp:
                        if resp.status == 403:
                            raise RateLimitError("GitHub API rate limit exceeded")
                        return await resp.json()
                except aiohttp.ClientError:
                    if attempt < self._retry_count - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise
        return {}

    async def rest(self, path: str, params: Optional[Dict] = None) -> Any:
        """makes a REST API call with retry for 202 (processing) responses"""
        url = f"{self.REST_ENDPOINT}/{path.lstrip('/')}"

        async with self._semaphore:
            for _ in range(30):
                async with self._session.get(
                    url,
                    headers=self._headers(use_bearer=False),
                    params=params
                ) as resp:
                    if resp.status == 202:
                        await asyncio.sleep(2)
                        continue
                    if resp.status == 403:
                        raise RateLimitError("GitHub API rate limit exceeded")
                    return await resp.json()
        return {}

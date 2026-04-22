import asyncio
from typing import Any

import arxiv


def _fetch_arxiv_sync(topic: str, max_papers: int) -> list[dict[str, Any]]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_papers,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results: list[dict[str, Any]] = []
    for r in client.results(search):
        results.append(
            {
                "title": r.title,
                "authors": [str(a) for a in r.authors],
                "abstract": r.summary,
                "url": r.entry_id,
                "published": r.published.isoformat(),
                "pdf_url": r.pdf_url,
            }
        )
    return results


async def fetch_arxiv(topic: str, max_papers: int = 5) -> list[dict[str, Any]]:
    """Fetch papers from ArXiv for a given topic."""
    return await asyncio.to_thread(_fetch_arxiv_sync, topic, max_papers)

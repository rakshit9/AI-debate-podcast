import httpx


async def read_url(url: str, timeout: int = 30) -> str:
    """Fetch and return the text content of a URL."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

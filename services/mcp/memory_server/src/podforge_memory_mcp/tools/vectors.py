import uuid
from typing import Any

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..config import get_settings


async def _get_embedding(text: str) -> list[float]:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )
    return response.data[0].embedding


async def _ensure_collection(qdrant: AsyncQdrantClient, name: str) -> None:
    settings = get_settings()
    try:
        await qdrant.get_collection(name)
    except Exception:
        await qdrant.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,
                distance=Distance.COSINE,
            ),
        )


async def get_host_memory(host_id: str, query: str, k: int = 5) -> list[dict[str, Any]]:
    """Semantic search over a host's accumulated memories."""
    settings = get_settings()
    qdrant = AsyncQdrantClient(url=settings.qdrant_url)
    await _ensure_collection(qdrant, settings.host_memory_collection)

    query_vec = await _get_embedding(query)
    results = await qdrant.search(  # type: ignore[attr-defined]
        collection_name=settings.host_memory_collection,
        query_vector=query_vec,
        query_filter=Filter(must=[FieldCondition(key="host_id", match=MatchValue(value=host_id))]),
        limit=k,
    )
    return [
        {
            "content": r.payload.get("content", "") if r.payload else "",
            "score": r.score,
            "metadata": {k: v for k, v in (r.payload or {}).items() if k != "content"},
        }
        for r in results
    ]


async def update_host_memory(host_id: str, content: str) -> None:
    """Upsert a memory entry for a host into Qdrant."""
    settings = get_settings()
    qdrant = AsyncQdrantClient(url=settings.qdrant_url)
    await _ensure_collection(qdrant, settings.host_memory_collection)

    embedding = await _get_embedding(content)
    await qdrant.upsert(
        collection_name=settings.host_memory_collection,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"host_id": host_id, "content": content},
            )
        ],
    )


async def search_past_episodes(show_id: str, query: str, k: int = 5) -> list[dict[str, Any]]:
    """Semantic search over past episodes for a show."""
    settings = get_settings()
    qdrant = AsyncQdrantClient(url=settings.qdrant_url)
    await _ensure_collection(qdrant, settings.episodes_collection)

    query_vec = await _get_embedding(query)
    results = await qdrant.search(  # type: ignore[attr-defined]
        collection_name=settings.episodes_collection,
        query_vector=query_vec,
        query_filter=Filter(must=[FieldCondition(key="show_id", match=MatchValue(value=show_id))]),
        limit=k,
    )
    return [
        {
            "episode_id": r.payload.get("episode_id", "") if r.payload else "",
            "topic": r.payload.get("topic", "") if r.payload else "",
            "score": r.score,
        }
        for r in results
    ]


async def index_episode(show_id: str, episode_id: str, topic: str, summary: str) -> None:
    """Index an episode's summary into Qdrant for future semantic search."""
    settings = get_settings()
    qdrant = AsyncQdrantClient(url=settings.qdrant_url)
    await _ensure_collection(qdrant, settings.episodes_collection)

    embedding = await _get_embedding(summary)
    await qdrant.upsert(
        collection_name=settings.episodes_collection,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "show_id": show_id,
                    "episode_id": episode_id,
                    "topic": topic,
                    "summary": summary,
                },
            )
        ],
    )

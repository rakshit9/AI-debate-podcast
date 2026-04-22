import asyncio
import uuid
from typing import Any

import boto3

from ..config import get_settings


def _upload_sync(audio_bytes: bytes, key: str) -> str:
    settings = get_settings()
    s3: Any = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=audio_bytes,
        ContentType="audio/mpeg",
    )
    return f"{settings.s3_endpoint}/{settings.s3_bucket}/{key}"


async def upload_audio(audio_bytes: bytes, prefix: str = "audio") -> str:
    """Upload audio bytes to S3/MinIO and return the public URL."""
    key = f"{prefix}/{uuid.uuid4()}.mp3"
    return await asyncio.to_thread(_upload_sync, audio_bytes, key)

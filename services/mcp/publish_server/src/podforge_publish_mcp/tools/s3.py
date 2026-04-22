import asyncio
import uuid
from pathlib import Path
from typing import Any

import boto3

from ..config import get_settings


def _upload_sync(file_path: str, bucket: str, key: str) -> str:
    settings = get_settings()
    s3: Any = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    content_type = "audio/mpeg" if file_path.endswith(".mp3") else "application/octet-stream"
    s3.upload_file(file_path, bucket, key, ExtraArgs={"ContentType": content_type})
    return f"{settings.s3_endpoint}/{bucket}/{key}"


async def upload_s3(file_path: str, bucket: str | None = None) -> str:
    """Upload a local file to S3/MinIO. Returns the public URL."""
    settings = get_settings()
    target_bucket = bucket or settings.s3_bucket
    suffix = Path(file_path).suffix
    key = f"episodes/{uuid.uuid4()}{suffix}"
    return await asyncio.to_thread(_upload_sync, file_path, target_bucket, key)

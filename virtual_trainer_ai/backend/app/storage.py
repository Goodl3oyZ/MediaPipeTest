"""MinIO/S3 storage helper utilities."""

from __future__ import annotations

from typing import BinaryIO

import boto3

from .config import settings


_session = boto3.session.Session()
_client = _session.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    region_name=settings.s3_region,
    use_ssl=settings.s3_use_ssl,
)


def presigned_put(mime: str, filename: str) -> tuple[str, str]:
    key = filename
    url = _client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.s3_bucket, "Key": key, "ContentType": mime},
        ExpiresIn=3600,
    )
    return url, key


def presigned_get(key: str) -> str:
    return _client.generate_presigned_url(
        "get_object", Params={"Bucket": settings.s3_bucket, "Key": key}, ExpiresIn=3600
    )


def upload_bytes(data: bytes, key: str, mime: str) -> None:
    _client.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=mime)


def exists(key: str) -> bool:
    try:
        _client.head_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except Exception:
        return False

# TODO: implement S3/MinIO client utilities

from typing import BinaryIO


def upload_file(file_obj: BinaryIO, filename: str) -> str:
    """Upload file and return URL. Placeholder implementation."""
    # In production, upload to S3/MinIO and return the object URL
    return f"https://storage.example.com/{filename}"

"""S3-compatible object storage service for call recordings."""

import asyncio
from typing import Any

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class StorageService:
    """S3-compatible storage for uploading/downloading recordings.

    Uses boto3 synchronous client wrapped in asyncio.to_thread()
    (same pattern as the Twilio SDK integration).
    """

    def __init__(self) -> None:
        client_kwargs: dict[str, Any] = {
            "service_name": "s3",
            "region_name": settings.s3_region,
        }
        if settings.s3_endpoint_url:
            client_kwargs["endpoint_url"] = settings.s3_endpoint_url
        if settings.s3_access_key_id:
            client_kwargs["aws_access_key_id"] = settings.s3_access_key_id
        if settings.s3_secret_access_key:
            client_kwargs["aws_secret_access_key"] = (
                settings.s3_secret_access_key.get_secret_value()
            )

        self._client = boto3.client(**client_kwargs)
        self._bucket = settings.s3_bucket_name

    async def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't already exist."""

        def _ensure() -> None:
            try:
                self._client.head_bucket(Bucket=self._bucket)
                logger.info("S3 bucket '{}' already exists", self._bucket)
            except ClientError as e:
                error_code = int(e.response.get("Error", {}).get("Code", 0))
                if error_code == 404:
                    self._client.create_bucket(Bucket=self._bucket)
                    logger.info("Created S3 bucket '{}'", self._bucket)
                else:
                    raise

        await asyncio.to_thread(_ensure)

    async def upload_recording(
        self, key: str, data: bytes, content_type: str = "audio/wav"
    ) -> str:
        """Upload a recording to S3.

        Args:
            key: Object key (e.g., "recordings/{call_id}.wav")
            data: Raw file bytes
            content_type: MIME type of the file

        Returns:
            The S3 URL of the uploaded object.
        """

        def _upload() -> str:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
            base = settings.s3_public_url or settings.s3_endpoint_url
            return f"{base}/{self._bucket}/{key}"

        url = await asyncio.to_thread(_upload)
        logger.info("Uploaded recording to s3://{}/{}", self._bucket, key)
        return url

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned download URL.

        Args:
            key: Object key
            expires_in: URL validity in seconds (default 1 hour)

        Returns:
            Presigned URL string.
        """

        def _presign() -> str:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in,
            )

        return await asyncio.to_thread(_presign)

    async def delete_recording(self, key: str) -> None:
        """Delete an object from S3.

        Args:
            key: Object key to delete
        """

        def _delete() -> None:
            self._client.delete_object(Bucket=self._bucket, Key=key)

        await asyncio.to_thread(_delete)
        logger.info("Deleted recording s3://{}/{}", self._bucket, key)

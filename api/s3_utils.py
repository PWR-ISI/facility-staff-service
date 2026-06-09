"""S3 (LocalStack) helpers for doctor profile photos."""
import json
import logging
from uuid import uuid4

from django.conf import settings
from common.aws import aws_client

logger = logging.getLogger(__name__)


def _public_read_policy(bucket: str) -> str:
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket}/*"],
        }],
    })


def _ensure_bucket(s3, bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        try:
            s3.create_bucket(Bucket=bucket)
            s3.put_bucket_policy(Bucket=bucket, Policy=_public_read_policy(bucket))
        except Exception as exc:  # bucket may already exist / race
            logger.warning("Could not create/configure bucket %s: %s", bucket, exc)


def upload_staff_photo(file_obj, user_id: str) -> str:
    """Upload a doctor photo to the LocalStack S3 bucket and return a public URL."""
    bucket = getattr(settings, "STAFF_PHOTO_BUCKET", "isi-files") or "isi-files"
    s3 = aws_client("s3")
    _ensure_bucket(s3, bucket)

    safe_name = getattr(file_obj, "name", "photo").replace("/", "_")
    key = f"doctors/{user_id}/{uuid4().hex}_{safe_name}"
    s3.upload_fileobj(
        file_obj, bucket, key,
        ExtraArgs={"ContentType": getattr(file_obj, "content_type", "application/octet-stream")},
    )
    logger.info("Uploaded doctor photo to s3://%s/%s", bucket, key)

    # Browser-reachable URL (LocalStack is served on the host at S3_PUBLIC_URL).
    base = (getattr(settings, "S3_PUBLIC_URL", "") or getattr(settings, "AWS_ENDPOINT_URL", "") or "").rstrip("/")
    if base:
        return f"{base}/{bucket}/{key}"
    return f"https://{bucket}.s3.amazonaws.com/{key}"

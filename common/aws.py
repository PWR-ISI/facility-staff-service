"""
boto3 client factory pointing at LocalStack when AWS_ENDPOINT_URL is set.
Mirrors schedule-service/common/aws.py — all AWS calls MUST go through this so
they hit the local emulation, never real AWS.
"""
import boto3
from django.conf import settings


def aws_client(service: str):
    kwargs = {"region_name": getattr(settings, "AWS_REGION", "us-east-1")}
    endpoint = getattr(settings, "AWS_ENDPOINT_URL", None)
    if endpoint:
        kwargs["endpoint_url"] = endpoint
        kwargs["aws_access_key_id"] = "test"
        kwargs["aws_secret_access_key"] = "test"
    return boto3.client(service, **kwargs)

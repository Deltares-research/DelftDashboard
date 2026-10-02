"""Helpers for the DelftDashboard remote data store.

The store is an S3 or S3-compatible bucket holding the remote data
(bathymetry catalog + tiles/COGs, tide models, ...). It is configured via
three ``app.config`` keys, all overridable in ``delftdashboard.ini``:

* ``s3_bucket``   - bucket name
* ``s3_endpoint`` - endpoint URL for S3-compatible stores (e.g.
  ``https://s3.deltares.nl``). Leave EMPTY for AWS S3.
* ``s3_region``   - AWS region, only used when ``s3_endpoint`` is empty.

To switch back to the old AWS bucket, put this in ``delftdashboard.ini``::

    s3_bucket=deltares-ddb
    s3_endpoint=
"""

from delftdashboard.app import app


def have_aws_credentials() -> bool:
    """Return True when AWS credentials are resolvable from the environment.

    Uses the standard boto3/botocore credential chain: ``AWS_ACCESS_KEY_ID`` /
    ``AWS_SECRET_ACCESS_KEY`` environment variables, a shared credentials file
    (``~/.aws/credentials``), an ``AWS_PROFILE``, etc. When credentials are
    present, requests are signed; otherwise the store is accessed anonymously
    (which only works for public buckets/prefixes).
    """
    import botocore.session

    try:
        return botocore.session.get_session().get_credentials() is not None
    except Exception:
        return False


def s3_client():
    """Return a boto3 client for the configured store.

    Signs requests when AWS credentials are available (see
    :func:`have_aws_credentials`), otherwise falls back to unsigned/anonymous
    access for public data.
    """
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config

    endpoint = app.config.get("s3_endpoint") or None
    if have_aws_credentials():
        return boto3.client("s3", endpoint_url=endpoint)
    return boto3.client(
        "s3", endpoint_url=endpoint, config=Config(signature_version=UNSIGNED)
    )


def s3_filesystem():
    """Return an s3fs filesystem for the configured store.

    Uses credentials when available, otherwise anonymous access.
    """
    import s3fs

    endpoint = app.config.get("s3_endpoint") or None
    anon = not have_aws_credentials()
    kwargs = {"anon": anon}
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    return s3fs.S3FileSystem(**kwargs)


def s3_http_url(key: str) -> str:
    """Return the public HTTPS URL for *key* on the configured store.

    Uses path-style addressing for S3-compatible stores
    (``<endpoint>/<bucket>/<key>``) and virtual-hosted style for AWS
    (``https://<bucket>.s3.<region>.amazonaws.com/<key>``).
    """
    bucket = app.config.get("s3_bucket", "delftdashboard")
    endpoint = app.config.get("s3_endpoint")
    if endpoint:
        return f"{endpoint.rstrip('/')}/{bucket}/{key}"
    region = app.config.get("s3_region", "eu-west-1")
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

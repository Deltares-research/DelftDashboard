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


def s3_client():
    """Return an unsigned boto3 client for the configured store."""
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config

    endpoint = app.config.get("s3_endpoint") or None
    return boto3.client(
        "s3", endpoint_url=endpoint, config=Config(signature_version=UNSIGNED)
    )


def s3_filesystem():
    """Return an anonymous s3fs filesystem for the configured store."""
    import s3fs

    endpoint = app.config.get("s3_endpoint") or None
    if endpoint:
        return s3fs.S3FileSystem(anon=True, endpoint_url=endpoint)
    return s3fs.S3FileSystem(anon=True)


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

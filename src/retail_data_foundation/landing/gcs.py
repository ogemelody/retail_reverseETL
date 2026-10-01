from __future__ import annotations

import hashlib
import json

from .protocol import ObjectResult


class GCSLanding:
    def __init__(self, bucket: str, prefix: str = "", *, client=None, region: str = "europe-west3", storage_class: str = "STANDARD"):
        if not bucket:
            raise ValueError("bucket is required")
        self.bucket_name, self.prefix = bucket, prefix.strip("/")
        self.region, self.storage_class = region, storage_class
        if client is None:
            try:
                from google.cloud import storage
            except ImportError as exc:
                raise RuntimeError("google-cloud-storage is required for live GCS landing") from exc
            client = storage.Client()
        self.client = client
        self.bucket = client.bucket(bucket)

    def _uri(self, name: str) -> str:
        return f"gs://{self.bucket_name}/{name}"

    def put_text(self, name: str, text: str, records: int) -> ObjectResult:
        digest = hashlib.sha256(text.encode()).hexdigest()
        blob = self.bucket.blob(name)
        existing = getattr(blob, "exists", lambda: False)()
        if existing:
            reload_blob = getattr(blob, "reload", None)
            if reload_blob:
                reload_blob()
            existing_hash = getattr(blob, "metadata", None) or {}
            if existing_hash.get("sha256") == digest or self._existing_text_matches(blob, text):
                return ObjectResult(self._uri(name), digest, len(text.encode()), records, True)
            raise FileExistsError(f"GCS object exists with different checksum: {self._uri(name)}")
        blob.metadata = {"sha256": digest, "record_count": str(records), "storage_class": self.storage_class, "region": self.region}
        blob.upload_from_string(text, content_type="application/x-ndjson")
        return ObjectResult(self._uri(name), digest, len(text.encode()), records)

    def put_json(self, name: str, value: dict, *, overwrite: bool = False) -> ObjectResult:
        text = json.dumps(value, sort_keys=True, indent=2)
        digest = hashlib.sha256(text.encode()).hexdigest()
        blob = self.bucket.blob(name)
        if getattr(blob, "exists", lambda: False)():
            if not overwrite and self._existing_text_matches(blob, text):
                return ObjectResult(self._uri(name), digest, len(text.encode()), 1, True)
            if not overwrite:
                raise FileExistsError(f"GCS object exists with different checksum: {self._uri(name)}")
        blob.metadata = {"sha256": digest, "record_count": "1", "storage_class": self.storage_class, "region": self.region}
        blob.upload_from_string(text, content_type="application/json")
        return ObjectResult(self._uri(name), digest, len(text.encode()), 1)

    @staticmethod
    def _existing_text_matches(blob, expected: str) -> bool:
        download = getattr(blob, "download_as_text", None)
        if not download:
            return False
        return download() == expected

    def get_json(self, name: str) -> dict | None:
        blob = self.bucket.blob(name)
        if not getattr(blob, "exists", lambda: False)():
            return None
        download = getattr(blob, "download_as_text", None)
        if not download:
            raise RuntimeError("GCS client does not support reading control objects")
        return json.loads(download())

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class Config:
    seed: int = 7
    run_id: str = "demo-001"
    start_timestamp: str = "2026-01-01T09:00:00Z"
    batch_count: int = 3
    batch_interval_hours: int = 24
    customers: int = 1000
    products: int = 50
    behavioral_events_per_customer: int = 10
    bucket: str = ""
    prefix: str = ""
    region: str = "europe-west3"
    storage_class: str = "STANDARD"
    part_records: int = 500
    identity_quality_mix: tuple[str, ...] = ("strong", "incomplete", "conflicting", "anonymous_only", "single_source", "multi_source")
    anomaly_scenarios: tuple[str, ...] = ()
    schema_transition_batch: int = 2

    @property
    def start(self) -> datetime:
        return datetime.fromisoformat(self.start_timestamp.replace("Z", "+00:00"))

    def ingestion_time(self, sequence: int) -> datetime:
        return self.start + timedelta(hours=self.batch_interval_hours * sequence)


def load_config(path: str | Path, *, bucket: str | None = None) -> Config:
    with Path(path).open("rb") as handle:
        raw = tomllib.load(handle)
    generation = raw.get("generation", raw)
    landing = raw.get("landing", {})
    identity = raw.get("identity", {})
    anomalies = raw.get("anomalies", {})
    configured_bucket = bucket or os.getenv("GCS_BUCKET") or landing.get("bucket", "")
    values = {
        "seed": generation.get("seed", 7),
        "run_id": generation.get("run_id", "demo-001"),
        "start_timestamp": generation.get("start_timestamp", "2026-01-01T09:00:00Z"),
        "batch_count": generation.get("batch_count", 3),
        "batch_interval_hours": generation.get("batch_interval_hours", 24),
        "customers": generation.get("customers", 1000),
        "products": generation.get("products", 50),
        "behavioral_events_per_customer": generation.get("behavioral_events_per_customer", 10),
        "bucket": configured_bucket,
        "prefix": os.getenv("GCS_PREFIX", landing.get("prefix", "")),
        "region": os.getenv("GCS_REGION", landing.get("region", "europe-west3")),
        "storage_class": os.getenv("GCS_STORAGE_CLASS", landing.get("storage_class", "STANDARD")),
        "part_records": generation.get("part_records", 500),
        "identity_quality_mix": tuple(identity.get("quality_mix", Config.identity_quality_mix)),
        "anomaly_scenarios": tuple(anomalies.get("scenarios", ())),
        "schema_transition_batch": generation.get("schema_transition_batch", 2),
    }
    config = Config(**values)
    if not config.bucket:
        raise ValueError("A GCS bucket is required via --bucket, GCS_BUCKET, or [landing].bucket")
    if config.batch_count < 1 or config.customers < 1 or config.part_records < 1:
        raise ValueError("batch_count, customers, and part_records must be positive")
    return config

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectResult:
    uri: str
    checksum: str
    bytes: int
    records: int
    reused: bool = False


def object_name(prefix, source_system, entity, ingestion_timestamp, batch_id, part, run_id=None):
    day = ingestion_timestamp[:10]
    year, month, date = day.split("-")
    root = f"{prefix.strip('/')}/" if prefix.strip("/") else ""
    run_root = f"run_id={run_id}/" if run_id else ""
    return f"{root}raw/{run_root}{source_system}/{entity}/year={year}/month={month}/day={date}/batch_id={batch_id}/part-{part:03d}.jsonl"


def control_name(prefix, category, suffix):
    root = f"{prefix.strip('/')}/" if prefix.strip("/") else ""
    return f"{root}raw/_control/{category}/{suffix}.json"

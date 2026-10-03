from __future__ import annotations

import hashlib
import json


def stream_jsonl_parts(records, part_records: int = 500):
    chunk: list[str] = []
    for record in records:
        raw = record.raw() if hasattr(record, "raw") else record
        chunk.append(json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
        if len(chunk) >= part_records:
            yield "\n".join(chunk) + "\n", len(chunk)
            chunk = []
    if chunk:
        yield "\n".join(chunk) + "\n", len(chunk)


def checksum(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

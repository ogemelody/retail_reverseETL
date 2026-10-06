from __future__ import annotations

from dataclasses import replace

from ..canonical.entities import SourceObservation


def annotate_operations(records: list[SourceObservation], previous_ids: set[str] | None = None) -> list[SourceObservation]:
    previous_ids = previous_ids or set()
    seen: set[str] = set()
    result: list[SourceObservation] = []
    for record in records:
        operation = record.operation if record.operation == "delete" else ("update" if record.source_record_id in previous_ids else "insert")
        same_logical_version = any(
            prior.source_record_id == record.source_record_id
            and prior.business_event_timestamp == record.business_event_timestamp
            and prior.source_updated_at == record.source_updated_at
            and prior.payload.get("logical_version") == record.payload.get("logical_version")
            for prior in result
        )
        if record.source_record_id in seen and not same_logical_version:
            operation = "update"
        seen.add(record.source_record_id)
        result.append(replace(record, operation=operation))
    return result

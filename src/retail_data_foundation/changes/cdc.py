from __future__ import annotations

from dataclasses import replace

from ..canonical.entities import SourceObservation


def annotate_operations(records: list[SourceObservation], previous_ids: set[str] | None = None) -> list[SourceObservation]:
    previous_ids = previous_ids or set()
    seen: set[str] = set()
    result: list[SourceObservation] = []
    for record in records:
        operation = "update" if record.source_record_id in previous_ids else "insert"
        if record.source_record_id in seen:
            operation = "update"
        seen.add(record.source_record_id)
        result.append(replace(record, operation=operation))
    return result

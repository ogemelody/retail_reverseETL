from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone


def mark_late(records, ingestion_timestamp: str, threshold_hours: int = 24):
    ingestion = datetime.fromisoformat(ingestion_timestamp.replace("Z", "+00:00"))
    result = []
    for record in records:
        event_time = datetime.fromisoformat(record.business_event_timestamp.replace("Z", "+00:00"))
        late = (ingestion - event_time).total_seconds() > threshold_hours * 3600
        result.append(replace(record, late_arrival=late, late_arrival_reason="business_event_delay" if late else None))
    return result

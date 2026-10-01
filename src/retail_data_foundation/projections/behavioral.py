from __future__ import annotations

from ..canonical.entities import CanonicalWorld, SourceObservation
from ..canonical.utils import iso


def project_behavioral(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str):
    for index, journey in enumerate(world.journeys):
        anonymous_id = "anon_7842" if index == 0 else f"anon_{index + 1000}"
        user_id = "user_0001" if index == 0 else f"user_{index + 1:04d}"
        for event_index, event in enumerate(journey.events):
            event_type = event["event_type"]
            if event_type == "pos_purchased":
                continue
            payload = {
                "anonymous_id": anonymous_id,
                "user_id": user_id if event_type == "identify" else None,
                "event_type": event_type,
                "product_id": event.get("product_id"),
            }
            if event_type == "identify" and index == 0:
                payload["ecommerce_customer_id"] = "EC-93821"
            yield SourceObservation("behavioral", "events", f"BEH-{index + 1:04d}-{event_index:02d}", "insert", event["at"], event["at"], ingestion_timestamp, batch_id, "behavioral.events.v1", payload)

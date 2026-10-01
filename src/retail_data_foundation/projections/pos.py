from __future__ import annotations

from ..canonical.entities import CanonicalWorld, SourceObservation
from ..canonical.utils import contact_hash


def project_pos(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str):
    for index, journey in enumerate(world.journeys):
        for event_index, event in enumerate(journey.events):
            if event["event_type"] not in {"pos_purchased", "pos_returned"}:
                continue
            loyalty_id = "LOY-10021" if index == 0 else (f"LOY-{10022 + index}" if index % 3 else None)
            payload = {"store_id": f"STORE-{(index % 5) + 1:03d}", "product_id": event["product_id"], "amount": event["amount"], "currency": "EUR"}
            if loyalty_id:
                payload["loyalty_id"] = loyalty_id
            if event["event_type"] == "pos_returned":
                payload["return_of_transaction_id"] = f"POS-TXN-{index + 1:05d}"
                payload["return_type"] = "full"
            entity = "transactions" if event["event_type"] == "pos_purchased" else "returns"
            record_id = f"POS-TXN-{index + 1:05d}" if entity == "transactions" else f"POS-RETURN-{index + 1:05d}"
            yield SourceObservation("pos", entity, record_id, "insert", event["at"], event["at"], ingestion_timestamp, batch_id, f"pos.{entity}.v1", payload)

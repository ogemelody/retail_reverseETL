from __future__ import annotations

from ..canonical.entities import CanonicalWorld, SourceObservation
from ..canonical.utils import contact_hash


def project_ecommerce(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str):
    for index, customer in enumerate(world.customers.values()):
        ecommerce_id = "EC-93821" if index == 0 else f"EC-{93822 + index}"
        yield SourceObservation("ecommerce", "customers", ecommerce_id, "insert", ingestion_timestamp, ingestion_timestamp, ingestion_timestamp, batch_id, "ecommerce.customers.v1", {"ecommerce_customer_id": ecommerce_id, "email_hash": contact_hash(customer.email, "email"), "first_name": customer.first_name, "last_name": customer.last_name, "city": customer.city})
    for index, journey in enumerate(world.journeys):
        for event_index, event in enumerate(journey.events):
            if event["event_type"] != "online_ordered":
                continue
            customer_id = "EC-93821" if index == 0 else f"EC-{93822 + index}"
            order_id = f"EC-ORDER-{index + 1:05d}"
            yield SourceObservation("ecommerce", "orders", order_id, "insert", event["at"], event["at"], ingestion_timestamp, batch_id, "ecommerce.orders.v1", {"ecommerce_customer_id": customer_id, "status": "completed", "currency": "EUR", "total_amount": event["amount"]})
            yield SourceObservation("ecommerce", "order_items", f"{order_id}-ITEM-01", "insert", event["at"], event["at"], ingestion_timestamp, batch_id, "ecommerce.order_items.v1", {"order_id": order_id, "product_id": event["product_id"], "quantity": 1, "unit_price": event["amount"]})
            for refund_index, later in enumerate(journey.events):
                if later["event_type"] == "refund_issued":
                    yield SourceObservation("ecommerce", "refunds", f"{order_id}-REFUND-{refund_index + 1}", "insert", later["at"], later["at"], ingestion_timestamp, batch_id, "ecommerce.refunds.v1", {"order_id": order_id, "refund_amount": later["amount"], "currency": "EUR"})

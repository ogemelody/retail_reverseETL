from __future__ import annotations

from datetime import timedelta

from ..config import Config
from .entities import Customer, Journey, Product
from .utils import iso, rng


def build_journeys(config: Config, customers: list[Customer], products: list[Product]) -> list[Journey]:
    journeys: list[Journey] = []
    start = config.start
    for index, customer in enumerate(customers):
        product = products[index % len(products)]
        if index == 0:
            kind = "hero_cart_abandonment_offline_conversion"
            events = [
                {"event_type": "product_viewed", "at": iso(start), "product_id": product.product_id},
                {"event_type": "add_to_cart", "at": iso(start + timedelta(minutes=5)), "product_id": product.product_id},
                {"event_type": "identify", "at": iso(start + timedelta(minutes=10)), "product_id": product.product_id},
                {"event_type": "checkout_started", "at": iso(start + timedelta(minutes=12)), "product_id": product.product_id},
                {"event_type": "pos_purchased", "at": iso(start + timedelta(days=2)), "product_id": product.product_id, "amount": product.price},
            ]
        elif index % 4 == 0:
            kind = "online_purchase_refund"
            events = [{"event_type": "product_viewed", "at": iso(start), "product_id": product.product_id}, {"event_type": "online_ordered", "at": iso(start + timedelta(hours=2)), "product_id": product.product_id, "amount": product.price}, {"event_type": "refund_issued", "at": iso(start + timedelta(days=1)), "product_id": product.product_id, "amount": round(product.price / 2, 2)}]
        elif index % 4 == 1:
            kind = "pos_return"
            events = [{"event_type": "pos_purchased", "at": iso(start), "product_id": product.product_id, "amount": product.price}, {"event_type": "pos_returned", "at": iso(start + timedelta(days=3)), "product_id": product.product_id, "amount": product.price}]
        elif index % 4 == 2:
            kind = "anonymous_to_identified"
            events = [{"event_type": "product_viewed", "at": iso(start), "product_id": product.product_id}, {"event_type": "identify", "at": iso(start + timedelta(hours=1)), "product_id": product.product_id}]
        else:
            kind = "anonymous_only"
            events = [{"event_type": "product_viewed", "at": iso(start), "product_id": product.product_id}, {"event_type": "add_to_cart", "at": iso(start + timedelta(minutes=4)), "product_id": product.product_id}]
        journeys.append(Journey(f"journey_{index + 1:04d}", customer.canonical_customer_id, kind, events))
    return journeys

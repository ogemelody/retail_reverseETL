from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Customer:
    canonical_customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    city: str


@dataclass
class Product:
    product_id: str
    sku: str
    name: str
    category: str
    price: float
    currency: str = "EUR"


@dataclass
class Journey:
    journey_id: str
    canonical_customer_id: str
    journey_type: str
    events: list[dict[str, Any]] = field(default_factory=list)
    source_ids: dict[str, str] = field(default_factory=dict)


@dataclass
class SourceObservation:
    source_system: str
    source_entity: str
    source_record_id: str
    operation: str
    business_event_timestamp: str
    source_updated_at: str
    ingestion_timestamp: str
    batch_id: str
    schema_version: str
    payload: dict[str, Any]
    late_arrival: bool = False
    late_arrival_reason: str | None = None

    def raw(self) -> dict[str, Any]:
        return {
            "source_system": self.source_system,
            "source_entity": self.source_entity,
            "source_record_id": self.source_record_id,
            "operation": self.operation,
            "late_arrival": self.late_arrival,
            **({"late_arrival_reason": self.late_arrival_reason} if self.late_arrival_reason else {}),
            "business_event_timestamp": self.business_event_timestamp,
            "source_updated_at": self.source_updated_at,
            "ingestion_timestamp": self.ingestion_timestamp,
            "batch_id": self.batch_id,
            "schema_version": self.schema_version,
            "payload": self.payload,
        }


@dataclass
class CanonicalWorld:
    customers: dict[str, Customer]
    products: dict[str, Product]
    journeys: list[Journey]
    batch_sequence: int = 0

    def successor(self, sequence: int) -> "CanonicalWorld":
        cities = ("Berlin", "Cologne", "Munich")
        customers = self.customers.copy()
        if customers:
            customer_id = sorted(customers)[(sequence - 4) % len(customers)]
            customer = customers[customer_id]
            next_city = cities[(sequence + int(customer_id.rsplit("_", 1)[-1])) % len(cities)]
            customers[customer_id] = Customer(
                customer.canonical_customer_id,
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone,
                next_city,
            )
        return CanonicalWorld(customers, self.products.copy(), self.journeys, sequence)

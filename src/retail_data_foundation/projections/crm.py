from __future__ import annotations

from ..canonical.entities import CanonicalWorld, SourceObservation
from ..canonical.utils import contact_hash


def _contact_id(index: int) -> str:
    return "CRM-29382" if index == 0 else f"CRM-{29383 + index}"


def project_crm(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str):
    for index, customer in enumerate(world.customers.values()):
        contact_id = _contact_id(index)
        payload = {"crm_contact_id": contact_id, "email_hash": contact_hash(customer.email, "email"), "phone_hash": contact_hash(customer.phone, "phone"), "first_name": customer.first_name, "last_name": customer.last_name, "city": customer.city, "consent_status": "granted"}
        if index == 0:
            payload["loyalty_id"] = "LOY-10021"
        yield SourceObservation("crm", "contacts", contact_id, "insert", ingestion_timestamp, ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1", payload)


def project_crm_successor(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str, sequence: int):
    if not world.customers:
        return
    index = (sequence - 4) % len(world.customers)
    customer = list(world.customers.values())[index]
    payload = {
        "crm_contact_id": _contact_id(index),
        "email_hash": contact_hash(customer.email, "email"),
        "phone_hash": contact_hash(customer.phone, "phone"),
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "city": customer.city,
        "consent_status": "withdrawn" if sequence % 2 == 0 else "granted",
    }
    if index == 0:
        payload["loyalty_id"] = "LOY-10021"
    yield SourceObservation(
        "crm",
        "contacts",
        _contact_id(index),
        "update",
        ingestion_timestamp,
        ingestion_timestamp,
        ingestion_timestamp,
        batch_id,
        "crm.contacts.v1",
        payload,
    )

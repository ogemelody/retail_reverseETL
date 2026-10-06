from __future__ import annotations

from datetime import datetime, timedelta

from ..canonical.entities import CanonicalWorld, SourceObservation
from ..canonical.utils import contact_hash, rng


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


def project_crm_controlled_scenarios(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str, sequence: int, seed: int = 7):
    """Emit deterministic CRM continuation scenarios as source observations."""
    if sequence < 6 or len(world.customers) < 5:
        return

    customers = list(world.customers.values())
    consent_customer = customers[0]
    consent_id = _contact_id(0)
    yield SourceObservation(
        "crm", "contacts", consent_id, "update", ingestion_timestamp,
        ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
        {
            "crm_contact_id": consent_id,
            "email_hash": contact_hash(consent_customer.email, "email"),
            "phone_hash": contact_hash(consent_customer.phone, "phone"),
            "first_name": consent_customer.first_name,
            "last_name": consent_customer.last_name,
            "city": consent_customer.city,
            "previous_consent_status": "granted",
            "consent_status": "withdrawn",
            "consent_change": {"old": "granted", "new": "withdrawn"},
            "loyalty_id": "LOY-10021",
        },
    )

    delete_id = _contact_id(1)
    yield SourceObservation(
        "crm", "contacts", delete_id, "delete", ingestion_timestamp,
        ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
        {"crm_contact_id": delete_id, "tombstone": True, "deleted_at": ingestion_timestamp},
    )

    late_customer = customers[2]
    late_id = "CRM-LATE-29386"
    late_event = "2026-01-03T09:00:00Z"
    yield SourceObservation(
        "crm", "contacts", late_id, "insert", late_event, late_event,
        ingestion_timestamp, batch_id, "crm.contacts.v1",
        {
            "crm_contact_id": late_id,
            "email_hash": contact_hash(late_customer.email, "email"),
            "phone_hash": contact_hash(late_customer.phone, "phone"),
            "first_name": late_customer.first_name,
            "last_name": late_customer.last_name,
            "city": late_customer.city,
            "consent_status": "granted",
        },
    )

    duplicate_customer = customers[3]
    duplicate_id = "CRM-DUP-29387"
    duplicate_event = "2026-01-07T08:00:00Z"
    duplicate_payload = {
        "crm_contact_id": duplicate_id,
        "email_hash": contact_hash(duplicate_customer.email, "email"),
        "phone_hash": contact_hash(duplicate_customer.phone, "phone"),
        "first_name": duplicate_customer.first_name,
        "last_name": duplicate_customer.last_name,
        "city": duplicate_customer.city,
        "consent_status": "granted",
        "logical_version": "crm-dup-29387-v1",
    }
    for delivery_instance in (1, 2):
        yield SourceObservation(
            "crm", "contacts", duplicate_id, "insert", duplicate_event,
            duplicate_event, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {**duplicate_payload, "delivery_instance": delivery_instance},
        )

    # Add a deterministic population around the anchors. The index ranges are
    # disjoint, so a source contact cannot be selected for conflicting
    # generated scenarios in the same continuation batch.
    customers = list(world.customers.values())
    if len(customers) < 65:
        return
    random = rng(seed, "crm-controlled-population", sequence)
    update_indexes = list(range(4, 22))
    consent_indexes = list(range(22, 27))
    delete_indexes = list(range(27, 30))
    insert_indexes = list(range(30, 62))
    late_indexes = list(range(62, 64))
    random.shuffle(update_indexes)
    random.shuffle(consent_indexes)
    random.shuffle(delete_indexes)
    random.shuffle(insert_indexes)
    random.shuffle(late_indexes)

    for index in update_indexes:
        customer = customers[index]
        contact_id = _contact_id(index)
        yield SourceObservation(
            "crm", "contacts", contact_id, "update", ingestion_timestamp,
            ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {
                "crm_contact_id": contact_id,
                "email_hash": contact_hash(customer.email, "email"),
                "phone_hash": contact_hash(customer.phone, "phone"),
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "city": customer.city,
                "previous_city": customer.city,
                "consent_status": "granted",
            },
        )

    for index in consent_indexes:
        customer = customers[index]
        contact_id = _contact_id(index)
        yield SourceObservation(
            "crm", "contacts", contact_id, "update", ingestion_timestamp,
            ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {
                "crm_contact_id": contact_id,
                "email_hash": contact_hash(customer.email, "email"),
                "phone_hash": contact_hash(customer.phone, "phone"),
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "city": customer.city,
                "previous_consent_status": "granted",
                "consent_status": "withdrawn",
                "consent_change": {"old": "granted", "new": "withdrawn"},
            },
        )

    for index in delete_indexes:
        contact_id = _contact_id(index)
        yield SourceObservation(
            "crm", "contacts", contact_id, "delete", ingestion_timestamp,
            ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {"crm_contact_id": contact_id, "tombstone": True, "deleted_at": ingestion_timestamp},
        )

    for index in insert_indexes:
        customer = customers[index]
        contact_id = f"CRM-NEW-{29388 + index:05d}"
        yield SourceObservation(
            "crm", "contacts", contact_id, "insert", ingestion_timestamp,
            ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {
                "crm_contact_id": contact_id,
                "email_hash": contact_hash(customer.email, "email"),
                "phone_hash": contact_hash(customer.phone, "phone"),
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "city": customer.city,
                "consent_status": "granted",
            },
        )

    ingestion = datetime.fromisoformat(ingestion_timestamp.replace("Z", "+00:00"))
    for offset, index in enumerate(late_indexes, start=1):
        customer = customers[index]
        contact_id = f"CRM-LATE-{29388 + index:05d}"
        event_timestamp = (ingestion - timedelta(days=3, hours=offset)).isoformat().replace("+00:00", "Z")
        yield SourceObservation(
            "crm", "contacts", contact_id, "insert", event_timestamp,
            event_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {
                "crm_contact_id": contact_id,
                "email_hash": contact_hash(customer.email, "email"),
                "phone_hash": contact_hash(customer.phone, "phone"),
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "city": customer.city,
                "consent_status": "granted",
            },
        )

    duplicate_customer = customers[64]
    duplicate_id = "CRM-DUP-29388"
    duplicate_event = (ingestion - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    duplicate_payload = {
        "crm_contact_id": duplicate_id,
        "email_hash": contact_hash(duplicate_customer.email, "email"),
        "phone_hash": contact_hash(duplicate_customer.phone, "phone"),
        "first_name": duplicate_customer.first_name,
        "last_name": duplicate_customer.last_name,
        "city": duplicate_customer.city,
        "consent_status": "granted",
        "logical_version": "crm-dup-29388-v1",
    }
    for delivery_instance in (1, 2):
        yield SourceObservation(
            "crm", "contacts", duplicate_id, "insert", duplicate_event,
            duplicate_event, ingestion_timestamp, batch_id, "crm.contacts.v1",
            {**duplicate_payload, "delivery_instance": delivery_instance},
        )

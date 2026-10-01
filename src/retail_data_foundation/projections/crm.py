from __future__ import annotations

from ..canonical.entities import CanonicalWorld, SourceObservation
from ..canonical.utils import contact_hash


def project_crm(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str):
    for index, customer in enumerate(world.customers.values()):
        contact_id = "CRM-29382" if index == 0 else f"CRM-{29383 + index}"
        payload = {"crm_contact_id": contact_id, "email_hash": contact_hash(customer.email, "email"), "phone_hash": contact_hash(customer.phone, "phone"), "first_name": customer.first_name, "last_name": customer.last_name, "city": customer.city, "consent_status": "granted"}
        if index == 0:
            payload["loyalty_id"] = "LOY-10021"
        yield SourceObservation("crm", "contacts", contact_id, "insert", ingestion_timestamp, ingestion_timestamp, ingestion_timestamp, batch_id, "crm.contacts.v1", payload)

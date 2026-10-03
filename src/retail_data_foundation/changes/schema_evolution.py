from __future__ import annotations


def schema_for(source_system: str, entity: str, sequence: int, transition_batch: int) -> str:
    version = 2 if sequence >= transition_batch else 1
    return f"{source_system}.{entity}.v{version}"


def transition_records(sequence: int, transition_batch: int) -> list[dict]:
    if sequence != transition_batch:
        return []
    return [{"from_schema_version": "pos.transactions.v1", "to_schema_version": "pos.transactions.v2", "effective_batch_id": f"batch_{sequence + 1:03d}", "change_type": "added_field", "field_name": "channel", "previous_definition": None, "new_definition": "string", "description": "Explicit source schema evolution example"}]

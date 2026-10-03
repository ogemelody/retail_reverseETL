from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from itertools import groupby

from ..anomalies import inject_anomalies
from ..canonical.world import build_world
from ..changes.cdc import annotate_operations
from ..changes.late_arrivals import mark_late
from ..changes.schema_evolution import schema_for, transition_records
from ..identity import apply_identity_evidence
from ..projections import project_all, project_successor_changes
from ..validation.report import validate_records
from .jsonl import stream_jsonl_parts
from .manifests import batch_manifest, run_manifest
from ..landing.protocol import control_name, object_name


def _target_sequence(config, record) -> int:
    event = datetime.fromisoformat(record.business_event_timestamp.replace("Z", "+00:00"))
    delta_days = (event - config.start).days
    if record.source_system == "pos" and delta_days >= 2:
        return 2
    if record.source_system == "ecommerce" and record.source_entity == "refunds":
        return 1
    return max(0, delta_days)


def _configuration(config) -> dict:
    return {
        "bucket": config.bucket,
        "prefix": config.prefix,
        "seed": config.seed,
        "start_timestamp": config.start_timestamp,
        "batch_interval_hours": config.batch_interval_hours,
        "customers": config.customers,
        "products": config.products,
        "behavioral_events_per_customer": config.behavioral_events_per_customer,
        "part_records": config.part_records,
        "identity_quality_mix": list(config.identity_quality_mix),
        "anomaly_scenarios": list(config.anomaly_scenarios),
        "schema_transition_batch": config.schema_transition_batch,
        "batch_count": config.batch_count,
    }


def _committed_batches(run: dict) -> list[dict]:
    batches = run.get("batches", [])
    if run.get("status") != "landed":
        raise ValueError("Existing run is not fully landed and cannot be continued")
    return batches


def _existing_checkpoint(run: dict, config) -> tuple[int, list[dict]]:
    batches = _committed_batches(run)
    checkpoint = run.get("checkpoint") or {}
    last_sequence = checkpoint.get("last_committed_sequence")
    if last_sequence is None:
        last_sequence = max((batch.get("batch_sequence", index) for index, batch in enumerate(batches)), default=-1)
    if last_sequence != len(batches) - 1:
        raise ValueError("Existing run checkpoint does not match its committed batch list")
    normalized = []
    for index, batch in enumerate(batches):
        sequence = batch.get("batch_sequence", index)
        normalized_batch = dict(batch)
        normalized_batch.setdefault("batch_sequence", sequence)
        normalized_batch.setdefault("ingestion_timestamp", config.ingestion_time(sequence).isoformat().replace("+00:00", "Z"))
        normalized.append(normalized_batch)
    return last_sequence, normalized


def _validate_continuation(config, run: dict) -> None:
    if run.get("run_id") != config.run_id:
        raise ValueError("Run manifest run_id does not match the requested run_id")
    if run.get("seed") != config.seed:
        raise ValueError("Incompatible continuation configuration: seed")
    existing = run.get("configuration", {})
    requested = _configuration(config)
    immutable = set(requested) - {"batch_count"}
    mismatches = [key for key in sorted(immutable) if key in existing and existing[key] != requested[key]]
    if mismatches:
        raise ValueError(f"Incompatible continuation configuration: {', '.join(mismatches)}")


def _batch_records(world, projected, grouped, sequence, ingestion, previous_ids, config):
    records = []
    for record in grouped.get(sequence, []):
        records.append(replace(record, batch_id=f"batch_{sequence + 1:03d}", ingestion_timestamp=ingestion, schema_version=schema_for(record.source_system, record.source_entity, sequence, config.schema_transition_batch)))
    if sequence == 1 and projected:
        candidate = next((item for item in projected if item.source_system == "ecommerce" and item.source_entity == "customers"), None)
        if candidate:
            records.append(replace(candidate, batch_id="batch_002", ingestion_timestamp=ingestion, source_updated_at=ingestion, operation="update", schema_version="ecommerce.customers.v1", payload={**candidate.payload, "city": "Berlin"}))
    if sequence >= 4:
        records.extend(project_successor_changes(world.successor(sequence), f"batch_{sequence + 1:03d}", ingestion, sequence))
    records = annotate_operations(records, previous_ids)
    records = mark_late(records, ingestion)
    records = list(apply_identity_evidence(records))
    return inject_anomalies(records, config.anomaly_scenarios, config.seed + sequence)


def generate_to_gcs(config, landing, *, continue_run: bool = False, new_batches: int | None = None):
    if new_batches is not None and new_batches < 1:
        raise ValueError("new_batches must be positive")
    world = build_world(config)
    projected = list(project_all(world, "batch_001", config.start_timestamp))
    grouped = {}
    for record in projected:
        grouped.setdefault(_target_sequence(config, record), []).append(record)
    run_name = control_name(config.prefix, "runs", f"run_id={config.run_id}")
    existing_run = landing.get_json(run_name)
    if existing_run is not None:
        if not continue_run:
            raise ValueError("run_id already exists; use --continue --new-batches N")
        if new_batches is None:
            raise ValueError("--new-batches is required when continuing an existing run")
        _validate_continuation(config, existing_run)
        last_sequence, committed_batches = _existing_checkpoint(existing_run, config)
        start_sequence = last_sequence + 1
        requested_batches = new_batches
        batch_results = list(committed_batches)
        object_namespace = existing_run.get("object_namespace", "legacy")
    else:
        if continue_run:
            raise ValueError(f"Cannot continue missing run_id: {config.run_id}")
        if new_batches is not None:
            raise ValueError("--new-batches requires --continue")
        start_sequence = 0
        requested_batches = config.batch_count
        batch_results = []
        object_namespace = "run_scoped"
    previous_ids: set[str] = set()
    for sequence in range(start_sequence):
        ingestion = config.ingestion_time(sequence).isoformat().replace("+00:00", "Z")
        previous_ids.update(r.source_record_id for r in _batch_records(world, projected, grouped, sequence, ingestion, previous_ids, config))
    for sequence in range(start_sequence, start_sequence + requested_batches):
        batch_id = f"batch_{sequence + 1:03d}"
        ingestion = config.ingestion_time(sequence).isoformat().replace("+00:00", "Z")
        records = _batch_records(world, projected, grouped, sequence, ingestion, previous_ids, config)
        report = validate_records(records)
        objects = []
        for (source_system, entity), entity_records in groupby(sorted(records, key=lambda item: (item.source_system, item.source_entity)), key=lambda item: (item.source_system, item.source_entity)):
            for part, (text, count) in enumerate(stream_jsonl_parts(list(entity_records), config.part_records)):
                name = object_name(config.prefix, source_system, entity, ingestion, batch_id, part, config.run_id if object_namespace == "run_scoped" else None)
                result = landing.put_text(name, text, count)
                objects.append(result.__dict__)
        validation_name = control_name(config.prefix, "validation", f"run_id={config.run_id}/batch_id={batch_id}")
        validation_result = landing.put_json(validation_name, report.as_dict())
        objects.append(validation_result.__dict__)
        transitions = transition_records(sequence, config.schema_transition_batch)
        for transition in transitions:
            schema_name = control_name(config.prefix, "schemas", f"transition-{config.run_id}-{batch_id}")
            objects.append(landing.put_json(schema_name, transition).__dict__)
        manifest = batch_manifest(config.run_id, batch_id, sequence, ingestion, {r.source_system for r in records}, {f"{r.source_system}.{r.source_entity}": r.schema_version for r in records}, {f"{key[0]}.{key[1]}": sum(1 for r in records if (r.source_system, r.source_entity) == key) for key in {(r.source_system, r.source_entity) for r in records}}, objects, report, transitions)
        manifest_name = control_name(config.prefix, "batches", f"run_id={config.run_id}/batch_id={batch_id}")
        manifest_result = landing.put_json(manifest_name, manifest)
        batch_results.append({"manifest": manifest_result.__dict__, "batch_id": batch_id, "batch_sequence": sequence, "ingestion_timestamp": ingestion, "record_count": len(records)})
        previous_ids.update(r.source_record_id for r in records)
    run = run_manifest(config.run_id, config.seed, _configuration(config), batch_results, object_namespace=object_namespace)
    landing.put_json(run_name, run, overwrite=existing_run is not None)
    return run

from __future__ import annotations

import hashlib
import json


def batch_manifest(run_id, batch_id, sequence, ingestion_timestamp, source_domains, schemas, counts, objects, report, transitions=None):
    return {"run_id": run_id, "batch_id": batch_id, "batch_sequence": sequence, "planned_ingestion_timestamp": ingestion_timestamp, "source_domains": sorted(source_domains), "schema_versions": schemas, "actual_record_counts": counts, "output_objects": objects, "schema_transitions": transitions or [], "status": "landed", "validation_summary": report.as_dict()["summary"]}


def configuration_fingerprint(config: dict) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def run_manifest(run_id, seed, config, batches, status="landed", object_namespace="run_scoped"):
    last_sequence = max((batch["batch_sequence"] for batch in batches), default=-1)
    last_batch_id = f"batch_{last_sequence + 1:03d}" if last_sequence >= 0 else None
    return {
        "run_id": run_id,
        "seed": seed,
        "configuration": config,
        "configuration_fingerprint": configuration_fingerprint(config),
        "object_namespace": object_namespace,
        "batches": batches,
        "checkpoint": {
            "last_committed_batch_id": last_batch_id,
            "last_committed_sequence": last_sequence,
            "next_batch_id": f"batch_{last_sequence + 2:03d}",
            "next_batch_sequence": last_sequence + 1,
            "batch_timestamps": [batch["ingestion_timestamp"] for batch in batches],
            "schema_transition_batch": config["schema_transition_batch"],
        },
        "status": status,
    }

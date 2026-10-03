from __future__ import annotations

from dataclasses import replace

from ..canonical.utils import rng


def inject_anomalies(records, scenarios: tuple[str, ...], seed: int):
    records = list(records)
    if not records:
        return records
    output = list(records)
    random = rng(seed, "anomalies")
    if "duplicate_events" in scenarios:
        output.append(records[0])
    if "invalid_product" in scenarios:
        bad = replace(records[0], payload={**records[0].payload, "product_id": "INVALID-PRODUCT"})
        output.append(bad)
    if "missing_campaign" in scenarios:
        output[0] = replace(output[0], payload={key: value for key, value in output[0].payload.items() if key != "campaign_id"})
    if "missing_optional_fields" in scenarios:
        output[0] = replace(output[0], payload={key: value for key, value in output[0].payload.items() if key not in {"city", "phone_hash"}})
    return output

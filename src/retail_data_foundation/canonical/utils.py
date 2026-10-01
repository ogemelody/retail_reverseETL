from __future__ import annotations

import hashlib
import random
import re


def rng(seed: int, *parts: object) -> random.Random:
    material = ":".join([str(seed), *(str(part) for part in parts)])
    return random.Random(int(hashlib.sha256(material.encode()).hexdigest()[:16], 16))


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value)


def contact_hash(value: str, kind: str) -> str:
    normalized = normalize_email(value) if kind == "email" else normalize_phone(value)
    return hashlib.sha256(normalized.encode()).hexdigest()


def iso(value) -> str:
    return value.astimezone(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z")

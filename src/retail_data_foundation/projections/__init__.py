from collections.abc import Iterable

from ..canonical.entities import CanonicalWorld, SourceObservation
from .behavioral import project_behavioral
from .crm import project_crm, project_crm_successor
from .ecommerce import project_ecommerce
from .pos import project_pos


def project_all(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str) -> Iterable[SourceObservation]:
    yield from project_behavioral(world, batch_id, ingestion_timestamp)
    yield from project_ecommerce(world, batch_id, ingestion_timestamp)
    yield from project_pos(world, batch_id, ingestion_timestamp)
    yield from project_crm(world, batch_id, ingestion_timestamp)


def project_successor_changes(world: CanonicalWorld, batch_id: str, ingestion_timestamp: str, sequence: int) -> Iterable[SourceObservation]:
    """Project deterministic source changes from a canonical successor state."""
    yield from project_crm_successor(world, batch_id, ingestion_timestamp, sequence)


__all__ = ["project_all", "project_successor_changes"]

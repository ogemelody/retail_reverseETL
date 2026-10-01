from retail_data_foundation.canonical.world import build_world
from retail_data_foundation.config import Config


def test_hero_has_no_online_order():
    journey = build_world(Config(bucket="b", customers=1, products=1)).journeys[0]
    assert "online_ordered" not in [event["event_type"] for event in journey.events]
    assert "pos_purchased" in [event["event_type"] for event in journey.events]

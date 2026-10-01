from __future__ import annotations

from datetime import timedelta

from ..config import Config
from .entities import CanonicalWorld, Customer, Journey, Product
from .journeys import build_journeys
from .utils import iso, rng


def build_world(config: Config, sequence: int = 0) -> CanonicalWorld:
    random = rng(config.seed, "world")
    customers = {}
    for index in range(config.customers):
        cid = f"customer_{index + 1:04d}"
        customers[cid] = Customer(cid, f"Name{index + 1}", f"Family{index + 1}", f"customer{index + 1}@example.test", f"+491700{index:06d}", random.choice(["Berlin", "Cologne", "Munich"]))
    products = {}
    categories = ["Jackets", "Shoes", "Accessories", "Tops"]
    for index in range(config.products):
        pid = f"product_{index + 1:04d}"
        products[pid] = Product(pid, f"SKU-{index + 1:04d}", f"Retail Product {index + 1}", categories[index % len(categories)], float(25 + (index % 10) * 15))
    journeys = build_journeys(config, list(customers.values()), list(products.values()))
    return CanonicalWorld(customers, products, journeys, sequence)

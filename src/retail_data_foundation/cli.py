from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .landing.gcs import GCSLanding
from .serialization.pipeline import generate_to_gcs


def build_parser():
    parser = argparse.ArgumentParser(prog="retail-data")
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate")
    generate.add_argument("--config", required=True)
    generate.add_argument("--bucket", required=False)
    generate.add_argument("--continue", dest="continue_run", action="store_true")
    generate.add_argument("--new-batches", type=int, required=False)
    validate = sub.add_parser("validate")
    validate.add_argument("--bucket", required=True)
    validate.add_argument("--run-id", required=True)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        config = load_config(args.config, bucket=args.bucket)
        landing = GCSLanding(config.bucket, config.prefix, region=config.region, storage_class=config.storage_class)
        result = generate_to_gcs(config, landing, continue_run=args.continue_run, new_batches=args.new_batches)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    print(json.dumps({"bucket": args.bucket, "run_id": args.run_id, "status": "use GCS control objects for inspection"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

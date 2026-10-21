#!/usr/bin/env python3
"""Validate JSON without modifying files or contacting a server."""

import argparse
from decimal import Decimal
import json
from pathlib import Path
import sys

MAX_BYTES = 10 * 1024 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key: " + repr(key))
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-standard JSON number: " + value)


def validate(data):
    """Raise ValueError for invalid UTF-8 JSON, duplicate keys or constants."""
    if len(data) > MAX_BYTES:
        raise ValueError("input exceeds the 10 MiB limit")
    text = data.decode("utf-8-sig")
    try:
        json.loads(text, object_pairs_hook=unique_object,
                   parse_constant=reject_constant, parse_float=Decimal,
                   parse_int=Decimal)
    except RecursionError as exc:
        raise ValueError("JSON nesting exceeds the parser limit") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="UTF-8 JSON files, or - for stdin")
    args = parser.parse_args(argv)
    if args.files.count("-") > 1:
        parser.error("stdin (-) can only be specified once")
    failed = False
    for filename in args.files:
        try:
            if filename == "-":
                data = sys.stdin.buffer.read(MAX_BYTES + 1)
            else:
                with Path(filename).open("rb") as stream:
                    data = stream.read(MAX_BYTES + 1)
            validate(data)
        except (ValueError, OSError) as exc:
            print("FAIL {}: {}".format(filename, exc), file=sys.stderr)
            failed = True
        else:
            print("OK {}".format(filename))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

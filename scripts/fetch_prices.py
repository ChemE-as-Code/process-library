# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "jsonschema"]
# ///
"""Turn open trade statistics into a registry ``price`` (process-library#46).

The registry records prices from open sources only (docs/registry.md, "Missing prices"). This
script reads UN Comtrade's annual trade records of one HS 2022 subheading and year and prints a
``price`` entry for ``chemicals/chemicals.yaml``: the unit value (traded value over net weight)
in USD/kg, with year, currency, region, a range and the source URL. It does not edit the
registry; the owner reviews the entry and pastes it under the substance's ``properties``.

- The **unit value** is the sum of the value over the sum of the net weight of every reporter
  that reports both; the **range** is the lowest and highest unit value of the reporters that
  traded at least ``--min-kg`` (default 1000 t), so that a few small consignments do not set it.
- An HS subheading covers every grade of the substance (HS 2804.40 is gaseous and liquid oxygen
  alike), so the price belongs to the substance, not to a grade. The entry's note says so.
- Exports (``--flow X``, the default) are valued FOB, imports (``M``) CIF.

Two ways to run it:

    # fetch (needs network access to comtradeapi.un.org; COMTRADE_KEY, if set, uses the
    # subscription API instead of the keyless preview, which returns at most 500 records)
    uv run scripts/fetch_prices.py --slug oxygen --year 2023

    # convert a response saved from the same URL (e.g. downloaded in a browser)
    uv run scripts/fetch_prices.py --slug oxygen --year 2023 --input comtrade-280440-2023.json

``--slug`` reads the HS code from the registry's ``classification.hs``; ``--hs 2804.40`` gives
it directly. The entry is checked against the registry schema's ``price`` before it is printed.

Not yet run against the live API from this repository's CI or development environment (its
network policy blocks comtradeapi.un.org). On the first real run, check that the response's
fields are those read below (``primaryValue``, ``netWgt``, ``reporterCode``/``reporterISO``,
``partnerCode``) and that UN Comtrade's terms of use allow the derived value to be published
under CC BY 4.0.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

KIT = Path(__file__).resolve().parents[1]
REGISTRY = KIT / "chemicals" / "chemicals.yaml"
SCHEMA = KIT / "schemas" / "chemicals.schema.json"

PREVIEW = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
DATA = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
#: Reporters below this net weight (kg) do not set the range (they still count in the mean).
MIN_KG = 1.0e6
FLOWS = {"X": "exports, FOB", "M": "imports, CIF"}


class PriceError(Exception):
    pass


def hs_code(registry: dict, slug: str) -> str:
    """The HS subheading of *slug* from the registry's ``classification.hs`` (e.g. ``2804.40``)."""
    for chem in registry.get("chemicals", []):
        if chem["slug"] == slug:
            hs = (chem.get("classification") or {}).get("hs")
            if not hs:
                raise PriceError(f"chemicals.{slug} has no classification.hs; give --hs")
            return hs
    raise PriceError(f"no chemical {slug!r} in the registry")


def query_url(hs: str, year: int, flow: str = "X", keyed: bool = False) -> str:
    """The Comtrade request for every reporter's trade of *hs* with the world in *year*."""
    if flow not in FLOWS:
        raise PriceError(f"flow {flow!r} is not one of {', '.join(FLOWS)}")
    params = {
        "cmdCode": hs.replace(".", ""),
        "flowCode": flow,
        "period": str(year),
        "partnerCode": "0",  # world
        "partner2Code": "0",
        "customsCode": "C00",  # all customs procedures
        "motCode": "0",  # all modes of transport
        "includeDesc": "true",
    }
    return f"{DATA if keyed else PREVIEW}?{urllib.parse.urlencode(params)}"


def fetch(url: str, key: str | None = None) -> Any:
    headers = {"User-Agent": "process-library fetch_prices", "Accept": "application/json"}
    if key:
        headers["Ocp-Apim-Subscription-Key"] = key
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return json.loads(response.read())


@dataclass
class UnitValues:
    mean: float  # USD/kg over every reporter with value and weight
    low: float | None
    high: float | None
    reporters: list[str]
    skipped: list[str]  # reporters without value or net weight


def unit_values(response: Any, hs: str, year: int, min_kg: float = MIN_KG) -> UnitValues:
    """The unit value and range of a Comtrade response (``{"data": [...]}``)."""
    records = response.get("data") if isinstance(response, dict) else None
    if not records:
        raise PriceError(f"the response has no records for HS {hs} in {year}")
    code = hs.replace(".", "")
    value = weight = 0.0
    per_reporter: list[tuple[str, float, float]] = []
    reporters: list[str] = []
    skipped: list[str] = []
    for record in records:
        if str(record.get("cmdCode", code)) != code or str(record.get("period", year)) != str(year):
            continue
        if str(record.get("partnerCode", 0)) != "0":
            continue  # a bilateral record; the world total of that reporter is counted instead
        who = str(record.get("reporterISO") or record.get("reporterDesc") or record.get("reporterCode") or "?")
        if who in reporters or who in skipped:
            raise PriceError(f"reporter {who} appears twice for HS {hs} in {year}: query one customs procedure and mode of transport (the totals)")
        trade, kg = record.get("primaryValue"), record.get("netWgt")
        if not trade or not kg or trade <= 0 or kg <= 0:
            skipped.append(who)
            continue
        value += float(trade)
        weight += float(kg)
        reporters.append(who)
        per_reporter.append((who, float(trade), float(kg)))
    if weight <= 0:
        raise PriceError(f"no record for HS {hs} in {year} has both a value and a net weight")
    large = [t / kg for _, t, kg in per_reporter if kg >= min_kg]
    return UnitValues(value / weight, min(large) if large else None, max(large) if large else None, sorted(reporters), sorted(skipped))


def price_entry(values: UnitValues, hs: str, year: int, flow: str, url: str, min_kg: float = MIN_KG) -> dict:
    """The registry ``price`` (schemas/chemicals.schema.json, ``$defs/price``)."""
    entry: dict[str, Any] = {
        "value": round(values.mean, 4),
        "unit": "USD/kg",
        "currency": "USD",
        "year": year,
        "region": f"world ({FLOWS[flow]}, {len(values.reporters)} reporters)",
    }
    if values.low is not None and values.high is not None:
        entry["range"] = [round(values.low, 4), round(values.high, 4)]
    retrieved = "UN Comtrade, annual HS data"
    entry["source"] = (
        f"{retrieved}: unit value of HS {hs} {FLOWS[flow]} to the world in {year}, "
        f"sum of primaryValue over sum of netWgt; {url}"
    )
    entry["note"] = (
        f"Trade unit value of the whole HS subheading, which covers every grade of the substance. "
        f"Range: lowest and highest unit value of reporters trading at least {min_kg / 1000:g} t. "
        f"Reporters: {', '.join(values.reporters)}."
        + (f" Without value or net weight (left out): {', '.join(values.skipped)}." if values.skipped else "")
    )
    return entry


def schema_problems(entry: dict) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    price = {**schema["$defs"]["price"], "$defs": schema["$defs"]}
    return [error.message for error in Draft202012Validator(price).iter_errors(entry)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--slug", help="registry slug; its classification.hs is used")
    which.add_argument("--hs", help="HS 2022 subheading, e.g. 2804.40")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--flow", default="X", choices=sorted(FLOWS), help="X exports (FOB, default) or M imports (CIF)")
    parser.add_argument("--min-kg", type=float, default=MIN_KG, help=f"smallest reporter net weight in the range (default {MIN_KG:g} kg)")
    parser.add_argument("--input", type=Path, help="a saved Comtrade response (JSON) instead of fetching")
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    args = parser.parse_args(argv)
    try:
        hs = args.hs or hs_code(yaml.safe_load(args.registry.read_text(encoding="utf-8")), args.slug)
        key = os.environ.get("COMTRADE_KEY", "").strip() or None
        url = query_url(hs, args.year, args.flow, keyed=bool(key))
        response = json.loads(args.input.read_text(encoding="utf-8")) if args.input else fetch(url, key)
        entry = price_entry(unit_values(response, hs, args.year, args.min_kg), hs, args.year, args.flow, query_url(hs, args.year, args.flow), args.min_kg)
    except (PriceError, OSError, json.JSONDecodeError) as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 1
    if problems := schema_problems(entry):
        print("error: the entry fails the registry schema: " + "; ".join(problems), file=sys.stderr)
        return 1
    label = args.slug or f"HS {hs}"
    print(f"# {label}: paste under properties of the substance in chemicals/chemicals.yaml, after review")
    print(yaml.safe_dump({"price": entry}, sort_keys=False, allow_unicode=True, width=100), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

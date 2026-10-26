"""fetch_prices.py: open trade statistics to a registry ``price``, offline (synthetic responses)."""

from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import fetch_prices as fp

REGISTRY = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))


def _record(reporter: str, value: float | None, kg: float | None, **extra) -> dict:
    return {"cmdCode": "280440", "period": 2023, "flowCode": "X", "partnerCode": 0, "reporterISO": reporter,
            "primaryValue": value, "netWgt": kg, **extra}


#: Synthetic numbers for the arithmetic only, not prices of anything.
RESPONSE = {"data": [
    _record("AAA", 3.0e6, 2.0e6),  # 1.5 /kg
    _record("BBB", 1.0e6, 4.0e6),  # 0.25 /kg
    _record("CCC", 9.0e3, 1.0e3),  # 9 /kg, but below the range's minimum weight
    _record("DDD", 5.0e5, None),  # no weight: left out
    _record("AAA", 1.0, 1.0, partnerCode=276),  # bilateral: not the world total
]}


def test_the_hs_code_comes_from_the_registry_classification() -> None:
    assert fp.hs_code(REGISTRY, "oxygen") == "2804.40"
    assert fp.hs_code(REGISTRY, "nitrogen") == "2804.30"
    assert fp.hs_code(REGISTRY, "argon") == "2804.21"
    with pytest.raises(fp.PriceError, match="no classification.hs"):
        fp.hs_code(REGISTRY, "cooling-water")
    with pytest.raises(fp.PriceError, match="no chemical"):
        fp.hs_code(REGISTRY, "unobtainium")


def test_the_query_asks_for_world_totals_of_one_subheading_and_year() -> None:
    url = fp.query_url("2804.40", 2023)
    assert url.startswith(fp.PREVIEW + "?")
    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    assert query["cmdCode"] == "280440" and query["period"] == "2023" and query["flowCode"] == "X"
    assert query["partnerCode"] == "0" and query["customsCode"] == "C00" and query["motCode"] == "0"
    assert fp.query_url("2804.40", 2023, keyed=True).startswith(fp.DATA + "?")
    with pytest.raises(fp.PriceError):
        fp.query_url("2804.40", 2023, flow="Z")


def test_unit_value_is_total_value_over_total_weight_and_range_skips_small_reporters() -> None:
    values = fp.unit_values(RESPONSE, "2804.40", 2023)
    assert values.mean == pytest.approx((3.0e6 + 1.0e6 + 9.0e3) / (2.0e6 + 4.0e6 + 1.0e3))
    assert (values.low, values.high) == (pytest.approx(0.25), pytest.approx(1.5))
    assert values.reporters == ["AAA", "BBB", "CCC"] and values.skipped == ["DDD"]
    # with no minimum, the small reporter sets the top of the range
    assert fp.unit_values(RESPONSE, "2804.40", 2023, min_kg=0).high == pytest.approx(9.0)


def test_empty_or_unusable_responses_and_duplicate_reporters_are_errors() -> None:
    with pytest.raises(fp.PriceError, match="no records"):
        fp.unit_values({"data": []}, "2804.40", 2023)
    with pytest.raises(fp.PriceError, match="both a value and a net weight"):
        fp.unit_values({"data": [_record("AAA", 1.0, 0)]}, "2804.40", 2023)
    with pytest.raises(fp.PriceError, match="appears twice"):
        fp.unit_values({"data": [_record("AAA", 1.0, 1.0), _record("AAA", 2.0, 1.0)]}, "2804.40", 2023)
    # records of another code or year are not counted
    with pytest.raises(fp.PriceError, match="both a value"):
        fp.unit_values({"data": [_record("AAA", 1.0, 1.0, period=2022)]}, "2804.40", 2023)


def test_the_entry_has_what_the_registry_schema_requires() -> None:
    values = fp.unit_values(RESPONSE, "2804.40", 2023)
    entry = fp.price_entry(values, "2804.40", 2023, "X", fp.query_url("2804.40", 2023))
    assert fp.schema_problems(entry) == []
    assert entry["unit"] == "USD/kg" and entry["currency"] == "USD" and entry["year"] == 2023
    assert entry["range"] == [0.25, 1.5]
    assert "UN Comtrade" in entry["source"] and fp.PREVIEW in entry["source"]
    assert "every grade" in entry["note"] and "DDD" in entry["note"]
    assert fp.schema_problems({**entry, "unit": "USD per kg"})  # the schema check bites


def test_cli_converts_a_saved_response_without_the_network(tmp_path: Path, capsys, monkeypatch) -> None:
    saved = tmp_path / "comtrade.json"
    saved.write_text(json.dumps(RESPONSE), encoding="utf-8")
    monkeypatch.setattr(fp, "fetch", lambda *a, **k: pytest.fail("fetched although --input was given"))
    assert fp.main(["--slug", "oxygen", "--year", "2023", "--input", str(saved)]) == 0
    out = capsys.readouterr().out
    price = yaml.safe_load(out)["price"]
    assert price["value"] == pytest.approx(0.6682, abs=1e-4) and price["region"].startswith("world (exports, FOB")


def test_cli_fetch_uses_the_key_only_in_the_header(tmp_path: Path, capsys, monkeypatch) -> None:
    seen = {}

    def fake_fetch(url: str, key: str | None = None):
        seen.update(url=url, key=key)
        return RESPONSE

    monkeypatch.setattr(fp, "fetch", fake_fetch)
    monkeypatch.setenv("COMTRADE_KEY", "secret")
    assert fp.main(["--hs", "2804.40", "--year", "2023"]) == 0
    assert seen["url"].startswith(fp.DATA) and seen["key"] == "secret"
    assert "secret" not in capsys.readouterr().out  # the published source is the keyless URL


def test_cli_reports_errors(tmp_path: Path, capsys) -> None:
    saved = tmp_path / "empty.json"
    saved.write_text(json.dumps({"data": []}), encoding="utf-8")
    assert fp.main(["--slug", "oxygen", "--year", "2023", "--input", str(saved)]) == 1
    assert "no records" in capsys.readouterr().err

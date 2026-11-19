"""Every feed and product of a process's LCI dataset is in the chemicals registry or explicitly
excluded (issue #251; docs/registry.md, "Feeds and products a process does not name yet").

A dataset exchange counts as named when the process's ``chemistry`` names it: a flow with that
``inventory_key``, or a flow whose note names the key (the library's form for a flow without an
``inventory_key``, docs/registry.md, "How processes name these chemicals"). A note that starts
with the key names it; a later mention names it unless its sentence says the flow has no registry
entry ("... (feed:X) has no registry entry yet" is not a name). Every other feed
(``feed:``, ``input:`` and ``consumable:`` inputs counted in kg) and every product counted in kg
is listed here, either with the registry slug it is (the process names it under ``chemistry`` in
its own review, which then removes it here) or with the reason it has no registry identity.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import registry as reg  # noqa: E402

PROCESSES = KIT / "processes"
REGISTRY = KIT / "chemicals" / "chemicals.yaml"
FEED_PREFIXES = ("feed", "input", "consumable")

#: Feeds and products whose substance is in the registry but which the process's ``chemistry``
#: does not name yet. Naming them links the process to the substance's producers in the Atlas;
#: it is the process's own change (CONTRIBUTING.md: another process's files change through its
#: own review), after which the entry goes from here.
UNNAMED_REGISTRY_FLOWS = {
    "acrylonitrile-1/feed:CAIR": "air",  # combustion air to the thermal oxidiser
    "bio-ethylene-1/feed:O2": "air",  # combustion oxygen from ambient air
    "bioethanol-1/consumable:caustic": "sodium-hydroxide",
    "bioethanol-1/consumable:lime": "calcium-oxide",  # quicklime, as its LCA mapping counts it
    "bioethanol-1/consumable:sulfuric-acid": "sulfuric-acid",
    "bioethanol-1/consumable:urea": "urea",
    "carbon-tetrabromide-1/consumable:rinse-water": "water",
    "co2-electrolysis-bpm-1/feed:AIR": "air",
    "copper-i-chloride-1/consumable:nitrogen": "nitrogen",
    "copper-i-chloride-1/consumable:rinse-water": "water",
    "cumene-1/product:LPG": "propane",  # propane (LPG) to sale or fuel, a co-product
    "e-fuels-1/feed:O2": "air",  # combustion oxygen from ambient air
    "ethanol-1/consumable:caustic-soda": "sodium-hydroxide",
    "ethanol-1/consumable:phosphoric-acid": "phosphoric-acid",
    "glycerol-1/feed:ACF": "activated-carbon",  # its water note still says "no registry entry yet"
    "hydrogen-peroxide-1/consumable:activated-carbon": "activated-carbon",
    "hydrogen-peroxide-1/consumable:nitric-acid": "nitric-acid",
    "hydrogen-peroxide-1/consumable:sodium-hydroxide": "sodium-hydroxide",
    "iodine-1/feed:AIR": "air",
    "iodomethane-1/consumable:activated-carbon": "activated-carbon",
    "lactic-acid-1/consumable:cip-caustic": "sodium-hydroxide",  # the cleaning in place's NaOH make-up
    "lactic-acid-1/consumable:cip-water": "water",  # the fermenters' cleaning rinse
    "n-bromosuccinimide-1/consumable:rinse-water": "water",
    "natural-gas-processing-1/consumable:MDEA": "n-methyldiethanolamine",
    "natural-gas-processing-1/consumable:TEG": "triethylene-glycol",
    "natural-gas-processing-1/feed:AIR": "air",
    "p-toluenesulfonyl-chloride-1/consumable:nitrogen": "nitrogen",
    "p-toluenesulfonyl-chloride-1/consumable:rinse-water": "water",
    "plastic-pyrolysis-1/feed:O2": "air",  # combustion oxygen from ambient air
    "power-generation-1/consumable:scr-dilution-water": "water",  # the water of the 19 wt% aqueous ammonia
    "propylene-pdh-1/input:alumina": "aluminium-oxide",  # activated alumina adsorbent
    "propylene-pdh-1/input:dmds": "dimethyl-disulfide",
    "sodium-cyanide-1/consumable:bfw-export": "water",  # boiler feed water leaving as exported steam
    "sodium-cyanide-1/consumable:bfw-makeup": "water",
    "sodium-cyanide-1/consumable:phosphate-makeup": "phosphoric-acid",
    "titanium-dioxide-1/consumable:scouring-salt": "sodium-chloride",  # rock salt
    "titanium-dioxide-1/consumable:scouring-sand": "silicon-dioxide",  # silica sand
    "utility-flare/feed:O2": "air",  # combustion oxygen from ambient air
    "utility-wwtp/feed:O2": "air",  # oxygen of the aeration air
    "waste-incineration-1/feed:activated-carbon": "activated-carbon",
}

CATALYST = "a catalyst charge or make-up (active metal or oxide on a support), not one substance"
PRECIOUS_METAL_LOSS = "precious metal lost from a catalyst or gauze, counted as metal: part of a catalyst, not a feed another process makes"
SORBENT = "a sorbent or ion-exchange material of no single identity (zeolite molecular sieve, resin)"
ARTICLE = "an article or maintenance material (membrane, electrode, filter, lubricant), not a chemical"
FUEL_RESIDUE = "a residue or off-gas of no fixed composition sent to fuel; no registry entry"
CONSUMER_STREAM = "a component of the consumer's stream the utility treats (wastewater, flare gas), not a supply"

#: Feeds and products without a registry identity, each with the reason.
NO_REGISTRY_IDENTITY = {
    "4-aminophenol-1/consumable:catalyst-pt-c": CATALYST,
    "4-aminophenol-1/consumable:surfactant": "a dimethylalkylamine oxide surfactant of mixed alkyl chains (C8 to C20, mostly dodecyl), not one substance",
    "acrylonitrile-1/consumable:ammox-catalyst": CATALYST,
    "aniline-1/consumable:hydrogenation-catalyst": CATALYST,
    "asu-1/consumable:lube-oil": ARTICLE,
    "asu-1/consumable:molecular-sieve": SORBENT,
    "bioethanol-1/consumable:alpha-amylase": "an enzyme preparation, not one substance",
    "bioethanol-1/consumable:gluco-amylase": "an enzyme preparation, not one substance",
    "bioethanol-1/consumable:yeast": "purchased yeast (Saccharomyces cerevisiae), an organism, not a chemical",
    "bromine-1/feed:BRINE": "natural bromide brine from the brine field, of no fixed composition (chemistry has water as its stand-in)",
    "btx-1/input:clay": "treating clay of the clay treaters, a sorbent; the registry's clay is the cement raw-meal material",
    "catalytic-reforming-1/input:catalyst": CATALYST,
    "co2-electrolysis-bpm-1/consumable:anode-ni-foam": ARTICLE,
    "co2-electrolysis-bpm-1/consumable:cathode-gde-ag": ARTICLE,
    "co2-electrolysis-bpm-1/consumable:cathode-gdl-carbon": ARTICLE,
    "co2-electrolysis-bpm-1/consumable:membrane-bpm": ARTICLE,
    "cumene-1/product:HEAVY": FUEL_RESIDUE,
    "ethanol-1/consumable:hydration-catalyst": CATALYST,
    "ethanol-1/consumable:molecular-sieve": SORBENT,
    "ethylbenzene-1/product:flux_oil": FUEL_RESIDUE,
    "ethylene-glycol-1/consumable:eo-catalyst": CATALYST,
    "glycerol-1/product:FAL": "the fatty-acid layer to the biodiesel plant, a mixture of no fixed composition",
    "fcc-1/input:catalyst": CATALYST,
    "formaldehyde-1/consumable:ecs-catalyst": CATALYST,
    "formaldehyde-1/consumable:femo-catalyst": CATALYST,
    "formaldehyde-1/consumable:oil-filters": ARTICLE,
    "hydrocracking-1/input:catalyst": CATALYST,
    "hydrogen-peroxide-1/feed:MKS": "the working-solution solvent make-up, a blend of C9 aromatic solvent and diisobutylcarbinol (process.yaml note), not one substance",
    "hydrogen-peroxide-1/consumable:ion-exchange-resin": SORBENT,
    "hydrogen-peroxide-1/consumable:palladium-catalyst-loss": PRECIOUS_METAL_LOSS,
    "hydrotreating-1/input:catalyst": CATALYST,
    "hydroxylamine-1/consumable:o2-removal-catalyst": CATALYST,
    "hydroxylamine-1/consumable:pt-catalyst-loss": PRECIOUS_METAL_LOSS,
    "hydroxylamine-1/consumable:pt-rh-gauze-loss": PRECIOUS_METAL_LOSS,
    "iodine-1/feed:BRINE": "natural iodide brine from the wellfield, of no fixed composition",
    "iodomethane-1/consumable:molecular-sieve": SORBENT,
    "iron-steel-1/feed:other-iron": "not named by the source, so no registry identity (process.yaml comment)",
    "iron-steel-1/feed:sinter-additives": "not named by the source, so no registry identity (process.yaml comment)",
    "isobutene-1/product:FUELGAS": FUEL_RESIDUE,
    "isobutene-1/product:HEAVIES": FUEL_RESIDUE,
    "lng-terminal-1/feed:INVDRAW": "LNG drawn from the terminal's own tank inventory, not a supply",
    "lng-terminal-1/feed:SHIPVAP": "vapour returned from the carrier the terminal loads, not a supply",
    "maleic-anhydride-1/consumable:vpo-catalyst": CATALYST,
    "natural-gas-processing-1/consumable:MOLSIEVE": SORBENT,
    "nitric-acid-1/consumable:pt-rh-gauze-loss": PRECIOUS_METAL_LOSS,
    "pet-1/input:catalyst": "antimony compounds, not named in the dataset",
    "pet-1/input:stabiliser": "a phosphorus stabiliser, compound not named in the dataset (polyphosphoric acid only as an example)",
    "propylene-pdh-1/input:catalyst": CATALYST,
    "propylene-pdh-1/input:phosphate": "a phosphate, compound not named in the dataset",
    "pvc-1/feed:STOPF": "the short-stop, a hindered-phenol antioxidant as a 30 wt% aqueous dispersion, compound not named in the dataset",
    "sodium-chlorate-1/consumable:sodium-dichromate": "sodium dichromate, Na2Cr2O7: the registry's atomic weights have no chromium, so it cannot carry the entry yet (the LCI keeps it a gap)",
    "sodium-cyanide-1/consumable:hcn-stabiliser": "an acid stabiliser, compound not named in the dataset",
    "sodium-cyanide-1/consumable:pt-rh-gauze": CATALYST,
    "styrene-1/consumable:catalyst": CATALYST,
    "styrene-1/consumable:inhibitor": "a phenolic polymerisation inhibitor, compound not named in the dataset",
    "terephthalic-acid-1/input:cobalt-catalyst": "cobalt catalyst, compound not named in the dataset",
    "terephthalic-acid-1/input:manganese-catalyst": "manganese catalyst, compound not named in the dataset",
    "titanium-dioxide-1/consumable:still-oil": "a mineral oil of no fixed composition",
    "utility-instrument-air/feed:moisture": "the water vapour of the intake air, part of air",
    "utility-wwtp/feed:nitrogen": CONSUMER_STREAM,
    "utility-wwtp/feed:organics": CONSUMER_STREAM,
    "utility-wwtp/feed:water": CONSUMER_STREAM,
    "vcm-1/input:catalyst": CATALYST,
}


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _dataset_flows() -> dict[str, str]:
    """``"<process>/<key>"`` -> title of every feed and product (counted in kg) of the processes'
    LCI datasets (``lca/dataset.yaml`` and ``lca/datasets/*.yaml``)."""
    flows: dict[str, str] = {}
    for folder in sorted(p for p in PROCESSES.iterdir() if (p / "process.yaml").is_file()):
        files = [folder / "lca" / "dataset.yaml"] if (folder / "lca" / "dataset.yaml").is_file() else []
        files += sorted((folder / "lca" / "datasets").glob("*.yaml"))
        for path in files:
            for exchange in (_yaml(path) or {}).get("exchanges", []) or []:
                key = exchange.get("key", "")
                if exchange.get("unit") != "kg":
                    continue
                feed = exchange.get("type") == "input" and key.split(":")[0] in FEED_PREFIXES
                if feed or exchange.get("type") == "product":
                    flows.setdefault(f"{folder.name}/{key}", exchange.get("title", ""))
    return flows


#: A sentence that says a flow is *not* in the registry ("has no registry entry yet", "no registry
#: slug"); a key mentioned in it is not named by it.
NOT_IN_REGISTRY = re.compile(r"\bno registry (?:entr|slug|identit)", re.IGNORECASE)


#: The key or key list a naming note starts with ("feed:CUM: ...", "feed:A, feed:B, ...").
LEADING_KEYS = re.compile(r"(?:[a-z]+:[A-Za-z0-9_\-]+(?:,\s*|\s+and\s+|\s*\([^)]*\)\s*(?:and\s+)?)?)+")


def _naming_texts(note: str) -> list[str]:
    """The parts of *note* that name keys: the key or key list it starts with, and each sentence
    that does not say a flow has no registry entry."""
    leading = LEADING_KEYS.match(note)
    sentences = [sentence for sentence in re.split(r"(?<=[.;])\s+", note) if not NOT_IN_REGISTRY.search(sentence)]
    return ([leading.group(0)] if leading else []) + sentences


def _named(pid: str, key: str, cache: dict[str, tuple[set[str], str]]) -> bool:
    """Whether *pid*'s ``chemistry`` names the exchange *key*: by ``inventory_key`` or in a note."""
    if pid not in cache:
        chemistry = (_yaml(PROCESSES / pid / "process.yaml") or {}).get("chemistry") or {}
        items = [item for group in ("inputs", "outputs", "utilities") for item in chemistry.get(group) or []]
        texts = [text for item in items for text in _naming_texts(item.get("note") or "")]
        cache[pid] = ({item["inventory_key"] for item in items if item.get("inventory_key")}, "\n".join(texts))
    keys, notes = cache[pid]
    return key in keys or re.search(re.escape(key) + r"(?![A-Za-z0-9_\-])", notes) is not None


def _unnamed() -> dict[str, str]:
    cache: dict[str, tuple[set[str], str]] = {}
    return {flow: title for flow, title in _dataset_flows().items() if not _named(*flow.split("/", 1), cache)}


def test_every_dataset_feed_and_product_is_named_or_listed() -> None:
    listed = set(UNNAMED_REGISTRY_FLOWS) | set(NO_REGISTRY_IDENTITY)
    missing = {flow: title for flow, title in _unnamed().items() if flow not in listed}
    assert missing == {}, (
        "feeds or products of an LCI dataset that the process's chemistry does not name: name each under "
        "chemistry (inventory_key, or a note naming the key) with its registry slug, adding the substance to "
        "chemicals/chemicals.yaml if it is missing, or list it in tests/test_registry_coverage.py with its reason"
    )


def test_listed_flows_are_still_unnamed() -> None:
    """An entry goes once the process names the flow, or the flow is gone."""
    unnamed = _unnamed()
    stale = sorted(flow for flow in (*UNNAMED_REGISTRY_FLOWS, *NO_REGISTRY_IDENTITY) if flow not in unnamed)
    assert stale == [], "remove these entries from tests/test_registry_coverage.py"


def test_unnamed_registry_flows_name_registry_slugs() -> None:
    chemicals = reg.load(_yaml(REGISTRY)).chemicals
    assert {flow: slug for flow, slug in UNNAMED_REGISTRY_FLOWS.items() if slug not in chemicals} == {}
    assert set(UNNAMED_REGISTRY_FLOWS).isdisjoint(NO_REGISTRY_IDENTITY)

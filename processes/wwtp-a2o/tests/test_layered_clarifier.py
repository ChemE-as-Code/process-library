"""Checks for the opt-in soluble transport and its published result metadata."""

import json

import numpy as np
import pytest

from wwtp_a2o.domains.process.model import REACTORS, clarifier_solubles, validate_inputs
from wwtp_a2o.foundation.runtime import ROOT
from wwtp_a2o.integrations.qsdsan import build_model, integrate


@pytest.fixture
def data():
    return json.loads((ROOT / "inputs/baseline.json").read_bytes())


def test_clarifier_solubles_opt_in(data):
    assert clarifier_solubles(data) == "mixed"
    data["clarifier_solubles"] = "bsm1-layered"
    validate_inputs(data)
    with pytest.raises(ValueError, match="unmodified upstream reference"):
        build_model(data, REACTORS, upstream_reference=True)
    data["clarifier_solubles"] = "unknown"
    with pytest.raises(ValueError, match="clarifier_solubles"):
        validate_inputs(data)


def test_layered_clarifier_soluble_balance_and_outlet_mapping(data):
    data["clarifier_solubles"] = "bsm1-layered"
    data["solver"]["days"] = 0.2
    system, units, streams = build_model(data, REACTORS)
    solution = integrate(system, data["solver"])
    assert solution.success

    system.DAE(solution.t[-1], solution.y[:, -1].copy())
    system._write_state()
    c1 = units["C1"]
    components = c1.components
    phosphorus = components.index("S_PO4")
    layers = c1._state[: c1.N_layer * len(components)].reshape(c1.N_layer, -1)
    derivatives = c1._dstate[: layers.size].reshape(layers.shape)
    assert layers.shape[0] == 10
    assert "TSS10 [mg/L]" in c1._state_header
    assert abs(layers[0, phosphorus] - layers[-1, phosphorus]) > 1e-5
    assert streams["EFFLUENT"].state[phosphorus] == pytest.approx(layers[0, phosphorus])
    for key in ("RAS", "WAS"):
        assert streams[key].state[phosphorus] == pytest.approx(layers[-1, phosphorus])

    feed = streams["TO_CLARIFIER"].state
    emitted = sum(
        streams[key].state[-1] * streams[key].state[phosphorus]
        for key in ("EFFLUENT", "RAS", "WAS")
    )
    accumulated = c1.A_settle * c1.h_layer * derivatives[:, phosphorus].sum()
    np.testing.assert_allclose(feed[-1] * feed[phosphorus] - emitted, accumulated, atol=1e-8)

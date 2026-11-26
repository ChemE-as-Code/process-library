"""Opt-in BSM1 transport of dissolved components through a QSDsan clarifier."""

import numpy as np
from biosteam import System
from exposan.bsm1.system import default_c1_kwargs
from qsdsan.unit_operations import FlatBottomCircularClarifier


class LayeredSolubleClarifier(FlatBottomCircularClarifier):
    """Keep QSDsan's solids model and resolve dissolved transport through each layer.

    State layout, top to bottom: one component vector per layer, influent
    flow, then the original TSS layer states. The first vector and the tail
    retain the layout used by QSDsan 1.5.3 for its effluent and solids.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        headers = self._state_header
        count = len(self.components)
        self._state_header = [
            f"Layer {layer} {name}"
            for layer in range(1, self.N_layer + 1)
            for name in headers[:count]
        ] + headers[count:]

    def _init_state(self):
        super()._init_state()
        count = len(self.components)
        concentrations = np.tile(self._state[:count], self.N_layer)
        self._state = np.concatenate((concentrations, self._state[count:]))
        self._dstate = np.zeros_like(self._state)

    def _update_state(self):
        super()._update_state()
        count = len(self.components)
        offset = (self.N_layer - 1) * count
        bottom_minus_top = self._state[offset : offset + count] - self._state[:count]
        for outlet in self.outs[1:]:
            outlet.state[:-1] += bottom_minus_top

    def _update_dstate(self):
        super()._update_dstate()
        count = len(self.components)
        offset = (self.N_layer - 1) * count
        bottom_minus_top = self._dstate[offset : offset + count] - self._dstate[:count]
        for outlet in self.outs[1:]:
            outlet.dstate[:-1] += bottom_minus_top

    def _compile_ODE(self):
        super()._compile_ODE()
        base_ode = self._ODE
        count = len(self.components)
        size = count * self.N_layer
        layer_shape = (self.N_layer, count)
        feed = self.feed_layer - 1
        layer_volume = self.A_settle * self.h_layer
        soluble = 1 - self.components.x
        underflow = self.underflow + self.wastage

        def layered_ode(t, inlet, state, inlet_rate):
            base_ode(t, inlet, state, inlet_rate)
            layers = state[:size].reshape(layer_shape)
            rate = self._dstate[:size].reshape(layer_shape)
            feed_flow = inlet[0, -1]
            upward = feed_flow - underflow
            rate[:feed] = (upward / layer_volume) * (layers[1 : feed + 1] - layers[:feed])
            rate[feed] = (feed_flow / layer_volume) * (inlet[0, :-1] * soluble - layers[feed])
            rate[feed + 1 :] = (underflow / layer_volume) * (layers[feed:-1] - layers[feed + 1 :])
            # The parent updates particulate derivatives and publishes with its
            # single-volume soluble rate. Publish the corrected layer rates.
            self._update_dstate()

        self._ODE = layered_ode


def use_layered_clarifier(system):
    """Replace the default vessel before integration, preserving ports and the concentration/TSS seeds."""
    units = {unit.ID: unit for unit in system.units}
    previous = units["C1"]
    inlet, outlets = previous.ins[0], tuple(previous.outs)
    previous.disconnect(discard=True)
    # These objects belong to the retired vessel and use its equipment ID.
    for auxiliary in (previous._mock_dyn_sys, previous._mixed, previous._inf, previous._ras, previous._was):
        auxiliary.registry.discard(auxiliary)
    clarifier = LayeredSolubleClarifier("C1", inlet, outlets, **default_c1_kwargs)
    if previous._solubles is not None:
        clarifier.set_init_solubles(**dict(zip(previous.components.IDs, previous._solubles, strict=True)))
    if previous._solids is not None:
        clarifier.set_init_TSS(previous._solids.copy())

    reactors = tuple(unit for unit in system.units if unit is not previous)
    layered = System("bsm1_layered", path=(*reactors, clarifier), recycle=system.recycle)
    layered.set_tolerance(rmol=1e-6)
    layered.set_dynamic_tracker(units["A1"], clarifier.outs[0])
    return layered

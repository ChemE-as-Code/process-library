"""Calls to the installed QSDsan/EXPOsan packages, without changing their equations."""

import copy
import hashlib
from pathlib import Path


def build_model(data, reactor_ids, upstream_reference=False):
    layered = data.get("clarifier_solubles") == "bsm1-layered"
    if upstream_reference and layered:
        raise ValueError("The unmodified upstream reference requires mixed clarifier solubles")
    # Heavy third-party imports stay at the integration boundary.
    from exposan.bsm1.system import create_system
    from qsdsan import process_models as pc

    if upstream_reference:
        system = create_system(suspended_growth_model="ASM2d", reactor_model="CSTR")
    else:
        c1 = copy.deepcopy(data["clarifier"])
        c1.update(
            underflow=data["recycles"]["return_sludge_m3_d"],
            wastage=data["recycles"]["waste_sludge_m3_d"],
        )
        system = create_system(
            suspended_growth_model="ASM2d",
            reactor_model="CSTR",
            inf_kwargs={
                "concentrations": data["influent"]["components_mg_L"],
                "units": ("m3/d", "mg/L"),
            },
            settler_kwargs=c1,
        )
        u = system.flowsheet.unit
        feed = u.A1.ins[0]
        feed.set_flow_by_concentration(
            data["influent"]["flow_m3_d"],
            concentrations=data["influent"]["components_mg_L"],
            units=("m3/d", "mg/L"),
        )
        feed.T = data["influent"]["temperature_K"]
        for uid in reactor_ids:
            reactor = getattr(u, uid)
            reactor.V_max = data["reactor_volumes_m3"][uid]
            if uid.startswith("O"):
                reactor.aeration = pc.DiffusedAeration(
                    "aer_" + uid,
                    "S_O2",
                    V=reactor.V_max,
                    KLa=data["aeration"]["kla_per_day"][uid],
                    DOsat=data["aeration"]["do_saturation_mg_O2_L"],
                )
        u.O3.split = [
            data["recycles"]["internal_m3_d"],
            data["influent"]["flow_m3_d"] + data["recycles"]["return_sludge_m3_d"],
        ]
        if layered:
            from wwtp_a2o.integrations.clarifier import use_layered_clarifier

            system = use_layered_clarifier(system, reactor_ids, c1)
    u = system.flowsheet.unit
    # ChemE IDs map to the actual QSDsan stream objects.
    streams = {
        "INFLUENT": u.A1.ins[0],
        "RAS": u.C1.outs[1],
        "INTERNAL": u.O3.outs[0],
        "TO_CLARIFIER": u.O3.outs[1],
        "EFFLUENT": u.C1.outs[0],
        "WAS": u.C1.outs[2],
    }
    for uid in reactor_ids[:-1]:
        streams[uid + "_OUT"] = getattr(u, uid).outs[0]
    return system, {uid: getattr(u, uid) for uid in (*reactor_ids, "C1")}, streams


def upstream_evidence(data, reference=False):
    """Return upstream metadata and source paths; do not copy or modify files."""
    import exposan.bsm1.system as upstream

    source = Path(upstream.__file__)
    return {
        "source_url": data["basis"]["url"],
        "source_file": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "asm2d_parameters": upstream.default_asm_kwargs["asm2d"],
        "factory_without_wrapper_overrides": reference,
    }, [source, Path(upstream.data_path) / "initial_conditions_asm2d.xlsx"]


def integrate(system, solver):
    """Keep the pre-refactor numerical settings and call order unchanged."""
    system.simulate(
        state_reset_hook="reset_cache",
        t_span=(0, solver["days"]),
        method=solver["method"],
        rtol=solver["rtol"],
        atol=solver["atol"],
        max_step=solver["max_step_days"],
        dense_output=True,
        timeout=solver.get("wall_limit_s", 180),
    )
    return system.scope.sol

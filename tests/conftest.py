"""Shared pytest configuration of the process library tooling."""


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "brightway: needs bw2io, bw2data and bw2calc (the LCI round trip); skipped without them"
    )
    config.addinivalue_line(
        "markers",
        "engineering: regenerates a process design with core (minutes; ADR 0033): run by the "
        "engineering job of validate.yml, deselected in the library job with -m 'not engineering'",
    )

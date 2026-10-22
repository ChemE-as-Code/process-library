"""Shared pytest configuration of the process library tooling."""


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "brightway: needs bw2io, bw2data and bw2calc (the LCI round trip); skipped without them"
    )

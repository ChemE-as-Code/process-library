"""Install the ChemE-as-Code Process Atlas LCI database into a Brightway 2.5 project."""

from cheme_as_code_lci.install import InstallReport, install, resolve
from cheme_as_code_lci.unallocated import (
    install_multifunctional,
    register_strategies,
    resolve_multifunctional,
)

__all__ = ["InstallReport", "install", "install_multifunctional", "register_strategies", "resolve", "resolve_multifunctional"]
__version__ = "0.1.0"

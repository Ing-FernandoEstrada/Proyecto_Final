# Re-export desde 04_dashboard.py
from importlib.util import spec_from_file_location, module_from_spec
import os

spec = spec_from_file_location("_dashboard", os.path.join(os.path.dirname(__file__), "04_dashboard.py"))
_module = module_from_spec(spec)
spec.loader.exec_module(_module)

DashboardSaludDato = _module.DashboardSaludDato

__all__ = ['DashboardSaludDato']

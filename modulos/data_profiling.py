# Re-export desde 01_data_profiling.py
from importlib.util import spec_from_file_location, module_from_spec
import os

spec = spec_from_file_location("_data_profiling", os.path.join(os.path.dirname(__file__), "01_data_profiling.py"))
_module = module_from_spec(spec)
spec.loader.exec_module(_module)

DataProfiler = _module.DataProfiler

__all__ = ['DataProfiler']

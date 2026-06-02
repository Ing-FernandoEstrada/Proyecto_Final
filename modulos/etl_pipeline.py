# Re-export desde 02_etl_pipeline.py
from importlib.util import spec_from_file_location, module_from_spec
import os

spec = spec_from_file_location("_etl_pipeline", os.path.join(os.path.dirname(__file__), "02_etl_pipeline.py"))
_module = module_from_spec(spec)
spec.loader.exec_module(_module)

ETLPipeline = _module.ETLPipeline

__all__ = ['ETLPipeline']

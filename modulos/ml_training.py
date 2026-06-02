# Re-export desde 03_ml_training.py
from importlib.util import spec_from_file_location, module_from_spec
import os

spec = spec_from_file_location("_ml_training", os.path.join(os.path.dirname(__file__), "03_ml_training.py"))
_module = module_from_spec(spec)
spec.loader.exec_module(_module)

ModeloRegresion = _module.ModeloRegresion
ModeloClasificacion = _module.ModeloClasificacion
TuberiaImputacionML = _module.TuberiaImputacionML

__all__ = ['ModeloRegresion', 'ModeloClasificacion', 'TuberiaImputacionML']

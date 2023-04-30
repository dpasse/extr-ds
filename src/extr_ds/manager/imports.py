from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from types import ModuleType


def load_file(name: str, path: str) -> ModuleType:
    spec = spec_from_loader(name, SourceFileLoader(name, path))
    if spec is None:
        raise TypeError('SPEC IS NONE')

    if spec.loader is None:
        raise TypeError('SPEC LOADER IS NONE')

    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)

    return mod

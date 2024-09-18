import importlib
import inspect
import pkgutil
import sys

from ..services.database import Base


__all__ = ['Base']

# Enables alembic to auto generate migrations for all models in the models package.
for module_tuple in pkgutil.iter_modules(sys.modules[__name__].__path__):
    module_name = module_tuple.name
    module = importlib.import_module(f'{__name__}.{module_name}')

    # Get a list of all classes in the module
    classes = [
        member
        for member, member_type in inspect.getmembers(module, inspect.isclass)
        if member_type.__module__ == module.__name__ and issubclass(member_type, Base)
    ]

    # Import the classes
    for class_name in classes:
        globals()[class_name] = getattr(module, class_name)
        __all__.append(class_name)

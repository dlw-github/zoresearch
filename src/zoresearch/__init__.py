from importlib.metadata import version
__version__ = version(__name__)
print(__version__)

invocation = f'Invoking __init__.py for {__name__}'

print(invocation)
from zoresearch.main import open
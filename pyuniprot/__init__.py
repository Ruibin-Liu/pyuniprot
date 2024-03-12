from .Uniprot import Uniprot
from .utils import get_isoforms
from .version import __version__

__all__ = [
    "Uniprot",
    "get_isoforms",
    "__version__",
]

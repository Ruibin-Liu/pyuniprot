from .UniProt import UniProt
from .UniRef import UniRef
from .utils import get_alt_resids, get_isoforms
from .version import __version__

__all__ = [
    "UniProt",
    "UniRef",
    "get_alt_resids",
    "get_isoforms",
    "__version__",
]

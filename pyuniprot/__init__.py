from .Uniprot import Uniprot
from .UniRef import UniRef
from .utils import get_alt_resids, get_isoforms
from .version import __version__

__all__ = [
    "Uniprot",
    "UniRef",
    "get_isoforms",
    "get_alt_resids",
    "__version__",
]

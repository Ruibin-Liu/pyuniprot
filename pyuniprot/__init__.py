# from .Uniprot import Uniprot
from .UniProt import UniProt
from .UniRef import UniRef
from .utils import get_alt_resids, get_isoforms
from .version import __version__

__all__ = [
    # "Uniprot",
    "UniProt",
    "UniRef",
    "get_isoforms",
    "get_alt_resids",
    "__version__",
]

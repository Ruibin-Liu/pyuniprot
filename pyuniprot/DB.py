"""
Dataclasses for the DB records in a Uniprot txt file.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HGNC:
    """Store the HGNC data in the DB records"""

    hgnc_id: int
    hgnc_name: str


@dataclass
class PANTHER:
    """Store the PANTHER data in the DB records"""

    family_id: str
    family_name: str
    family_occurrence: int
    subfamily_id: str
    subfamily_name: str
    subfamily_occurrence: int


@dataclass
class SeqRange:
    """Store a sequence range record."""

    seq_begin: int | str
    seq_end: int | str


@dataclass
class PDB:
    """Store the PDB data in the DB records"""

    pdb_id: str
    experiment_method: str
    resolution: float | str
    resolution_unit: str
    chain_ids: list[str]
    uniprot_res_range: list[SeqRange]

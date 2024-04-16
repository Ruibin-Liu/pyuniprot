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
    """Store a single PDB data in the DR records"""

    pdb_id: str
    experiment_method: str
    resolution: float | str
    resolution_unit: str
    chain_ids: list[str]
    uniprot_res_range: list[SeqRange]


"""
The following four are used for seuqnece databases
"""


@dataclass
class EMBL:
    """Store a single EMBL data entry in the DR records"""

    nucleotide_sequence_id: str  # "NUCLEOTIDE SEQUENCE" in the website
    protein_sequence_id: str  # "PROTEIN SEQUENCE" in the website
    molecule_type: str  # "MOLECULE TYPE" in the website
    status: str  # "STATUS" in the website


@dataclass
class CCDS:
    """Store a single CCDS data entry in the DR records"""

    ccds_id: str  # like 'CCDS11118.1'
    isoform: str  # like '[P04637-1]'


@dataclass
class PIR:
    """Store a single PIR data entry in the DR records"""

    uid: str  # the uid for a PIR record URL
    entry: str  # ENTRY for a PIR record


@dataclass
class RefSeq:
    """Store a single RefSeq data entry in the DR records"""

    protein_sequence_id: str  # protein sequence by NCBI
    nucleotide_sequence_id: str  # nuccore sequence by NCBI
    isoform: str  # like '[P04637-1]'


@dataclass
class GO:
    """Store a single GO data entry in the DR records"""

    accession_number: str  # an GO entry is GO: accession_number
    aspect: str  # ASPECT in the UniProt webiste
    # C: Cellular Component
    # F: Molecular Fucntion
    # P: Biological Process
    term: str  # TERM in the UniProt webiste
    inferred_from: str  # IDA: direct assay
    # IEA: electronic annotation
    source: str  # annotation source


@dataclass
class Reactome:
    """Store a single Reactome data entry in the DR records"""

    id: str  # Reactome Id
    pathway: str  # Reactome pathway

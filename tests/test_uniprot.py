import os
import sys
from pathlib import Path

from pyuniprot.Uniprot import Uniprot

sys.path.append("..")
CFD = os.path.dirname(__file__)
CWD = os.getcwd()


def test_get_properties():
    """
    Test class properties
    """
    uniprot_id = "P36952"
    uniprot = Uniprot(uniprot_id)
    assert (
        uniprot.uniprot_txt_url
        == f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.txt"
    ), "Uniprot TXT file link not right."

    file_path = Path(uniprot.local_download_dir, f"{uniprot.uniprot_id}.txt")

    if not file_path.exists():
        file_path = None
    assert (
        uniprot.local_download_dir == os.getcwd()
    ), "local_download_dir not user's CWD."
    assert (
        uniprot.uniprot_txt_file == file_path
    ), "Uniprot TXT file path not right when not existed."

    uniprot = Uniprot(
        uniprot_id,
        local_download_dir=Path(CFD, "test_files"),
    )
    assert uniprot.local_download_dir == Path(
        CFD, "test_files"
    ), "local_download_dir not pointing to test_files."
    assert uniprot.uniprot_txt_file == Path(
        CFD, "test_files", f"{uniprot.uniprot_id}.txt"
    ), "Uniprot TXT file path not right when existed."
    try:
        os.remove(f"{CWD}/{uniprot_id}.txt")
    except OSError:
        pass


def test_get_category_lines():
    """Test the _get_category_lines function."""
    uniprot_id = "P04637"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    category_lines = uniprot.category_lines
    assert (
        category_lines["SQ"].length == 393
    ), "P04637 sequence length in SQ not read as integer 393."


def test_empty_file():
    """Test the _get_category_lines function."""
    uniprot_id = "P30042"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    category_lines = uniprot.category_lines
    assert category_lines == {}, "P04637 sequence length in SQ not read as integer 393."


def test_no_panther():
    """Test the _get_category_lines function."""
    uniprot_id = "Q8IUI8"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    category_lines = uniprot.category_lines
    assert (
        len(category_lines["DR"].database_references["PANTHER"]) == 0
    ), "Q8IUI8 has wrong PANTHER,"


def test_empty_resid():
    """Test the _get_category_lines function."""
    uniprot_id = "Q9NPA5"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    category_lines = uniprot.category_lines
    assert (
        category_lines["DR"]
        .database_references["PDB"][0]
        .uniprot_res_range[0]
        .seq_begin
        == ""
    ), "Q9NPA5 first PDB resid is not ''."


def test_dr_records():
    """Test the different DR records as dataclasses."""
    uniprot_id = "P04637"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    category_lines = uniprot.category_lines
    dr = category_lines["DR"].database_references
    assert dr["PDB"][0].pdb_id == "1A1U", "P04637 first PDB not 1A1U."
    assert (
        dr["EMBL"][-1].nucleotide_sequence_id == "AY270155"
    ), "P04637 last EMBL nucleotide_sequence_id not AY270155."
    assert (
        dr["CCDS"][-1].ccds_id == "CCDS73971.1"
    ), "P04637 last CCDS ccds_id not CCDS73971.1."
    assert dr["PIR"][0].uid == "A25224", "P04637 PIR uid not A25224."
    assert (
        dr["GO"][-1].accession_number == "0016032"
    ), "P04637 last GO accession_number not 0016032."
    assert (
        dr["Reactome"][-1].id == "R-HSA-983231"
    ), "P04637 last Reactome id not R-HSA-983231."
    assert (
        dr["RefSeq"][-1].protein_sequence_id == "NP_001263690.1"
    ), "P04637 last RefSeq protein_sequence_id not NP_001263690.1."

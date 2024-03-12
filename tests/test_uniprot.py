import os
import sys
from pathlib import Path

from pyuniprot.Uniprot import Uniprot

sys.path.append("..")
CFD = os.path.dirname(__file__)


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
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass


def test_get_category_lines():
    """Test the _get_category_lines function."""
    uniprot_id = "P04637"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    uniprot._get_category_lines()
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
    uniprot._get_category_lines()
    category_lines = uniprot.category_lines
    assert category_lines == {}, "P04637 sequence length in SQ not read as integer 393."


def test_no_panther():
    """Test the _get_category_lines function."""
    uniprot_id = "Q8IUI8"
    uniprot = Uniprot(
        uniprot_id, save_txt=True, local_download_dir=Path(CFD, "test_files")
    )
    uniprot._get_category_lines()
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
    uniprot._get_category_lines()
    category_lines = uniprot.category_lines
    assert (
        category_lines["DR"]
        .database_references["PDB"][0]
        .uniprot_res_range[0]
        .seq_begin
        == ""
    ), "Q9NPA5 first PDB resids are not ''."

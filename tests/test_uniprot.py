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

import os
import sys
from pathlib import Path

import pytest

from pyuniprot.UniProt import UniProt

sys.path.append("..")
CFD = os.path.dirname(__file__)
CWD = os.getcwd()


@pytest.mark.filterwarnings("ignore")
def test_get_basic_properties():
    """
    Test class properties (not json content)
    """
    uniprot_id = "P36952"
    uniprot = UniProt(uniprot_id)
    assert (
        uniprot.uniprot_json_url == f"https://rest.uniprot.org/uniprotkb/{uniprot_id}"
    ), "UniProt json file link not right."

    file_path = Path(uniprot.local_download_dir, f"{uniprot.uniprot_id}.json")

    if not file_path.exists():
        file_path = None
    assert (
        uniprot.local_download_dir == os.getcwd()
    ), "local_download_dir not user's CWD."
    assert (
        uniprot.uniprot_json_file == file_path
    ), "UniProt json file path not right when not existed."

    uniprot = UniProt(
        uniprot_id,
        local_download_dir=Path(CFD, "test_files"),
    )
    assert uniprot.local_download_dir == Path(
        CFD, "test_files"
    ), "local_download_dir not pointing to test_files."
    assert uniprot.uniprot_json_file == Path(
        CFD, "test_files", f"{uniprot.uniprot_id}.json"
    ), "UniProt json file path not right when existed."
    try:
        os.remove(f"{CWD}/{uniprot_id}.json")
    except OSError:
        pass


@pytest.mark.filterwarnings("ignore")
def test_get_raw_json():
    """Test raw json."""
    uniprot_id = "P36952"
    uniprot = UniProt(
        uniprot_id, save_json=True, local_download_dir=Path(CFD, "test_files")
    )
    assert (
        uniprot.raw_json["primaryAccession"] == "P36952"
    ), "raw json primaryAccession wrong"
    assert (
        uniprot.raw_json["entryAudit"]["firstPublicDate"] == "1994-06-01"
    ), "raw json entryAudit->firstPublicDate wrong"


@pytest.mark.filterwarnings("ignore")
def test_get_json_as_properties():
    """Test json as properties."""
    uniprot_id = "P36952"
    uniprot = UniProt(
        uniprot_id, save_json=True, local_download_dir=Path(CFD, "test_files")
    )
    assert uniprot.primaryAccession == "P36952", "prop primaryAccession wrong"
    assert (
        uniprot.entryAudit.firstPublicDate == "1994-06-01"
    ), "prop entryAudit->firstPublicDate wrong"
    assert (
        uniprot.uniProtKBCrossReferences[0].properties[0].value == "AAA18957.1"
    ), "list prop wrong"

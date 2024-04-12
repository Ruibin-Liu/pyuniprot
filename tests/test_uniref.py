import json
import os
import sys
from pathlib import Path

from pyuniprot.UniRef import UniRef

sys.path.append("..")
CFD = os.path.dirname(__file__)
CWD = os.getcwd()


def test_get_properties():
    """
    Test class properties
    """
    uniprot_id = "P36952"
    uniprot = UniRef(uniprot_id)
    assert (
        uniprot.uniref_json_url
        == f"https://rest.uniprot.org/uniref/UniRef100_{uniprot_id}.json"
    ), "UniRef JSON file link not right."

    file_path = Path(uniprot.local_download_dir, f"UniRef100_{uniprot_id}.json")

    if not file_path.exists():
        file_path = None
    assert (
        uniprot.local_download_dir == os.getcwd()
    ), "local_download_dir not user's CWD."
    assert (
        uniprot.uniref_json_file == file_path
    ), "UniRef JSON file path not right when not existed."

    uniprot = UniRef(
        uniprot_id,
        local_download_dir=Path(CFD, "test_files"),
    )
    assert uniprot.local_download_dir == Path(
        CFD, "test_files"
    ), "local_download_dir not pointing to test_files."
    assert uniprot.uniref_json_file == Path(
        CFD, "test_files", f"UniRef100_{uniprot_id}.json"
    ), "UniRef JSON file path not right when existed."
    try:
        os.remove(f"{CWD}/UniRef100_{uniprot_id}.json")
    except OSError:
        pass


def test_get_json():
    """
    Test json content
    """
    uniprot_id = "P36952"
    uniprot = UniRef(uniprot_id, local_download_dir=Path(CFD, "test_files"))
    json_file = Path(CFD, "test_files", f"UniRef100_{uniprot_id}.json")
    with open(json_file, "r") as jf:
        expected = json.load(jf)
    assert uniprot.uniref_json == expected, "wrong json"
    try:
        os.remove(f"{CWD}/UniRef100_{uniprot_id}.json")
    except OSError:
        pass

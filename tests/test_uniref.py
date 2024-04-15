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
    thresh = 100
    uniprot = UniRef(
        uniprot_id, thresh=thresh, local_download_dir=Path(CFD, "test_files")
    )
    json_file = Path(CFD, "test_files", f"UniRef{thresh}_{uniprot_id}.json")
    with open(json_file, "r") as jf:
        expected = json.load(jf)
    assert uniprot.uniref_json == expected, "wrong json"


def test_get_json_properties():
    """
    Test json properties
    """
    uniprot_id = "P36952"
    uniprot = UniRef(uniprot_id, local_download_dir=Path(CFD, "test_files"))
    assert uniprot.id == "UniRef100_P36952", "wrong cluster id"
    assert uniprot.member_count == 2, "wrong cluster member count"
    assert uniprot.updated == "2023-11-08", "wrong cluster entry type"
    assert uniprot.entry_type == "UniRef100", "wrong cluster id"
    taxon = {"scientificName": "Homo sapiens", "taxonId": 9606}
    assert uniprot.common_taxon == taxon, "wrong cluster common taxon"
    members = [
        {
            "memberIdType": "UniParc",
            "memberId": "UPI0003EAE5A1",
            "organismName": "Homo sapiens",
            "organismTaxId": 9606,
            "sequenceLength": 204,
            "proteinName": "serpin B5 isoform X1",
            "uniref90Id": "UniRef90_P36952",
        }
    ]
    assert uniprot.members == members, "wrong cluster members"

    rep_member = UniRef._parse_representative_member(
        {
            "memberIdType": "UniProtKB ID",
            "memberId": "SPB5_HUMAN",
            "organismName": "Homo sapiens (Human)",
            "organismTaxId": 9606,
            "sequenceLength": 375,
            "proteinName": "Serpin B5",
            "accessions": ["P36952", "B2R6Y4", "Q6N0B4", "Q8WW89"],
            "uniref50Id": "UniRef50_P36952",
            "uniref90Id": "UniRef90_P36952",
            "uniparcId": "UPI0000201E51",
            "seed": True,
            "sequence": {
                "value": "MDALQLANSAFAVDLFKQLCEKEPLGNVLFSPICLSTSLSLAQVGAKGDTANEIGQVLHFENVKDVPFGFQTVTSDVNKLSSFYSLKLIKRLYVDKSLNLSTEFISSTKRPYAKELETVDFKDKLEETKGQINNSIKDLTDGHFENILADNSVNDQTKILVVNAAYFVGKWMKKFSESETKECPFRVNKTDTKPVQMMNMEATFCMGNIDSINCKIIELPFQNKHLSMFILLPKDVEDESTGLEKIEKQLNSESLSQWTNPSTMANAKVKLSIPKFKVEKMIDPKACLENLGLKHIFSEDTSDFSGMSETKGVALSNVIHKVCLEITEDGGDSIEVPGARILQHKDELNADHPFIYIIRHNKTRNIIFFGKFCSP",  # noqa
                "length": 375,
                "molWeight": 42100,
                "crc64": "9F24E18505912804",
                "md5": "07D06FD58D1EAB7DD89B019EDD40CC71",
            },
        }
    )
    assert (
        uniprot.representative_member == rep_member
    ), "wrong cluster representative member"

    sequence = UniRef._parse_sequence_data(
        {
            "value": "MDALQLANSAFAVDLFKQLCEKEPLGNVLFSPICLSTSLSLAQVGAKGDTANEIGQVLHFENVKDVPFGFQTVTSDVNKLSSFYSLKLIKRLYVDKSLNLSTEFISSTKRPYAKELETVDFKDKLEETKGQINNSIKDLTDGHFENILADNSVNDQTKILVVNAAYFVGKWMKKFSESETKECPFRVNKTDTKPVQMMNMEATFCMGNIDSINCKIIELPFQNKHLSMFILLPKDVEDESTGLEKIEKQLNSESLSQWTNPSTMANAKVKLSIPKFKVEKMIDPKACLENLGLKHIFSEDTSDFSGMSETKGVALSNVIHKVCLEITEDGGDSIEVPGARILQHKDELNADHPFIYIIRHNKTRNIIFFGKFCSP",  # noqa
            "length": 375,
            "molWeight": 42100,
            "crc64": "9F24E18505912804",
            "md5": "07D06FD58D1EAB7DD89B019EDD40CC71",
        }
    )
    assert uniprot.representative_member.sequence == sequence, "wrong sequence data"

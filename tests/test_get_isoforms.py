"""
Test all utils functions here.
"""

import os

import pytest

from pyuniprot.utils import get_isoforms

CFD = os.path.dirname(__file__)


def test_get_isoforms_wrong_id():
    """
    Test the get_isoforms function when the uniprot_id str length is wrong
    """
    uniprot_id = "xxx"
    e_message = f"{uniprot_id} is not valid by its length {len(uniprot_id)}"
    with pytest.raises(ValueError, match=e_message):
        get_isoforms(uniprot_id)


def test_get_isoforms_obsolete_id():
    """
    Test the get_isoforms function when the uniprot_id is obsolete
    """
    uniprot_id = "P00016"
    e_message = f"{uniprot_id} is obsolete"
    with pytest.raises(ValueError, match=e_message):
        get_isoforms(uniprot_id)
    try:
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass


def test_get_isoforms_no_iso():
    """
    Test the get_isoforms function when there is no isoform
    """
    uniprot_id = "Q9H0H0"
    isoforms = get_isoforms(uniprot_id)
    assert isoforms == {"Q9H0H0": []}, "Q9H0H0 isoform is not empty."
    try:
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass


def test_get_isoforms():
    """
    Test the get_isoforms function
    """
    uniprot_id = "Q92879"
    expected = {
        "Q92879-1": [],
        "Q92879-2": [(231, 234, "", "Missing")],
        "Q92879-3": [(231, 234, "", "Missing"), (297, 297, "S", "SA")],
        "Q92879-4": [
            (1, 1, "M", "MAAFKLDFLPEMMVDHCSLNSSPVSKKM"),
            (104, 104, "", "Missing"),
        ],
        "Q92879-5": [(1, 17, "", "Missing"), (104, 104, "", "Missing")],
        "Q92879-6": [(104, 104, "", "Missing")],
    }
    isoforms = get_isoforms(uniprot_id)
    assert isoforms == expected, "Q92879 isoforms are wrong."
    try:
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass

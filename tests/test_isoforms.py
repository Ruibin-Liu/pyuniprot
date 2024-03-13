"""
Test all utils functions here.
"""

import os

import pytest

from pyuniprot.utils import AA, get_alt_resids, get_isoforms

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


def test_get_alt_wrong_aa():
    """
    Test wrong AA names
    """
    uniprot_id = "P01116-1"
    uniprot_resid = 200
    residue_type = "X"

    e_message = f"{residue_type} not one of the {len(AA)} amino acids"
    with pytest.raises(ValueError, match=e_message):
        get_alt_resids(uniprot_id, uniprot_resid, residue_type)

    residue_type = "glu"
    e_message = f"{residue_type} not one of the {len(AA)} amino acids"
    with pytest.raises(ValueError, match=e_message):
        get_alt_resids(uniprot_id, uniprot_resid, residue_type)

    uniprot_resid = 12
    residue_type = "C"
    e_message = f"{uniprot_id} {uniprot_resid} is not {residue_type}"
    with pytest.raises(ValueError, match=e_message):
        get_alt_resids(uniprot_id, uniprot_resid, residue_type)

    try:
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass


def test_get_alt_resids_oob():
    """
    Test out of bounds resids
    """
    uniprot_id = "P01116-1"
    uniprot_resid = 200
    residue_type = "C"

    e_message = f"{uniprot_id} {uniprot_resid} is beyond the sequence of length 189"
    with pytest.raises(ValueError, match=e_message):
        get_alt_resids(uniprot_id, uniprot_resid, residue_type)
    try:
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass


def test_get_alt_resids():
    """
    Test different resid situations
    """
    uniprot_id = "Q92879-4"
    uniprot_resid = 460
    residue_type = "I"

    expected = [
        ("Q92879-1", 434),
        ("Q92879-2", 430),
        ("Q92879-3", 431),
        ("Q92879-4", 460),
        ("Q92879-5", 416),
        ("Q92879-6", 433),
    ]
    resids = get_alt_resids(uniprot_id, uniprot_resid, residue_type)
    assert (
        resids == expected
    ), f"{uniprot_id} {uniprot_resid} {residue_type} alt resids wrong"
    try:
        os.remove(f"{CFD}/{uniprot_id}.txt")
    except OSError:
        pass


# def test():
#     """
#     Test the get_isoforms function when there is no isoform
#     """
#     uniprot_id = "P01116"
#     isoforms = get_isoforms(uniprot_id)
#     print(isoforms)

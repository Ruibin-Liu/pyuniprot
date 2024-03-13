"""Find all isoforms given a Uniprot ID.
"""

from __future__ import annotations

import re
import warnings
from collections import defaultdict

from pyuniprot.Uniprot import Uniprot

AA = {
    "A",
    "R",
    "N",
    "D",
    "C",
    "E",
    "Q",
    "G",
    "H",
    "I",
    "L",
    "K",
    "M",
    "F",
    "P",
    "S",
    "T",
    "W",
    "Y",
    "V",
}


def _get_var_seqs(uniprot: Uniprot) -> dict[int, list[tuple]]:
    """Get all the VAR_SEQ records for isoforms.

    Args:
        uniprot (Uniprot): the Uniprot object

    Returns:
        dict[str, tuple]: each isoform index as key and a list of tuples of
            (seq_begin, seq_end, sequence_in_canonical, sequence_in_isoform) as value
    """
    results = defaultdict(list)
    isoform_regex = r"isoform\s\d+[a-zA-Z]?"
    try:
        var_seqs = uniprot.category_lines["FT"].feature_tables["VAR_SEQ"]
        for var_seq in var_seqs:
            if "in isoform" not in var_seq["note"]:  # usually site mutation
                continue

            if "in_range" in var_seq:
                in_range = var_seq["in_range"]
                seq_begin, seq_end = in_range.seq_begin, in_range.seq_end
            else:
                seq_begin, seq_end = var_seq["at_site"], var_seq["at_site"]

            note = var_seq["note"]
            seqs = note.split(" -> ")
            if len(seqs) == 2:
                sequence_in_canonical = seqs[0]
                sequence_in_isoform = seqs[1].split(" ")[0]
            else:
                sequence_in_canonical = ""
                sequence_in_isoform = "Missing"

            isoforms = re.findall(isoform_regex, note)
            for isoform in isoforms:
                isoform_index = isoform.split(" ")[-1]
                results[isoform_index].append(
                    (seq_begin, seq_end, sequence_in_canonical, sequence_in_isoform)
                )
    except Exception as e:
        raise ValueError(f"{e}")
    return results


def get_isoforms(uniprot_id: str) -> dict[str, list]:
    """Get the isoforms given Uniprot Accession number or isoform ID.

    Args:
        uniprot_id (str): Uniprot Accession umber of isoform ID.

    Returns:
        dict[str, list]: isoform IDs as keys and a list of sequence differences
            from the primary/displayed one. The list element is a tuple of
            (seq_begin, seq_end, sequence_in_canonical, sequence_in_isoform) where
            seq_begin and seq_end are the two residue numbers denoting the start and end
            residues in the canonical isoform, sequence_in_canonical is the sequence that
            are between seq_begin and seq_end in the canonical isoform, and sequence_in_isoform
            is the sequence that are in the current isoform.

    Raises:
        ValueError: if the provided uniprot_id is invalid in `length`; or the uniprot_id is obsolete.
    """
    results: dict[str, list] = {}
    uniprot_id_str = uniprot_id.split("-")[0]
    if len(uniprot_id_str) not in [6, 10]:
        raise ValueError(
            f"{uniprot_id_str} is not valid by its length {len(uniprot_id_str)}"
        )
    uniprot = Uniprot(uniprot_id_str)
    try:
        isoforms = uniprot.category_lines["CC"].comments["ALTERNATIVE PRODUCTS"]
        for record in isoforms.split(";"):
            if "Named isoforms" in record:
                var_seqs = _get_var_seqs(uniprot)
                continue

            if "Name=" in record:
                isoform_index = record.split("=")[-1]
                continue

            if "IsoId" in record:
                isoform = record.split("=")[-1].split(", ")[
                    0
                ]  # The 2nd split is necessary; check P63208.txt
                continue

            if "Displayed" in record:
                results[isoform] = []  # This is the canonical/primary/displayed one
            elif "Sequence=" in record:
                results[isoform] = var_seqs[isoform_index]

    except KeyError:
        if uniprot.category_lines:  # the provided uniprot_id is the only isoform
            results[uniprot_id_str] = []
        else:  # the uniprot_id is obsolete
            raise ValueError(f"{uniprot_id_str} is obsolete")

    return results


def get_alt_resids(
    uniprot_id: str, uniprot_resid: int, residue_type: str
) -> list[tuple[str, int | str]]:
    """Get all residue IDs in all isoforms given the residue ID in one.

    Args:
        uniprot_id (str): Uniprot Accession number or an isoform ID
        uniprot_resid (str): Uniprot residue number
        residue_type (str): single-letter amino acid type

    Returns:
        list[tuple[str, int]]: a list of (isoform_id, residue_id)

    Raises:
        ValueError: if the provided uniprot_id is invalid in `length`; or the uniprot_id is obsolete;
            or if the uniprot_resid is not in the provided uniprot_id; or the corresponding type is
            not the same as residue_type
    """
    if residue_type not in AA:
        raise ValueError(f"{residue_type} not one of the {len(AA)} amino acids")

    results: list[tuple[str, int | str]] = []

    isoforms = get_isoforms(uniprot_id)
    if "-" not in uniprot_id and len(isoforms) > 1:
        for isoform, diff in isoforms.items():
            if not diff:
                target_isoform = isoform
                break
        warning = f"Warning: {uniprot_id} has {len(isoforms)} isoforms,"
        warning += (
            f"the canonical one {isoform} is used since an isoform is not provided."
        )
        warnings.warn(warning, stacklevel=2)
    else:
        target_isoform = uniprot_id

    target_uniprot = Uniprot(target_isoform)
    target_sequence = target_uniprot.category_lines["SQ"]
    uniprot_resid = int(uniprot_resid)
    if uniprot_resid > target_sequence.length or uniprot_resid <= 0:
        raise ValueError(
            f"{uniprot_id} {uniprot_resid} is beyond the sequence of length {target_sequence.length}"
        )

    if target_sequence.sequence[uniprot_resid - 1] != residue_type:
        raise ValueError(f"{target_isoform} {uniprot_resid} is not {residue_type}")

    can_isoform: str = ""
    resid_in_can: int | str = (
        "-"  # Every isoform resid is relative to the canonical form so we convert to it
    )
    for isoform, diff in isoforms.items():
        if not diff:
            can_isoform = isoform
            can_uniprot = Uniprot(can_isoform)
            if target_isoform == can_isoform:
                resid_in_can = uniprot_resid
            else:
                target_resids_in_can: list[int | str] = []
                last_resid: int = 0
                for begin, end, can_seq, iso_seq in isoforms[target_isoform]:
                    for _ in range(begin - last_resid - 1):
                        last_resid += 1
                        target_resids_in_can.append(last_resid)
                    if iso_seq == "Missing":
                        for _ in range(end - begin + 1):
                            last_resid += 1
                    elif len(can_seq) > len(iso_seq):
                        for _ in range(len(iso_seq)):
                            last_resid += 1
                            target_resids_in_can.append(last_resid)
                        for _ in range(len(can_seq) - len(iso_seq)):
                            last_resid += 1
                            target_resids_in_can.append("-")
                    else:
                        for _ in range(len(can_seq)):
                            last_resid += 1
                            target_resids_in_can.append(last_resid)
                        for _ in range(len(iso_seq) - len(can_seq)):
                            target_resids_in_can.append("-")
                n_existed = len(target_resids_in_can)
                for _ in range(target_uniprot.category_lines["SQ"].length - n_existed):
                    last_resid += 1
                    target_resids_in_can.append(last_resid)
                resid_in_can = target_resids_in_can[uniprot_resid - 1]

    if resid_in_can == "-":
        results.append((target_isoform, uniprot_resid))
        return results

    for isoform, diff in isoforms.items():
        if not diff:
            results.append((can_isoform, resid_in_can))
            continue

        if isoform == target_isoform and (target_isoform, uniprot_resid) not in results:
            results.append((target_isoform, uniprot_resid))
            continue

        can_resids_in_isoform: list[int | str] = []
        last_resid = 0
        for begin, end, can_seq, iso_seq in isoforms[isoform]:
            for _ in range(begin - last_resid - 1):
                last_resid += 1
                can_resids_in_isoform.append(last_resid)
            if iso_seq == "Missing":
                for _ in range(end - begin + 1):
                    can_resids_in_isoform.append("-")
            elif len(can_seq) >= len(iso_seq):
                for _ in range(len(iso_seq)):
                    last_resid += 1
                    can_resids_in_isoform.append(last_resid)
                for _ in range(len(can_seq) - len(iso_seq)):
                    last_resid += 1
                    can_resids_in_isoform.append("-")
            else:
                for _ in range(len(can_seq)):
                    last_resid += 1
                    can_resids_in_isoform.append(last_resid)
                for _ in range(len(iso_seq) - len(can_seq)):
                    last_resid += 1
        n_existed = len(can_resids_in_isoform)
        for _ in range(can_uniprot.category_lines["SQ"].length - n_existed):
            last_resid += 1
            can_resids_in_isoform.append(last_resid)
        isoform_resid = can_resids_in_isoform[int(resid_in_can) - 1]
        results.append((isoform, isoform_resid))

    return results

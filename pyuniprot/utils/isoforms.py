"""Find all isoforms given a Uniprot ID.
"""

from __future__ import annotations

import re
from collections import defaultdict

from pyuniprot.Uniprot import Uniprot


def _get_var_seqs(uniprot: Uniprot) -> dict[int, list[tuple]]:
    """Get all the VAR_SEQ records for isoforms.

    Args:
        uniprot (Uniprot): the Uniprot object

    Returns:
        dict[str, tuple]: each isoform index as key and a list of tuples of
            (seq_begin, seq_end, sequence_in_canonical, sequence_in_isoform) as value
    """
    results = defaultdict(list)
    isoform_regex = r"isoform\s\d+"
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
                isoform_index = int(isoform.split(" ")[-1])
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
                isoform_index = int(record.split("=")[-1])
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

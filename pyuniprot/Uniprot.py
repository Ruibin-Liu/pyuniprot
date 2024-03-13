from __future__ import annotations

import io
import os
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Union

from .DB import HGNC, PANTHER, PDB, SeqRange


@dataclass
class ID:
    """Entry name and length"""

    entry_name: str
    is_reviewed: bool
    aa_length: int


@dataclass
class AC:
    """Accessions"""

    primary_accession: str
    secondary_accessions: list[str]


@dataclass
class DT:
    """Brief history of the entry"""

    history: list[tuple[date, str]]


@dataclass
class EC:
    """Enzyme Commission; 'EC' itself not in a Uniprot txt file"""

    EC_number: str
    ECO: str | None
    ECO_pubmed: str | None


@dataclass
class DE:
    """Protein names"""

    recommended_name: str | None
    ec_record: EC | None
    alt_names: list[str] | None
    contains: str | None


@dataclass
class GN:
    """Gene names"""

    name: str
    synonyms: list[str] | None


@dataclass
class OSCX:
    """Organism names; OS+OC+OX lines"""

    organism: str
    taxonomic_lineage: list[str]  # OC lines
    taxonomic_identifier: int  # OX
    _covered_keywords: tuple[str, str, str] = ("OS", "OC", "OX")


@dataclass
class CrossRef:
    """Cross reference record."""

    pubmed: str
    doi: str


@dataclass
class REF:
    """Reference record; 'REF' itself not in a Uniprot txt file"""

    number: int  # RN
    positions: str | None  # RP
    comments: str | None  # RC
    cross_ref: CrossRef | None  # RX
    group: str | None  # RG
    authors: list[str] | None  # RA
    title: str | None  # RT
    cite: str | None  # RL


@dataclass
class RNPCXATL:
    """References; RN+RP+RC+RX+RA+RT+RL lines"""

    references: list[REF]
    _covered_keywords: tuple[str, str, str, str, str, str, str] = (
        "RN",
        "RP",
        "RC",
        "RX",
        "RA",
        "RT",
        "RL",
    )


@dataclass
class CC:
    """Comments"""

    comments: dict[str, str]


@dataclass
class DR:
    """Database references."""

    database_references: dict[str, list]


@dataclass
class PE:
    """Protein existence."""

    protein_existence: str


@dataclass
class KW:
    """Keywords."""

    keywords: list[str]


@dataclass
class FT:
    """Feature tables."""

    feature_tables: dict[str, list[dict[str, str | int | SeqRange | None]]]


@dataclass
class SQ:
    """Sequence."""

    sequence: str
    length: int
    weight: int
    crc_checksum_value: str
    crc_bits: int


UNIPROT = Union[ID, AC, DT, DE, GN, OSCX, RNPCXATL, CC, DR, PE, KW, FT, SQ]


class Uniprot:
    """The python object representing all information of a Uniprot txt file."""

    def __init__(
        self,
        uniprot_id: str,
        save_txt: bool = True,
        local_download_dir: str | os.PathLike | None = None,
    ) -> None:
        """Init class with a Uniprot ID.

        Args:
            uniprot_id (str): Uniprot Access Number. It looks at the the <local_download_dir> first for <uniprot_id>.txt,
                and if not found, it will try to fetch content from https://rest.uniprot.org/uniprotkb/<uniprot_id>.txt.
            save_txt (bool, optional): whether to save the fetched txt content to a <local_download_dir>/<uniprot_id>.txt
                file when that file no already existing. Defaults to False.
            local_download_dir (str | os.PathLike | None, optional): where to save the downloaded Uniprot txt file.
                Defaults to None and the current working directory is used instead.
        """  # noqa
        self._uniprot_id: str = uniprot_id
        self.save_txt: bool = save_txt
        if local_download_dir is None:
            local_download_dir = os.getcwd()
        self._local_download_dir: str | os.PathLike | None = local_download_dir
        self._uniprot_txt_url = (
            f"https://rest.uniprot.org/uniprotkb/{self.uniprot_id}.txt"
        )
        self._uniprot_txt_file: str | os.PathLike | io.StringIO | None = None
        txt_file = Path(self.local_download_dir, f"{self.uniprot_id}.txt")
        if txt_file.exists():
            self._uniprot_txt_file = txt_file
        self._category_lines: dict[str, UNIPROT] | None = None
        self._get_category_lines()

    @property
    def uniprot_id(self):
        return self._uniprot_id

    @property
    def local_download_dir(self):
        return self._local_download_dir

    @local_download_dir.setter
    def local_download_dir(self, dir: str | os.PathLike):
        """Set the directory to save downloaded Uniprot txt files.

        Args:
            dir (str | os.PathLike): directory path str or Path.
        """
        self._local_download_dir = dir

    @property
    def uniprot_txt_url(self):
        return self._uniprot_txt_url

    @uniprot_txt_url.setter
    def uniprot_txt_url(self, url: str):
        """Set the Uniprot txt file URL if not the official REST one.

        Args:
            url (str): URL link.
        """
        self._uniprot_txt_url = url

    @property
    def uniprot_txt_file(self):
        return self._uniprot_txt_file

    @uniprot_txt_file.setter
    def uniprot_txt_file(self, path: str | os.PathLike | io.StringIO):
        """Set the Uniprot txt file path

        Args:
            path (str | os.PathLike| io.StringIO): file-like or path to the file.

        Raises:
            FileExistsError: if <path> is not in the file system.
        """
        if isinstance(path, os.PathLike) and not Path(path).exists():
            raise FileExistsError(f"Cannot find {path}.")
        self._uniprot_txt_file = path

    @property
    def category_lines(self):
        return self._category_lines

    @category_lines.setter
    def category_lines(self, content_dict: dict[str, UNIPROT]):
        """Set the category_lines by the Uniprot txt file content.

        Args:
            content_dict (defaultdict(list)): the Uniprot txt file content as a dict of list of lines.

        Raises:
            AttributeError: if it is already set.
        """
        if self.category_lines is None:
            self._category_lines = content_dict
        else:
            raise AttributeError("category_lines already set.")

    def _get_category_lines(self) -> None:
        """Parse the Uniprot txt file into a dict of list of lines.

        Raises:
            ValueError: if the file cannot be found locally nor through
                Uniprot REST service.
        """
        content_dict: dict[str, UNIPROT] = {}
        if self.uniprot_txt_file is None:
            try:
                with urllib.request.urlopen(self.uniprot_txt_url) as response:
                    raw_data = response.read()
                text = raw_data.decode("utf-8")
                txt_file: io.StringIO | os.PathLike = io.StringIO(text)
                if self.save_txt:
                    txt_file = Path(self.local_download_dir, f"{self.uniprot_id}.txt")
                    with open(txt_file, "w", encoding="utf-8") as u_file:
                        u_file.write(text)

                self.uniprot_txt_file = txt_file
            except urllib.error.HTTPError:
                raise ValueError(f"Cannot download from url {self.uniprot_txt_url}.")

        if not isinstance(self.uniprot_txt_file, io.StringIO):
            u_file = open(self.uniprot_txt_file, "r", encoding="utf-8")
        else:
            u_file = self.uniprot_txt_file

        line: str = u_file.readline()
        references: list = []
        while line and line[0:2] != "//":
            if line.startswith("ID"):
                items = line[2:-1].split()
                entry_name = items[0]
                if items[1] == "Reviewed;":
                    is_reviewed = True
                else:
                    is_reviewed = False
                aa_length = int(items[2])
                content_dict["ID"] = ID(entry_name, is_reviewed, aa_length)
            elif line.startswith("AC"):
                accessions: list[str] = []
                while line.startswith("AC"):
                    items = line[2:-1].split()
                    accessions.extend(items)
                    line = u_file.readline()
                accessions = [i.strip(";") for i in accessions]
                primary_accession = accessions[0]
                accessions.remove(primary_accession)
                content_dict["AC"] = AC(primary_accession, accessions)
                continue
            elif line.startswith("DT"):
                history_lines: list[tuple[date, str]] = []
                date_format = "%d-%b-%Y"
                while line.startswith("DT"):
                    items = line[2:-1].split(",")
                    date_object = datetime.strptime(
                        items[0].strip(), date_format
                    ).date()
                    event = items[1].strip()
                    history_lines.append((date_object, event))
                    line = u_file.readline()
                content_dict["DT"] = DT(history_lines)
                continue
            elif line.startswith("DE"):
                alt_names: list[str] = []
                ec_line: str = "DE            EC="
                ec_record: EC | None = None
                contains: str | None = None
                recommended_name: str | None = None
                while line.startswith("DE"):
                    if line.startswith("DE   RecName:"):
                        recommended_name = line[:-2].split("=")[-1]
                    elif line.startswith("DE     RecName:"):
                        contains = line[:-2].split("=")[-1]
                    elif line.startswith("DE   AltName:"):
                        alt_name = line[:-2].split("=")[-1]
                        alt_names.append(alt_name)
                    elif line.startswith(ec_line):
                        items = line[len(ec_line) : -2].split()
                        EC_number = items[0]
                        ECO: str | None = None
                        ECO_pubmed: str | None = None
                        if len(items) > 1:
                            evidence: list[str] = items[1].split("|")
                            ECO = evidence[0][5:]
                            if len(evidence) > 1:
                                ECO_pubmed = evidence[1][7:]
                        ec_record = EC(EC_number, ECO, ECO_pubmed)
                    line = u_file.readline()
                content_dict["DE"] = DE(
                    recommended_name, ec_record, alt_names, contains
                )
                continue
            elif line.startswith("GN"):
                items = line[2:-2].split("; ")
                gene_name: str = items[0].split("=")[-1].split()[0]
                synonyms: list[str] | None = None
                if len(items) > 1 and "Synonyms" in items[1]:
                    synonyms = items[1].split("=")[-1].split(", ")
                content_dict["GN"] = GN(gene_name, synonyms)
            elif line.startswith(("OS", "OC", "OX")):
                if line.startswith("OS"):
                    organism = line[2:-2].strip()
                elif line.startswith("OC"):
                    taxonomic_lineage: list[str] = []
                    while line.startswith("OC"):
                        items = line[2:-2].strip().split("; ")
                        taxonomic_lineage.extend(items)
                        line = u_file.readline()
                    continue
                elif line.startswith("OX"):
                    taxonomic_identifier = int(line[2:-2].split("=")[-1].split()[0])
                    content_dict["OSCX"] = OSCX(
                        organism, taxonomic_lineage, taxonomic_identifier
                    )
            elif line.startswith("RN"):
                number = int(line[6:-2].split("]")[0])
                positions: str | None = None
                comments: str | None = None
                cross_ref: CrossRef | None = None
                group: str | None = None
                authors: list[str] | None = None
                title: str | None = None
                cite: str | None = None
                line = u_file.readline()
                while not line.startswith(("RN", "CC")):
                    if line.startswith("RP"):
                        positions = ""
                        while line.startswith("RP"):
                            positions += line[5:-1]
                            line = u_file.readline()
                        positions = positions.rstrip(".")
                    if line.startswith("RC"):
                        comments = ""
                        while line.startswith("RC"):
                            comments += line[5:-1]
                            line = u_file.readline()
                        comments = comments.rstrip(";")
                    if line.startswith("RG"):
                        group = line[5:-2]
                        line = u_file.readline()
                    if line.startswith("RX"):
                        items = line[2:-2].split("; ")
                        pubmed = items[0].split("=")[-1]
                        doi = items[1].split("=")[-1] if len(items) > 1 else ""
                        cross_ref = CrossRef(pubmed, doi)
                        line = u_file.readline()
                    if line.startswith("RA"):
                        authors = []
                        while line.startswith("RA"):
                            items = line[5:-2].strip().split(", ")
                            authors.extend(items)
                            line = u_file.readline()
                    if line.startswith("RT"):
                        title = ""
                        while line.startswith("RT"):
                            title += line[5:-1].lstrip('"').rstrip('"')
                            line = u_file.readline()
                        title = title.rstrip(";").rstrip('"').rstrip(".")
                    if line.startswith("RL"):
                        cite = ""
                        while line.startswith("RL"):
                            cite += line[5:-2]
                            line = u_file.readline()
                ref = REF(
                    number, positions, comments, cross_ref, group, authors, title, cite
                )
                references.append(ref)
                continue
            elif line.startswith("CC"):
                content_dict["RNPCXATL"] = RNPCXATL(references)
                all_comments: dict[str, str] = {}
                new_comment_tag: str = "CC   -!- "
                comment_end: str = "CC   ----"
                while line.startswith("CC"):
                    new_comment: str = ""
                    if line.startswith(new_comment_tag):
                        semicolon_pos = line.find(":")
                        comment_name: str = line[len(new_comment_tag) : semicolon_pos]
                        all_comments[comment_name] = ""
                        new_comment += line[semicolon_pos + 1 : -1].strip()
                        line = u_file.readline()
                        while not line.startswith(
                            new_comment_tag
                        ) and not line.startswith(comment_end):
                            new_comment += line[len(new_comment_tag) : -1]
                            line = u_file.readline()
                        if all_comments[comment_name]:
                            all_comments[comment_name] = (
                                all_comments[comment_name]
                                + ";; "
                                + new_comment.rstrip(".").rstrip(";")
                            )
                        else:
                            all_comments[comment_name] = new_comment.rstrip(".").rstrip(
                                ";"
                            )
                        continue
                    line = u_file.readline()
                content_dict["CC"] = CC(
                    all_comments
                )  # TODO: parse each comment_name differently so that more info is directly accessible.
                continue
            elif line.startswith("DR"):
                db_reference: dict[str, list] = defaultdict(list)
                while line.startswith("DR"):
                    db_name: str = line[5:-2].split(";")[0]
                    db_content: list[str] = line[5:-1].strip(".").split(";")[1:]
                    if db_name == "PDB":
                        pdb_id: str = db_content[0].strip()
                        experiment_method: str = db_content[1].strip()

                        res: list[str] = db_content[2].strip().split()
                        resolution: float | str = (
                            "-" if res[0] == "-" else float(res[0])
                        )
                        resolution_unit: str = res[1] if len(res) > 1 else ""

                        seq_coverings: list[str] = db_content[3].strip().split(", ")
                        all_chain_ids: list[str] = []
                        all_seq_ranges: list[SeqRange] = []
                        for seq_covering in seq_coverings:
                            seq = seq_covering.split("=")
                            chain_ids: list[str] = seq[0].split("/")
                            all_chain_ids.extend(chain_ids)
                            if len(seq) > 1 and "-" != seq[1]:
                                uniprot_resid_start: int | str = int(
                                    seq[1].split("-")[0]
                                )
                                uniprot_resid_end: int | str = int(seq[1].split("-")[1])
                            else:
                                uniprot_resid_start, uniprot_resid_end = "", ""
                            all_seq_ranges.append(
                                SeqRange(uniprot_resid_start, uniprot_resid_end)
                            )
                        all_chain_ids = sorted(list(set(all_chain_ids)))

                        db_reference[db_name].append(
                            PDB(
                                pdb_id,
                                experiment_method,
                                resolution,
                                resolution_unit,
                                all_chain_ids,
                                all_seq_ranges,
                            )
                        )
                    elif db_name == "HGNC":
                        hgnc_id: int = int(db_content[0].strip().split(":")[-1])
                        hgnc_name: str = db_content[1].strip()
                        db_reference[db_name].append(HGNC(hgnc_id, hgnc_name))
                    elif db_name == "PANTHER":
                        family_id: str = ""
                        family_name: str = ""
                        family_occurrence: int = 1
                        subfamily_id: str = ""
                        subfamily_name: str = ""
                        subfamily_occurrence: int = 1
                        if ":" in db_content[0]:
                            family_id, subfamily_id = db_content[0].strip().split(":")
                            subfamily_name = db_content[1].strip()
                            subfamily_occurrence = int(db_content[2].strip())
                            line = u_file.readline()
                            db_name = line[5:-2].split(";")[0]
                            if db_name == "PANTHER":
                                db_content = line[5:-1].strip(".").split(";")[1:]
                                family_name = db_content[1].strip()
                                family_occurrence = int(db_content[2].strip())
                            else:
                                continue
                        else:
                            family_name = db_content[1].strip()
                            family_occurrence = int(db_content[2].strip())
                            line = u_file.readline()
                            db_name = line[5:-2].split(";")[0]
                            if db_name == "PANTHER":
                                db_content = line[5:-1].strip(".").split(";")[1:]
                                family_id, subfamily_id = (
                                    db_content[0].strip().split(":")
                                )
                                subfamily_name = db_content[1].strip()
                                subfamily_occurrence = int(db_content[2].strip())
                            else:
                                continue
                        db_reference[db_name].append(
                            PANTHER(
                                family_id,
                                family_name,
                                family_occurrence,
                                subfamily_id,
                                subfamily_name,
                                subfamily_occurrence,
                            )
                        )
                    else:
                        db_reference[db_name].append(tuple(db_content))
                    line = u_file.readline()
                content_dict["DR"] = DR(db_reference)
                continue
            elif line.startswith("PE"):
                protein_existence: str = line[5:-2]
                level_pos: int = protein_existence.find("Evidence at ")
                content_dict["PE"] = PE(protein_existence[(level_pos + 12) :])
            elif line.startswith("KW"):
                keywords: list[str] = []
                while line.startswith("KW"):
                    items = line[5:-2].split("; ")
                    keywords.extend(items)
                    line = u_file.readline()
                content_dict["KW"] = KW(keywords)
                continue
            elif line.startswith("FT"):
                feature_tables: dict[
                    str, list[dict[str, str | int | SeqRange | None]]
                ] = defaultdict(list)
                while line.startswith("FT"):
                    record_name: str = line[2:20].strip()
                    if record_name != "":
                        one_record: dict[str, str | int | SeqRange | None] = {}
                        site_or_range: str | int | SeqRange | None = None
                        seq_ids: list[str] = [
                            seq_id for seq_id in line[20:].strip().split("..")
                        ]
                        isoform: str = self.uniprot_id
                        if ":" in seq_ids[0]:
                            isoform = seq_ids[0].split(":")[0]
                        if len(seq_ids) == 1:
                            name: str = "at_site"
                            try:
                                site_or_range = int(seq_ids[0].split(":")[-1])
                            except ValueError:
                                site_or_range = seq_ids[0].split(":")[-1]
                        else:
                            name = "in_range"
                            seq_start: int | str = "?"
                            seq_end: int | str = "?"
                            if "?" not in seq_ids[0]:
                                try:
                                    seq_start = int(seq_ids[0].split(":")[-1])
                                except ValueError:
                                    seq_start = seq_ids[0].split(":")[-1]
                            if "?" not in seq_ids[1]:
                                try:
                                    seq_end = int(seq_ids[1].split(":")[-1])
                                except ValueError:
                                    seq_end = seq_ids[1].split(":")[-1]
                            site_or_range = SeqRange(seq_start, seq_end)
                        one_record[name] = site_or_range
                        one_record["isoform"] = isoform
                        line = u_file.readline()
                        record_name_like = line[2:20].strip()
                        one_record_lines: str = ""
                        while record_name_like == "":
                            if "/" in line:
                                one_record_lines += line[19:-1]
                            else:
                                one_record_lines += line[21:-1]
                            line = u_file.readline()
                            record_name_like = line[2:20].strip()
                        # if record_name == 'VAR_SEQ':
                        #     print(one_record_lines)
                        attrs: list[str] = one_record_lines.rstrip().split("  /")
                        for attr in attrs[1:]:
                            attr_name, attr_content = attr.strip().split('="')
                            one_record[attr_name] = attr_content.strip('"')
                        feature_tables[record_name].append(one_record)
                content_dict["FT"] = FT(feature_tables)
                continue
            elif line.startswith("SQ"):
                sequence: str = ""
                items = line[2:-1].strip().split()
                length: int = int(items[1])
                weight: int = int(items[3])
                crc_checksum_value: str = items[5]
                crc_bits: int = int(items[-1][3:-1])
                line = u_file.readline()
                while line.startswith("  "):
                    sequence += line.strip().replace(" ", "")
                    line = u_file.readline()
                content_dict["SQ"] = SQ(
                    sequence, length, weight, crc_checksum_value, crc_bits
                )
                break

            line = u_file.readline()
        # print(line)

        self._category_lines = content_dict
        # print(self.category_lines["FT"].feature_tables)

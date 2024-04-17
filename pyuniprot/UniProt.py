from __future__ import annotations

import io
import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .dict_to_property import DictToProp


@dataclass
class Sequence:
    """Sequence."""

    sequence: str
    length: int
    weight: int
    crc_checksum_value: str
    crc_bits: int


class UniProt:
    """The python object representing all information of a Uniprot JSON file."""

    def __init__(
        self,
        uniprot_id: str,
        save_json: bool = True,
        local_download_dir: str | os.PathLike | None = None,
    ) -> None:
        """Init class with a Uniprot ID.

        Args:
            uniprot_id (str): Uniprot Access Number. It looks at the the <local_download_dir> first for <uniprot_id>.json,
                and if not found, it will try to fetch content from https://rest.uniprot.org/uniprotkb/<uniprot_id>.
            save_json (bool, optional): whether to save the fetched json content to a <local_download_dir>/<uniprot_id>.json
                file when that file no already existing. Defaults to False.
            local_download_dir (str | os.PathLike | None, optional): where to save the downloaded Uniprot json file.
                Defaults to None and the current working directory is used instead.
        """  # noqa
        self._uniprot_id: str = uniprot_id
        self.save_json: bool = save_json
        if local_download_dir is None:
            local_download_dir = os.getcwd()
        self._local_download_dir: str | os.PathLike | None = local_download_dir
        self._uniprot_json_url = f"https://rest.uniprot.org/uniprotkb/{self.uniprot_id}"
        self._uniprot_json_file: str | os.PathLike | io.StringIO | None = None
        json_file = Path(self.local_download_dir, f"{self.uniprot_id}.json")
        if json_file.exists():
            self._uniprot_json_file = json_file
        self._raw_json: str | None = None  # json is only a str in python
        self._properties: dict = {}

        self._get_raw_json()
        self._get_properties()

    @property
    def uniprot_id(self):
        return self._uniprot_id

    @property
    def local_download_dir(self):
        return self._local_download_dir

    @local_download_dir.setter
    def local_download_dir(self, dir: str | os.PathLike):
        """Set the directory to save downloaded Uniprot json files.

        Args:
            dir (str | os.PathLike): directory path str or Path.
        """
        self._local_download_dir = dir

    @property
    def uniprot_json_url(self):
        return self._uniprot_json_url

    @uniprot_json_url.setter
    def uniprot_json_url(self, url: str):
        """Set the Uniprot json file URL if not the official REST one.

        Args:
            url (str): URL link.
        """
        self._uniprot_json_url = url

    @property
    def uniprot_json_file(self):
        return self._uniprot_json_file

    @uniprot_json_file.setter
    def uniprot_json_file(self, path: str | os.PathLike | io.StringIO):
        """Set the UniProt json file path

        Args:
            path (str | os.PathLike| io.StringIO): file-like or path to the file.

        Raises:
            FileExistsError: if <path> is not in the file system.
        """
        if isinstance(path, os.PathLike) and not Path(path).exists():
            raise FileExistsError(f"Cannot find {path}.")
        self._uniprot_json_file = path

    @property
    def raw_json(self):
        return self._raw_json

    @raw_json.setter
    def raw_json(self, content: str):
        """Set the uniprot JSON by json content (str repr in python).

        Args:
            content (str): JSON as a python str.

        Raises:
            AttributeError: if it is already set.
        """
        if self.raw_json is None:
            self._raw_json = content
        else:
            raise AttributeError("raw_json already set.")

    def _get_raw_json(self) -> None:
        """Get json content"""
        if self.uniprot_json_file is None:
            try:
                with urllib.request.urlopen(self.uniprot_json_url) as response:
                    raw_data = response.read()
                json_content = raw_data.decode("utf-8")
                json_file: io.StringIO | os.PathLike = io.StringIO(json_content)
                if self.save_json:
                    json_file = Path(
                        self.local_download_dir,
                        f"{self.uniprot_id}.json",
                    )
                    with open(json_file, "w", encoding="utf-8") as j_file:
                        j_file.write(json_content)

                self.uniprot_json_file = json_file
            except urllib.error.HTTPError:
                raise ValueError(f"Cannot download from url {self.uniprot_json_url}.")

        if not isinstance(self.uniprot_json_file, io.StringIO):
            j_file = open(self.uniprot_json_file, "r", encoding="utf-8")
        else:
            j_file = self.uniprot_json_file

        self.raw_json = json.load(j_file)

        try:
            j_file.close()
        except Exception:
            pass

    def _get_properties(self) -> None:
        """
        Turn raw json to properties.
        """
        self._properties = DictToProp(self.raw_json)._properties

    def __getattr__(self, key: str) -> str | list | DictToProp:
        """Retrieve properties."""
        if key in self._properties:
            return self._properties[key]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

from __future__ import annotations

import io
import json
import os
import urllib.request
from pathlib import Path


class UniRef:
    """The python object representing all information of a UniRef json file."""

    def __init__(
        self,
        uniprot_id: str | None,
        thresh: int = 100,
        save_json: bool = True,
        local_download_dir: str | os.PathLike | None = None,
    ) -> None:
        """Init class with a Uniprot ID.

        Args:
            uniprot_id (str, optional): Uniprot Access Number. If set, it looks at the the <local_download_dir> first for
                UniRef<thresh>_<uniprot_id>.json, and if not found, it will try to fetch content from
                rest.uniprot.org/uniref/UniRef<thresh>_<uniprot_id>.json. `thresh` is specified as below.
            thresh (int, optional): sequence identity threshold and it can only be 100, 90, or 50.
            save_json (bool, optional): whether to save the fetched json content to a
                <local_download_dir>/UniRef<thresh>_<uniprot_id>.json file when that file no already existing.
                Defaults to False.
            local_download_dir (str | os.PathLike | None, optional): where to save the downloaded UniRef JSON file.
                Defaults to None and the current working directory is used instead.

        Raises:
            ValueError: if thresh is not one of 100, 90, or 50.
        """  # noqa
        self._uniprot_id: str | None = uniprot_id
        if not self._uniprot_id:
            self.uniprot_id = "custom"

        self._thresh: int = int(thresh)
        if self.thresh not in [100, 90, 50]:
            raise ValueError(
                f"'thresh' must be 100, 90, or 50 but {self.thresh} is provided."
            )
        self.save_json: bool = save_json
        if local_download_dir is None:
            local_download_dir = os.getcwd()
        self._local_download_dir: str | os.PathLike | None = local_download_dir
        self._uniref_json_url = f"https://rest.uniprot.org/uniref/UniRef{self.thresh}_{self.uniprot_id}.json"
        self._uniref_json_file: str | os.PathLike | io.StringIO | None = None
        json_file = Path(
            self._local_download_dir, f"UniRef{self.thresh}_{self.uniprot_id}.json"
        )
        if json_file.exists():
            self.uniref_json_file = json_file
        self._uniref_json: str | None = None  # json is only a str in python
        self._get_uniref_json()

    @property
    def uniprot_id(self):
        return self._uniprot_id

    @uniprot_id.setter
    def uniprot_id(self, uniprot_id: str):
        self._uniprot_id = uniprot_id

    @property
    def thresh(self):
        return self._thresh

    @thresh.setter
    def thresh(self, thresh: int):
        if int(thresh) not in [100, 90, 50]:
            raise ValueError(
                f"'thresh' must be 100, 90, or 50 but {thresh} is provided."
            )
        self._thresh = int(thresh)

    @property
    def local_download_dir(self):
        return self._local_download_dir

    @local_download_dir.setter
    def local_download_dir(self, dir: str | os.PathLike):
        """Set the directory to save downloaded UniRef JSON files.

        Args:
            dir (str | os.PathLike): directory path str or Path.
        """
        self._local_download_dir = dir

    @property
    def uniref_json_url(self):
        return self._uniref_json_url

    @uniref_json_url.setter
    def uniref_json_url(self, url: str):
        """Set the UniRef JSON file URL if not the official REST one.

        Args:
            url (str): URL link.
        """
        self._uniref_json_url = url

    @property
    def uniref_json_file(self):
        return self._uniref_json_file

    @uniref_json_file.setter
    def uniref_json_file(self, path: str | os.PathLike | io.StringIO):
        """Set the UniRef JSON file path

        Args:
            path (str | os.PathLike| io.StringIO): file-like or path to the file.

        Raises:
            FileExistsError: if <path> is not in the file system.
        """
        if isinstance(path, os.PathLike) and not Path(path).exists():
            raise FileExistsError(f"Cannot find {path}.")
        self._uniref_json_file = path

    @property
    def uniref_json(self):
        return self._uniref_json

    @uniref_json.setter
    def uniref_json(self, content: str):
        """Set the UniRef JSON by json content (str repr in python).

        Args:
            content (str): JSON as a python str.

        Raises:
            AttributeError: if it is already set.
        """
        if self.uniref_json is None:
            self._uniref_json = content
        else:
            raise AttributeError("category_lines already set.")

    def _get_uniref_json(self):
        """Get json content"""
        if self.uniref_json_file is None:
            try:
                with urllib.request.urlopen(self.uniref_json_url) as response:
                    raw_data = response.read()
                json_content = raw_data.decode("utf-8")
                json_file: io.StringIO | os.PathLike = io.StringIO(json_content)
                if self.save_json:
                    json_file = Path(
                        self.local_download_dir,
                        f"UniRef{self.thresh}_{self.uniprot_id}.json",
                    )
                    with open(json_file, "w", encoding="utf-8") as j_file:
                        j_file.write(json_content)

                self.uniref_json_file = json_file
            except urllib.error.HTTPError:
                raise ValueError(f"Cannot download from url {self.uniref_json_url}.")

        if not isinstance(self.uniref_json_file, io.StringIO):
            j_file = open(self.uniref_json_file, "r", encoding="utf-8")
        else:
            j_file = self.uniref_json_file

        self.uniref_json = json.load(j_file)

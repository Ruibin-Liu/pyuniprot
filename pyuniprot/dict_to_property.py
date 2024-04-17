from __future__ import annotations

import keyword
import warnings


def validify_name(name: str) -> tuple[bool, str]:
    """
    Checks if the given name is a valid Python property name.
    If not return a valid one as well.

    Args:
        name (str, required): dictioanry key as str.

    Returns:
        (whether it is valid, validified one)
    """
    is_valid: bool = True
    valid_name: str = name
    if " " in name:
        is_valid = False
        valid_name = name.strip()

    if (not valid_name) or valid_name[0].isnumeric():
        is_valid = False
        valid_name = "_" + valid_name

    if " " in valid_name:
        is_valid = False
        valid_name = valid_name.replace(" ", "_")

    if any([c for c in valid_name.replace("_", "") if not c.isalnum()]):
        is_valid = False
        valid_name = "".join([c for c in valid_name if c.isalnum() or c == "_"])

    if keyword.iskeyword(valid_name):
        is_valid = False
        valid_name = "_" + valid_name

    if not is_valid:
        warnings.warn(
            f"key '{name}' is not a valid python variable. '{valid_name}' is used instead.",
            RuntimeWarning,
            stacklevel=2,
        )

    return is_valid, valid_name


class DictToProp:
    def __init__(self, data):
        self._data = data
        if not isinstance(self._data, dict):
            raise ValueError("Input is not a python dict")
        self._properties = {}
        self.create_properties()

    def create_properties(self):
        """Create properties based on the dictionary keys and values."""
        for key, value in self._data.items():
            key = validify_name(key)[1]
            if isinstance(value, dict):
                sub_instance = DictToProp(value)
                sub_instance.create_properties()
                self._properties[key] = sub_instance
            elif isinstance(value, list):
                self._properties[key] = DictToProp.parse_list(value)
            else:
                self._properties[key] = value

    @classmethod
    def parse_list(cls, lst: list) -> list:
        """Parse a list of dict recursively"""
        result: list = []
        for e in lst:
            if isinstance(e, dict):
                instance = DictToProp(e)
                instance.create_properties()
                result.append(instance)
            elif isinstance(e, list):
                result.append(DictToProp.parse_list(e))
            else:
                result.append(e)
        return result

    def __getattr__(self, key):
        """Override the attribute access to retrieve properties."""
        if key in self._properties:
            return self._properties[key]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

import os
import sys

import pytest

from pyuniprot.dict_to_property import DictToProp, validify_name

sys.path.append("..")
CFD = os.path.dirname(__file__)
CWD = os.getcwd()


def test_validify_name():
    """
    Test the validify_name function.
    """
    empty = ""
    warning_msg = "key '' is not a valid python variable. '_' is used instead."
    with pytest.warns(RuntimeWarning, match=warning_msg):
        assert validify_name(empty) == (False, "_"), "empty string not validified"

    py_kw = "de#f"
    warning_msg = "key 'de#f' is not a valid python variable. '_def' is used instead."
    with pytest.warns(RuntimeWarning, match=warning_msg):
        assert validify_name(py_kw) == (False, "_def"), "string 'de#f' not validified"

    space_in = "t est"
    warning_msg = "key 't est' is not a valid python variable. 't_est' is used instead."
    with pytest.warns(RuntimeWarning, match=warning_msg):
        assert validify_name(space_in) == (
            False,
            "t_est",
        ), "string 't est' not validified"

    wrong_start = "1a"
    warning_msg = "key '1a' is not a valid python variable. '_1a' is used instead."
    with pytest.warns(RuntimeWarning, match=warning_msg):
        assert validify_name(wrong_start) == (
            False,
            "_1a",
        ), "string '1a' not validified"

    correct = "test"
    assert validify_name(correct) == (True, "test"), "string 'test' not validified"


@pytest.mark.filterwarnings("ignore")
def test_DictToProp():
    """
    Test the DictToProp class.
    """
    test = {
        "normal": 0,
        "a_list": ["t", "e", "s", "t"],
        "a_dict": {
            "": "empty",
            "def": "python keyword",
            "t est": "space-in",
            "1a": "wrong-start",
            "_1234": "underscore-start",
        },
    }

    t = DictToProp(test)

    assert t.normal == 0, "normal propery failed"
    assert t.a_list == ["t", "e", "s", "t"], "list property failed"
    assert t.a_dict._ == "empty", "emtpy string key failed"
    assert t.a_dict._def == "python keyword", "python keyword key failed"
    assert t.a_dict.t_est == "space-in", "space-in key failed"
    assert t.a_dict._1a == "wrong-start", "wrong-start key failed"
    assert t.a_dict._1234 == "underscore-start", "underscore-start key failed"

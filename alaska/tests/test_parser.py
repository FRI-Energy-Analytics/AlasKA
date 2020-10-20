"""
Tests for Alaska's parser classes and functions
"""
from pathlib import Path
import pytest
from ..keyword_tree import Alias, search, make_tree, search_child, Node
from ..predict_from_model import make_prediction

test_case_1 = Path("alaska/data/testcase1.las")
test_case_2 = Path("alaska/data/testcase2.las")
test_case_3 = Path("alaska/data/testcase3.las")
test_case_4 = str(Path("alaska/data/testcase4.gz").resolve())
test_case_5 = Path("alaska/data/testcase5.las")
test_dir_1 = Path("alaska/data/")


def test_make_tree():
    """
    Test that it can build the keyword tree
    """
    root = make_tree()
    assert root.child[0].key == "caliper"


def test_search():
    """
    Test that it can search the keyword tree
    """
    result = search(make_tree(), "gr")
    assert result == "gamma ray"


def test_search_child():
    """
    Test that it can search nodes of the keyword tree
    """
    result = search_child(make_tree(), "density porosity")
    assert result == "density porosity"


def test_search_child_2():
    """
    Test that search of empty nodes returns None
    """
    empty_tree = Node(None)
    result = search_child(empty_tree, "density porosity")
    assert result is None


def test_search_child_3():
    """
    Test that search nodes for an non-existent description returns None
    """
    result = search_child(make_tree(), "not found")
    assert result is None


def test_parse():  # 1000080059
    """
    Test that Aliaser can parse las file
    """
    aliaser = Alias()
    result = aliaser.parse(test_case_1)
    assert result == ({"depth": ["DEPT"], "gamma ray": ["GR"]}, [])


def test_parse_2():
    """
    Test that Aliaser can parse las file with an empty mnemonic
    """
    aliaser = Alias()
    # import pdb; pdb.set_trace()
    result = aliaser.parse(test_case_5)
    assert result == ({"depth": ["DEPT"], "gamma ray": ["GR"]}, ["empty"])


def test_parse_directory_1():
    """
    Test that Aliaser can parse a directory of las files
    """
    expect_aliased = ["depth", "gamma ray", "density porosity", "caliper"]
    expect_not_aliased = ["empty", "qn"]

    aliaser = Alias()
    aliased, not_aliased = aliaser.parse_directory(test_dir_1)
    assert list(aliased) == expect_aliased
    assert not_aliased == expect_not_aliased


def test_parse_directory_2():
    """
    Test that Aliaser can parse a directory of las files and use the model
    parser
    """
    # aliaser = Alias()
    aliaser = Alias(dictionary=False, keyword_extractor=False, model=True)
    aliased, not_aliased = aliaser.parse_directory(test_dir_1)
    have1 = aliased.get("density porosity", "")
    have2 = aliased.get("medium conductivity", "")
    assert have1 == ["DPHI"]
    assert have2 == ["DEPT"]
    assert "empty" in not_aliased


def test_dictionary_parse_1():
    """
    Test that dictionary parser in Aliaser parses and returns correct labels
    """
    aliaser = Alias(keyword_extractor=False, model=False)
    result = aliaser.parse(test_case_1)
    assert result == ({"depth": ["DEPT"], "gamma ray": ["GR"]}, [])


def test_dictionary_parse_3():
    """
    Test that dictionary parser in Aliaser parses and returns correct labels
    with one item aliased and one item not aliased.
    """
    aliaser = Alias(keyword_extractor=False, model=False)
    aliased, not_aliased = aliaser.parse(test_case_3)

    assert len(aliased) == 1
    assert "density porosity" in aliased
    assert len(not_aliased) == 1
    assert "qn" in not_aliased


def test_keyword_parse_1():
    """
    Test that keyword parser in Aliaser parses and returns correct labels
    """
    aliaser = Alias(dictionary=False, model=False)
    aliased, not_aliased = aliaser.parse(test_case_1)

    assert len(aliased) == 1
    assert "gamma ray" in aliased
    assert len(not_aliased) == 1
    assert "dept" in not_aliased


def test_keyword_parse_2():  # 3725733C.las
    """
    Test that keyword parser in Aliaser parses and returns correct labels
    """
    aliaser = Alias(dictionary=False, model=False)
    result = aliaser.parse(test_case_2)
    assert result == ({"density porosity": ["DPHI"], "caliper": ["CALI"]}, [])


def test_dictionary_and_keyword_parse_1():
    """
    Test that keyword parser in Aliaser parses and returns correct labels
    """
    aliaser = Alias(model=False)
    aliased, not_aliased = aliaser.parse(test_case_1)

    assert aliased == {"depth": ["DEPT"], "gamma ray": ["GR"]}
    assert len(not_aliased) == 0


def test_dictionary_and_keyword_parse_3():
    """
    Test that keyword parser in Aliaser parses and returns correct labels
    """
    aliaser = Alias(model=False)
    aliased, not_aliased = aliaser.parse(test_case_3)

    assert len(aliased) == 1
    assert "density porosity" in aliased
    assert len(not_aliased) == 1
    assert "qn" in not_aliased


def test_model_parse():
    """
    Test that model in Aliaser parses and returns correct predictions
    """
    aliaser = Alias(dictionary=False, keyword_extractor=False, model=True)
    result = aliaser.parse(test_case_3)
    assert result == ({"near quality": ["QN"], "density porosity": ["DPHI"]}, [])


def test_make_prediction():
    """
    Test that make prediction works
    """
    result = make_prediction(test_case_4)
    assert result[0] == {"qn": "near quality"}
    assert result[1]["qn"] == pytest.approx(0.8421125945781427, rel=1e-4)

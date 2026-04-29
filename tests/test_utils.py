"""Tests for salesforce_py.utils."""

import pytest

from salesforce_py.utils import convert_to_18_char, get_object_type


class TestConvertTo18Char:
    def test_15_char_id_returns_18(self):
        result = convert_to_18_char("001000000000001")
        assert len(result) == 18

    def test_18_char_id_unchanged(self):
        sf_id = "001000000000001AAA"
        assert convert_to_18_char(sf_id) == sf_id

    def test_invalid_length_raises(self):
        with pytest.raises(ValueError, match="15 or 18"):
            convert_to_18_char("001")

    def test_known_conversion(self):
        # 15-char: 001D000000IqhSL  →  18-char: 001D000000IqhSLIAZ  (well-known example)
        assert convert_to_18_char("001D000000IqhSL") == "001D000000IqhSLIAZ"


class TestGetObjectType:
    def test_known_prefix(self):
        # Account prefix is 001
        result = get_object_type("001000000000001AAA")
        assert result["name"] == "Account"

    def test_15_char_id_accepted(self):
        result = get_object_type("001000000000001")
        assert result["name"] == "Account"

    def test_unknown_prefix_raises(self):
        with pytest.raises(ValueError, match="Unknown"):
            get_object_type("ZZZ000000000001")

    def test_invalid_length_raises(self):
        with pytest.raises(ValueError, match="15 or 18"):
            get_object_type("001")

    def test_knowledge_article_prefix(self):
        # kA0 should match kA# wildcard → KnowledgeArticle
        result = get_object_type("kA0000000000001AAA")
        assert result["name"] == "KnowledgeArticle"
        assert result["label"] == "Knowledge Article"

    def test_knowledge_article_version_prefix(self):
        # ka0 should match ka# wildcard → KnowledgeArticleVersion
        result = get_object_type("ka0000000000001AAA")
        assert result["name"] == "KnowledgeArticleVersion"
        assert result["label"] == "Knowledge Article Version"

    def test_knowledge_article_any_hash_char(self):
        # The # can be any character — test with a letter
        result = get_object_type("kAX000000000001AAA")
        assert result["name"] == "KnowledgeArticle"

"""Unit tests for scope utility functions"""
import pytest
from utils.scope import build_scope_match, _code_variants, prepend_match


@pytest.mark.unit
class TestCodeVariants:
    """Test code variant generation"""
    
    def test_code_variants_string(self):
        """Test string code variants"""
        result = _code_variants("123")
        assert "123" in result
        assert 123 in result
    
    def test_code_variants_string_with_zero(self):
        """Test string code starting with zero"""
        result = _code_variants("0123")
        assert "0123" in result
        assert 123 not in result  # Should not convert if starts with 0
    
    def test_code_variants_none(self):
        """Test None code"""
        result = _code_variants(None)
        assert result == []
    
    def test_code_variants_empty_string(self):
        """Test empty string code"""
        result = _code_variants("")
        assert result == []


@pytest.mark.unit
class TestBuildScopeMatch:
    """Test scope match building"""
    
    def test_no_scope(self):
        """Test with no scope parameters"""
        result = build_scope_match()
        assert result == {}
    
    def test_district_code_only(self):
        """Test with district code only"""
        result = build_scope_match(district_code="2725")
        assert "district_code" in result
        assert 2725 in result["district_code"]["$in"]
        assert "2725" in result["district_code"]["$in"]
    
    def test_district_name_only(self):
        """Test with district name only"""
        result = build_scope_match(district_name="PUNE")
        assert "district_name" in result
        assert result["district_name"] == "PUNE"
    
    def test_district_code_and_name(self):
        """Test with both district code and name"""
        result = build_scope_match(district_code="2725", district_name="PUNE")
        assert "$or" in result
        assert len(result["$or"]) == 2
    
    def test_block_code_only(self):
        """Test with block code only"""
        result = build_scope_match(block_code="123")
        assert "block_code" in result
    
    def test_udise_code_only(self):
        """Test with UDISE code only"""
        result = build_scope_match(udise_code="123456")
        assert "udise_code" in result
    
    def test_multiple_scopes(self):
        """Test with multiple scope levels"""
        result = build_scope_match(
            district_code="2725",
            block_code="123",
            udise_code="456"
        )
        assert "$and" in result
        assert len(result["$and"]) == 3
    
    def test_school_name(self):
        """Test with school name"""
        result = build_scope_match(school_name="Test School")
        assert "school_name" in result
        assert result["school_name"] == "Test School"
    
    def test_code_and_name_combination(self):
        """Test combination of code and name"""
        result = build_scope_match(
            district_code="2725",
            block_name="Test Block"
        )
        assert "$and" in result
        assert len(result["$and"]) == 2


@pytest.mark.unit
class TestPrependMatch:
    """Test prepend match function"""
    
    def test_prepend_with_match(self):
        """Test prepending match to pipeline"""
        pipeline = [{"$group": {"_id": "$district_code"}}]
        match = {"district_code": "2725"}
        result = prepend_match(pipeline, match)
        assert len(result) == 2
        assert result[0] == {"$match": match}
        assert result[1] == pipeline[0]
    
    def test_prepend_empty_match(self):
        """Test prepending empty match (should not add)"""
        pipeline = [{"$group": {"_id": "$district_code"}}]
        match = {}
        result = prepend_match(pipeline, match)
        assert result == pipeline
    
    def test_prepend_none_match(self):
        """Test prepending None match"""
        pipeline = [{"$group": {"_id": "$district_code"}}]
        result = prepend_match(pipeline, None)
        assert result == pipeline


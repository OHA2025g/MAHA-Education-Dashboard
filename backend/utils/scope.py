from typing import Any, Dict, Optional


def build_scope_match(
    district_code: Optional[str] = None,
    block_code: Optional[str] = None,
    udise_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a MongoDB match dict for the common drilldown scope:
    District -> Block -> School.

    Note: Collections are expected to store these fields as:
    - district_code
    - block_code
    - udise_code
    """
    match: Dict[str, Any] = {}
    if district_code:
        match["district_code"] = district_code
    if block_code:
        match["block_code"] = block_code
    if udise_code:
        match["udise_code"] = udise_code
    return match


def prepend_match(pipeline: list, match: Dict[str, Any]) -> list:
    """Prepend a $match stage when match is non-empty."""
    if not match:
        return pipeline
    return [{"$match": match}, *pipeline]



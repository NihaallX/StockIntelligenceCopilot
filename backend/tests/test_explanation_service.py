"""
Test Explanation Service
=========================

Tests for LLM explanation layer with strict constraint validation.
"""

import pytest
import asyncio
from app.core.llm.explanation_service import ExplanationService


@pytest.fixture
def mock_signal():
    """Mock VWAP signal"""
    return {
        "bias": "long",
        "confidence": 71,
        "method": "VWAP + Volume",
        "keyLevels": {
            "VWAP": 2850.0,
            "invalidation": 2810.0
        }
    }


@pytest.fixture
def mock_mcp_context():
    """Mock Market Context Protocol output"""
    return {
        "regime": "trending",
        "indexAlignment": "aligned",
        "volumeState": "expansion",
        "sessionTime": "early open"
    }


@pytest.mark.asyncio
async def test_fallback_explanation_always_works(mock_signal, mock_mcp_context):
    """Test that fallback explanation works when LLM is disabled"""
    service = ExplanationService(api_key="", enabled=False)
    
    result = await service.explain_vwap_signal(
        ticker="TEST.NS",
        signal=mock_signal,
        mcp_context=mock_mcp_context
    )
    
    assert result is not None
    assert result["fallback"] is True
    assert "explanation" in result
    assert "what_went_right" in result
    assert "what_could_go_wrong" in result
    assert "confidence_label" in result
    assert len(result["explanation"]) > 0


@pytest.mark.asyncio
async def test_fallback_explanation_structure(mock_signal):
    """Test fallback explanation has correct structure"""
    service = ExplanationService(api_key="", enabled=False)
    
    result = await service.explain_vwap_signal(
        ticker="TEST.NS",
        signal=mock_signal,
        mcp_context=None
    )
    
    # Check structure
    assert isinstance(result["explanation"], str)
    assert isinstance(result["what_went_right"], list)
    assert isinstance(result["what_could_go_wrong"], list)
    assert result["confidence_label"] in ["high", "medium", "low"]
    
    # Check content
    assert len(result["what_went_right"]) > 0
    assert len(result["what_could_go_wrong"]) > 0


def test_fallback_explanation_no_forbidden_language(mock_signal, mock_mcp_context):
    """Test that fallback explanation doesn't use forbidden speculative language"""
    service = ExplanationService(api_key="", enabled=False)
    
    result = asyncio.run(service.explain_vwap_signal(
        ticker="TEST.NS",
        signal=mock_signal,
        mcp_context=mock_mcp_context
    ))
    
    explanation = result["explanation"].lower()
    
    # Forbidden phrases
    forbidden = [
        "will go up",
        "will go down",
        "guaranteed",
        "certain to",
        "definitely will",
        "must buy",
        "must sell"
    ]
    
    for phrase in forbidden:
        assert phrase not in explanation, f"Forbidden phrase found: {phrase}"


def test_fallback_explanation_references_method(mock_signal):
    """Test that fallback explanation references the trading method"""
    service = ExplanationService(api_key="", enabled=False)
    
    result = asyncio.run(service.explain_vwap_signal(
        ticker="TEST.NS",
        signal=mock_signal
    ))
    
    explanation = result["explanation"].lower()
    method = mock_signal["method"].lower()
    
    # Should mention method or key terms
    assert any(term in explanation for term in ["vwap", "volume", method])


def test_fallback_explanation_confidence_mapping():
    """Test confidence score to label mapping"""
    service = ExplanationService(api_key="", enabled=False)
    
    test_cases = [
        (85, "high"),
        (70, "high"),
        (65, "medium"),
        (50, "medium"),
        (45, "low"),
        (30, "low")
    ]
    
    for confidence, expected_label in test_cases:
        signal = {"bias": "long", "confidence": confidence, "method": "VWAP + Volume"}
        result = asyncio.run(service.explain_vwap_signal(ticker="TEST.NS", signal=signal))
        
        assert result["confidence_label"] == expected_label, f"Confidence {confidence} should map to {expected_label}"


def test_prompt_building_includes_all_data(mock_signal, mock_mcp_context):
    """Test that prompt includes all provided data"""
    service = ExplanationService(api_key="test_key", enabled=True)
    
    prompt = service._build_prompt(
        ticker="RELIANCE.NS",
        signal=mock_signal,
        mcp_context=mock_mcp_context,
        price_data={"current": 2850.0, "vwap": 2840.0}
    )
    
    # Check all data is in prompt
    assert "RELIANCE.NS" in prompt
    assert str(mock_signal["confidence"]) in prompt
    assert mock_signal["bias"] in prompt
    assert mock_mcp_context["regime"] in prompt
    assert "2850" in prompt  # Current price


def test_system_message_contains_constraints():
    """Test that system message includes all constraint instructions"""
    service = ExplanationService(api_key="test_key", enabled=True)
    
    system_message = service.SYSTEM_MESSAGE.lower()
    
    # Must include constraint keywords
    required_terms = [
        "not generate",
        "not predict",
        "conditional",
        "provided",
        "may indicate",
        "confidence"
    ]
    
    for term in required_terms:
        assert term in system_message, f"System message missing constraint term: {term}"


@pytest.mark.asyncio
async def test_service_cleanup():
    """Test that service cleans up resources"""
    service = ExplanationService(api_key="test_key", enabled=True)
    
    # Should not raise
    await service.cleanup()
    
    # Disabled service cleanup should also work
    service_disabled = ExplanationService(api_key="", enabled=False)
    await service_disabled.cleanup()


def test_disabled_service_returns_fallback():
    """Test that disabled service always returns fallback"""
    service = ExplanationService(api_key="", enabled=False)
    
    result = asyncio.run(service.explain_vwap_signal(
        ticker="TEST.NS",
        signal={"bias": "long", "confidence": 60, "method": "VWAP + Volume"}
    ))
    
    assert result["fallback"] is True


@pytest.mark.skip(reason="Requires OpenRouter API key")
@pytest.mark.asyncio
async def test_live_llm_explanation():
    """
    Test live LLM explanation (requires OPENROUTER_API_KEY env var)
    
    To run: pytest tests/test_explanation_service.py -k test_live_llm_explanation -v
    Set OPENROUTER_API_KEY environment variable
    """
    import os
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY not set")
    
    service = ExplanationService(api_key=api_key, enabled=True)
    
    result = await service.explain_vwap_signal(
        ticker="RELIANCE.NS",
        signal={
            "bias": "long",
            "confidence": 71,
            "method": "VWAP + Volume",
            "keyLevels": {"VWAP": 2850, "invalidation": 2810}
        },
        mcp_context={
            "regime": "trending",
            "indexAlignment": "aligned",
            "volumeState": "expansion",
            "sessionTime": "early open"
        }
    )
    
    assert result is not None
    assert len(result["explanation"]) > 0
    assert result["fallback"] is False
    
    # Check for forbidden language
    explanation = result["explanation"].lower()
    assert "will go up" not in explanation
    assert "guaranteed" not in explanation
    
    await service.cleanup()

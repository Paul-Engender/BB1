import pytest
from unittest.mock import Mock, patch
import httpx

from llm_transport_gateway.providers.gemini import call_gemini, _safe_err
from llm_transport_gateway.errors import (
    GatewayAuthError,
    GatewayClientError,
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

# Mock configuration
MOCK_API_KEY = "test_api_key"
MOCK_MODEL = "gemini-test-model"
MOCK_PROMPT = "test prompt"
MOCK_TIMEOUT = 10.0


@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.__enter__.return_value = mock_client
        yield mock_client


def create_mock_response(
    status_code: int, json_body: dict | None, text: str | None = None
):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    if json_body is not None:
        mock_resp.json.return_value = json_body
    else:
        mock_resp.json.side_effect = ValueError("No JSON")
    mock_resp.text = text
    return httpx.HTTPStatusError(message="Error", request=Mock(), response=mock_resp)


# --- Test _safe_err function ---
def test_safe_err_client_error_with_json():
    exc = create_mock_response(400, {"error": {"message": "Invalid request"}})
    err = _safe_err(exc)
    assert isinstance(err, GatewayClientError)
    assert "Gemini API error: HTTP 400" == str(err)


def test_safe_err_auth_error():
    exc = create_mock_response(401, {"error": {"message": "Unauthorized"}})
    err = _safe_err(exc)
    assert isinstance(err, GatewayAuthError)
    assert "Gemini API error: HTTP 401" == str(err)


def test_safe_err_rate_limit_error():
    exc = create_mock_response(429, {"error": {"message": "Rate limit exceeded"}})
    err = _safe_err(exc)
    assert isinstance(err, GatewayRateLimitError)
    assert "Gemini API error: HTTP 429" == str(err)


def test_safe_err_upstream_error_with_json():
    exc = create_mock_response(500, {"error": {"message": "Internal server error"}})
    err = _safe_err(exc)
    assert isinstance(err, GatewayUpstreamError)
    assert "Gemini API error: HTTP 500" == str(err)


def test_safe_err_upstream_error_no_json():
    exc = create_mock_response(503, None, text="Service Unavailable")
    err = _safe_err(exc)
    assert isinstance(err, GatewayUpstreamError)
    assert "HTTP 503" in str(err)


# --- Test call_gemini function ---


def test_call_gemini_success(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Expected Output"}]}}]
    }
    mock_resp.raise_for_status = Mock()
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(
        prompt=MOCK_PROMPT,
        model=MOCK_MODEL,
        api_key=MOCK_API_KEY,
        timeout_s=MOCK_TIMEOUT,
    )
    assert result == "Expected Output"
    mock_httpx_client.post.assert_called_once()


def test_call_gemini_auth_error(mock_httpx_client):
    mock_resp = Mock(status_code=401)
    mock_resp.json.return_value = {"error": {"message": "Invalid API Key"}}
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Auth Error", request=Mock(), response=mock_resp
    )
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayAuthError, match="Gemini API error: HTTP 401"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_rate_limit_error(mock_httpx_client):
    mock_resp = Mock(status_code=429)
    mock_resp.json.return_value = {"error": {"message": "Rate limit exceeded"}}
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Rate Limit", request=Mock(), response=mock_resp
    )
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayRateLimitError, match="Gemini API error: HTTP 429"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_client_error(mock_httpx_client):
    mock_resp = Mock(status_code=400)
    mock_resp.json.return_value = {"error": {"message": "Bad Request"}}
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Bad Request", request=Mock(), response=mock_resp
    )
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayClientError, match="Gemini API error: HTTP 400"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_upstream_error(mock_httpx_client):
    mock_resp = Mock(status_code=500)
    mock_resp.json.return_value = {"error": {"message": "Internal Server Error"}}
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Server Error", request=Mock(), response=mock_resp
    )
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini API error: HTTP 500"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_timeout_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.ReadTimeout("Timeout")

    with pytest.raises(GatewayTimeoutError, match="Gemini timeout"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_network_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.RequestError(
        "Network error", request=httpx.Request("GET", "http://test.com")
    )

    with pytest.raises(GatewayUpstreamError, match="Gemini request error"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_invalid_json_response(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.side_effect = ValueError("Not JSON")
    mock_resp.raise_for_status = Mock()
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini returned non-JSON response"):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )


def test_call_gemini_empty_response_content(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": None}]}},
            {"content": {"parts": [{}]}},
            {"content": {}},
            {},
        ]
    }
    mock_resp.raise_for_status = Mock()
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(
        GatewayUpstreamError, match="Gemini returned no text in the first part."
    ):
        call_gemini(
            prompt=MOCK_PROMPT,
            model=MOCK_MODEL,
            api_key=MOCK_API_KEY,
            timeout_s=MOCK_TIMEOUT,
        )

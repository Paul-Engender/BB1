import pytest
from unittest.mock import Mock
import time

from llm_transport_gateway.retry import (
    RetryPolicy,
    run_with_retry,
    _sleep_s,
)  # Import _sleep_s directly
from llm_transport_gateway.errors import (
    GatewayTimeoutError,
    GatewayRateLimitError,
    GatewayUpstreamError,
    GatewayClientError,
)

MOCK_REQUEST_ID = "test-request-id"


def test_run_with_retry_success_first_attempt():
    # Test that a successful function call returns immediately
    mock_fn = Mock(return_value="success")
    policy = RetryPolicy(max_retries=3)
    result = run_with_retry(mock_fn, policy, MOCK_REQUEST_ID)
    assert result == "success"
    mock_fn.assert_called_once()


def test_run_with_retry_success_after_retries(mocker):  # Added mocker
    # Test that a function succeeds after a few retries
    mock_fn = Mock(
        side_effect=[
            GatewayTimeoutError("timeout"),
            GatewayUpstreamError("upstream"),
            "success",
        ]
    )
    policy = RetryPolicy(
        max_retries=3, backoff_base_s=0.01
    )  # Short backoff for testing
    mocker.patch("time.sleep")  # Mock sleep to avoid actual delays

    result = run_with_retry(mock_fn, policy, MOCK_REQUEST_ID)
    assert result == "success"
    assert mock_fn.call_count == 3
    assert time.sleep.called  # Ensure sleep was called


def test_run_with_retry_exceeds_max_retries(mocker):  # Added mocker
    # Test that a retryable error is re-raised after max_retries
    mock_fn = Mock(side_effect=GatewayTimeoutError("timeout"))
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch("time.sleep")

    with pytest.raises(GatewayTimeoutError):
        run_with_retry(mock_fn, policy, MOCK_REQUEST_ID)
    assert mock_fn.call_count == 3  # Initial call + 2 retries


def test_run_with_retry_non_retryable_error():
    # Test that a non-retryable error is raised immediately
    mock_fn = Mock(side_effect=GatewayClientError("bad request"))
    policy = RetryPolicy(max_retries=3)

    with pytest.raises(GatewayClientError):
        run_with_retry(mock_fn, policy, MOCK_REQUEST_ID)
    mock_fn.assert_called_once()  # Should not retry


def test_run_with_retry_other_exception_raised_immediately():
    # Test that an unexpected exception is raised immediately
    mock_fn = Mock(side_effect=ValueError("unexpected"))
    policy = RetryPolicy(max_retries=3)

    with pytest.raises(ValueError):
        run_with_retry(mock_fn, policy, MOCK_REQUEST_ID)
    mock_fn.assert_called_once()


def test_run_with_retry_multiple_retryable_errors(mocker):  # Added mocker
    # Test with a mix of retryable errors
    mock_fn = Mock(
        side_effect=[
            GatewayRateLimitError("rate limited"),
            GatewayTimeoutError("timeout"),
            "finally success",
        ]
    )
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch("time.sleep")

    result = run_with_retry(mock_fn, policy, MOCK_REQUEST_ID)
    assert result == "finally success"
    assert mock_fn.call_count == 3


def test_sleep_s_calculation(mocker):  # Added mocker
    # Test that _sleep_s calculates a reasonable backoff (no exact values due to jitter)
    policy = RetryPolicy(backoff_base_s=1.0, backoff_max_s=10.0)
    mocker.patch(
        "random.uniform", return_value=0
    )  # Remove jitter for predictable results

    # Attempt 0: base * 2^0 = 1.0, jitter 0, min(10.0, 1.0) = 1.0
    assert _sleep_s(policy, 0) == 1.0  # Corrected access

    # Attempt 1: base * 2^1 = 2.0, jitter 0, min(10.0, 2.0) = 2.0
    assert _sleep_s(policy, 1) == 2.0  # Corrected access

    # Attempt 2: base * 2^2 = 4.0, jitter 0, min(10.0, 4.0) = 4.0
    assert _sleep_s(policy, 2) == 4.0  # Corrected access

    # Attempt 3: base * 2^3 = 8.0, jitter 0, min(10.0, 8.0) = 8.0
    assert _sleep_s(policy, 3) == 8.0  # Corrected access

    # Attempt 4: base * 2^4 = 16.0, jitter 0, min(10.0, 16.0) = 10.0 (capped by backoff_max_s)
    assert _sleep_s(policy, 4) == 10.0  # Corrected access

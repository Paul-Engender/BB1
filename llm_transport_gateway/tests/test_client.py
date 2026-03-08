import pytest

from llm_transport_gateway.client import AIGatewayClient, CallOptions
from llm_transport_gateway.config import GatewayConfig
from llm_transport_gateway.errors import GatewayConfigError, GatewayAuthError


# Fixtures for common objects
@pytest.fixture
def mock_config():
    return GatewayConfig(
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        max_retries=1,
        backoff_base_s=1.0,
        backoff_max_s=20.0,
        gemini_api_key="TEST_GEMINI_KEY",
    )


@pytest.fixture
def client(mock_config):
    return AIGatewayClient(cfg=mock_config)


@pytest.fixture(autouse=True)
def mock_dependencies(mocker, mock_config):
    log_event_mock = mocker.patch("llm_transport_gateway.client.log_event")
    prompt_hash8_mock = mocker.patch(
        "llm_transport_gateway.client.prompt_hash8", return_value="TESTHASH"
    )

    # Ensure retry wrapper doesn't sleep; execute the function immediately.
    run_with_retry_mock = mocker.patch(
        "llm_transport_gateway.client.run_with_retry",
        side_effect=lambda fn, policy, request_id: fn(),
    )

    # Patch config load to use the fixture config
    load_config_mock = mocker.patch(
        "llm_transport_gateway.client.load_config", return_value=mock_config
    )

    # Patch provider boundary
    call_gemini_mock = mocker.patch(
        "llm_transport_gateway.client.call_gemini", return_value="MODEL_OUTPUT_OK"
    )
    call_offline_mock = mocker.patch(
        "llm_transport_gateway.client.call_offline", return_value="OFFLINE_OUTPUT_OK"
    )

    return {
        "log_event": log_event_mock,
        "prompt_hash8": prompt_hash8_mock,
        "run_with_retry": run_with_retry_mock,
        "load_config": load_config_mock,
        "call_gemini": call_gemini_mock,
        "call_offline": call_offline_mock,
    }


# --- Tests for Data Integrity and Privacy ---


def test_client_does_not_modify_prompt(client, mock_dependencies, mocker):
    original_prompt = "ORIGINAL_PROMPT"
    client.call(original_prompt)

    # Verify that call_gemini received the original prompt using call_args inspection
    call_args = mock_dependencies["call_gemini"].call_args
    args, kwargs = call_args

    assert kwargs["prompt"] == original_prompt  # prompt


def test_client_does_not_modify_output(client, mock_dependencies):
    out = client.call("any prompt")
    assert out == "MODEL_OUTPUT_OK"


def test_client_logs_prompt_hash_not_prompt_text(client, mock_dependencies, mocker):
    prompt = "Sensitive prompt content"
    output_text = "Sensitive output content from model"
    api_key = "SECRET_API_KEY_VALUE"

    # Temporarily override the return value of mock_call_gemini for this test
    mock_dependencies["call_gemini"].return_value = output_text

    # Temporarily override the gemini_api_key in the client's config for this test
    # Since config is frozen, we create a new client with a modified config
    original_config = client.cfg
    modified_config = GatewayConfig(
        **{**original_config.__dict__, "gemini_api_key": api_key}
    )
    client.cfg = modified_config  # Reassign cfg to the new modified config

    client.call(prompt)

    # Check log_event calls for 'prompt_hash8'
    mock_dependencies["log_event"].assert_any_call(
        "llm_transport_gateway.call.start",
        request_id=mocker.ANY,
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        prompt_hash8="TESTHASH",
    )
    mock_dependencies["log_event"].assert_any_call(
        "llm_transport_gateway.call.ok",
        request_id=mocker.ANY,
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY,  # Use mocker.ANY for dynamic values
        prompt_hash8="TESTHASH",
    )
    # Ensure no calls directly include the original prompt text, output text, or API key
    for call_args in mock_dependencies["log_event"].call_args_list:
        _args, kwargs = call_args
        # Check kwargs for sensitive data
        for k, v in kwargs.items():
            assert prompt not in str(v)
            assert output_text not in str(v)
            assert api_key not in str(v)
        # In this logging setup, sensitive data would primarily be in kwargs.
        # If any positional arguments could contain sensitive data, they would need checking too.


# --- Tests for core client behavior ---


def test_client_initializes_with_provided_config():
    custom_config = GatewayConfig(
        provider="offline",
        model="test-offline",
        timeout_s=5.0,
        max_retries=0,
        backoff_base_s=0.0,
        backoff_max_s=0.0,
        gemini_api_key=None,
    )
    client = AIGatewayClient(cfg=custom_config)
    assert client.cfg is custom_config


def test_client_loads_config_if_not_provided(mocker, mock_dependencies):
    # Ensure load_config is mocked out and returns a known config
    test_config = GatewayConfig(
        provider="default",
        model="default",
        timeout_s=1.0,
        max_retries=0,
        backoff_base_s=0.0,
        backoff_max_s=0.0,
        gemini_api_key=None,
    )
    mock_dependencies[
        "load_config"
    ].return_value = test_config  # Set return value for the mock

    # Create client without passing config, so it calls load_config
    client = AIGatewayClient()
    mock_dependencies["load_config"].assert_called_once()
    assert client.cfg.provider == "default"


def test_client_calls_gemini_provider_correctly(client, mock_dependencies, mock_config):
    original_prompt = "ORIGINAL_PROMPT"
    client.call(original_prompt)

    mock_dependencies["call_gemini"].assert_called_once()
    args, kwargs = mock_dependencies["call_gemini"].call_args

    # Validate prompt and critical config propagation
    assert kwargs["prompt"] == original_prompt
    assert kwargs["model"] == mock_config.model
    assert kwargs["api_key"] == mock_config.gemini_api_key
    assert kwargs["timeout_s"] == mock_config.timeout_s


def test_client_calls_offline_provider_correctly(mock_config, mock_dependencies):
    # Create a new client with a config that explicitly sets the provider to offline
    offline_config = GatewayConfig(**{**mock_config.__dict__, "provider": "offline"})
    client = AIGatewayClient(cfg=offline_config)
    client.call("test prompt")
    mock_dependencies["call_offline"].assert_called_once()
    mock_dependencies["call_gemini"].assert_not_called()


def test_client_handles_call_options_override(mock_config, mock_dependencies):
    # Ensure base config is gemini so we can override it
    base_config = GatewayConfig(**{**mock_config.__dict__, "provider": "gemini"})
    client = AIGatewayClient(cfg=base_config)

    options = CallOptions(provider="offline", timeout_s=5.0)
    client.call("test prompt", options=options)

    # Ensure offline was called with overridden timeout
    mock_dependencies["call_offline"].assert_called_once_with(
        prompt="test prompt",
        model="gemini-test-model",
        timeout_s=5.0,  # Model from config, not overridden
    )
    mock_dependencies["call_gemini"].assert_not_called()


def test_client_raises_value_error_for_empty_prompt(client):
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("   ")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call(None)  # type: ignore


def test_client_raises_gateway_config_error_for_missing_gemini_key(
    mocker, mock_dependencies, mock_config
):
    # Create a new config with missing API key
    mock_config_no_key = GatewayConfig(
        **{**mock_config.__dict__, "gemini_api_key": None}
    )
    mock_dependencies[
        "load_config"
    ].return_value = mock_config_no_key  # Ensure this is the config loaded

    client = AIGatewayClient()  # Client will load the mocked config

    with pytest.raises(GatewayConfigError, match="Missing GEMINI_API_KEY"):
        client.call("test prompt")


def test_client_raises_gateway_config_error_for_unknown_provider(
    mocker, mock_dependencies, mock_config
):
    # Create a new config with an unknown provider and a valid gemini key to reach the "unknown provider" check
    mock_config_unknown_provider = GatewayConfig(
        **{
            **mock_config.__dict__,
            "provider": "unknown",
            "gemini_api_key": "VALID_KEY_FOR_TEST",  # Ensure API key is present so it doesn't fail on missing key first
        }
    )
    mock_dependencies[
        "load_config"
    ].return_value = mock_config_unknown_provider  # Ensure this is the config loaded

    client = AIGatewayClient()  # Client will load the mocked config

    with pytest.raises(GatewayConfigError, match="Unknown provider: unknown"):
        client.call("test prompt")


def test_client_logs_failure_on_exception(client, mock_dependencies, mocker):
    mock_dependencies["call_gemini"].side_effect = GatewayAuthError("auth fail")

    with pytest.raises(GatewayAuthError):
        client.call("test prompt")

    mock_dependencies["log_event"].assert_called_with(
        "llm_transport_gateway.call.fail",
        request_id=mocker.ANY,
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY,
        prompt_hash8="TESTHASH",
        error_type="GatewayAuthError",
    )

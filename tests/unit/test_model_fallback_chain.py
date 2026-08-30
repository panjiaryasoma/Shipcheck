from app.services.live_rules import _is_retryable_model_error, _model_chain


def test_model_chain_preserves_primary_first() -> None:
    models = _model_chain()

    assert models[0] == "gemini-3.7-flash"
    assert "gemini-3.6-flash" in models
    assert "gemini-3.5-flash" in models
    assert len(models) == len(set(models))


def test_resource_exhausted_wrapper_is_retryable() -> None:
    class ResourceExhaustedError(RuntimeError):
        pass

    exc = ResourceExhaustedError("429 RESOURCE_EXHAUSTED")

    assert _is_retryable_model_error(exc) is True


def test_unrelated_application_error_is_not_retryable() -> None:
    assert _is_retryable_model_error(ValueError("invalid schema")) is False

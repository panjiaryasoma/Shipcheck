from app.services.live_rules import _model_chain


def test_model_chain_preserves_primary_first() -> None:
    models = _model_chain()

    assert models[0] == "gemini-3.7-flash"
    assert "gemini-3.6-flash" in models
    assert "gemini-3.5-flash" in models
    assert len(models) == len(set(models))

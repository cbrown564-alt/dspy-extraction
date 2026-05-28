import dspy

from clinical_extraction.experiments.runner import (
    collect_lm_token_usage,
    parse_ollama_ps_output,
    capture_local_model_residency,
)


def test_collect_lm_token_usage_aggregates_prompt_completion_and_total_tokens():
    primary = dspy.LM(model="openai/gpt-4.1-mini", api_key="test-key")
    reflection = dspy.LM(model="openai/gpt-4.1-mini", api_key="test-key")
    primary.history = [
        {"usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14}},
        {"usage": {"input_tokens": 8, "output_tokens": 3}},
    ]
    reflection.history = [
        {"usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7}},
    ]

    usage = collect_lm_token_usage([primary, reflection])

    assert usage == {
        "history_entries": 3,
        "prompt_tokens": 23,
        "completion_tokens": 9,
        "total_tokens": 32,
    }


def test_collect_lm_token_usage_returns_none_when_no_usage_is_available():
    lm = dspy.LM(model="openai/gpt-4.1-mini", api_key="test-key")
    lm.history = [{"usage": {}}, {"other": "ignored"}]

    assert collect_lm_token_usage([lm]) is None


def test_parse_ollama_ps_output_extracts_processor_and_context_for_target_model():
    output = """
NAME           ID              SIZE     PROCESSOR          CONTEXT    UNTIL
qwen3.6:35b    07d35212591f    26 GB    72%/28% CPU/GPU    4096       29 minutes from now
qwen3.5:9b     abcdef123456    8.1 GB   100% GPU           262144     5 minutes from now
""".strip()

    assert parse_ollama_ps_output(output, "qwen3.6:35b") == "72%/28% CPU/GPU (context=4096)"


def test_capture_local_model_residency_returns_unavailable_when_ollama_ps_fails(tmp_path):
    def runner(*args, **kwargs):
        raise OSError("ollama not found")

    residency = capture_local_model_residency("ollama", "qwen3.6:35b", runner=runner)

    assert residency == "unavailable"

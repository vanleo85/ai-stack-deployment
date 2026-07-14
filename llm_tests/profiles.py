"""Load test profile definitions.

Each profile defines a workload shape: prompt size, max output tokens,
system prompt, and task weight for Locust scheduling.
"""

from typing import Any, Dict

PROFILES: Dict[str, Dict[str, Any]] = {
    "smoke": {
        "prompt_chars": 200,
        "max_tokens": 64,
        "system": "You are a concise assistant. Reply briefly and accurately.",
    },
    "short_qa": {
        "prompt_chars": 600,
        "max_tokens": 128,
        "system": "You answer practical user questions with short, direct responses.",
    },
    "chat_balanced": {
        "prompt_chars": 1800,
        "max_tokens": 256,
        "system": "You are a helpful assistant for general multi-turn conversations.",
    },
    "rag_context": {
        "prompt_chars": 6000,
        "max_tokens": 192,
        "system": "Answer only from the provided context and be precise.",
    },
    "long_context": {
        "prompt_chars": 16000,
        "max_tokens": 256,
        "system": "You summarize and reason over long context windows.",
    },
    "long_generation": {
        "prompt_chars": 1200,
        "max_tokens": 1024,
        "system": "You write detailed structured answers with clear sections.",
    },
}

# Task weights for Locust @task decorator — higher = more frequent
TASK_WEIGHTS: Dict[str, int] = {
    "smoke": 1,
    "short_qa": 3,
    "chat_balanced": 4,
    "rag_context": 2,
    "long_context": 1,
    "long_generation": 1,
}

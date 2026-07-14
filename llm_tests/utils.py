"""Prompt generation and payload building utilities."""

import json
import random
import string
from typing import Any, Dict, List

from llm_tests.config import (
    VLLM_MODEL,
    VLLM_SEED,
    VLLM_TEMPERATURE,
    VLLM_TOP_K,
)
from llm_tests.profiles import PROFILES

# --- Prompt templates per category (3-5 each) ---

SHORT_QA_TEMPLATES = [
    "What is the capital of France?",
    "Explain quantum computing in one sentence.",
    "What are the main differences between Python and JavaScript?",
    "How does HTTPS encryption work?",
    "What is the time complexity of binary search?",
]

CHAT_TEMPLATES = [
    "I'm planning a trip to Japan next month. Can you help me create a 7-day itinerary focusing on cultural experiences, local food, and off-the-beaten-path destinations?",
    "I'm learning Python and struggling with decorators. Can you explain them step by step with practical examples that a beginner would understand?",
    "My company is migrating from a monolith to microservices. What are the key challenges we should anticipate and how can we mitigate them?",
    "I need to prepare a presentation about climate change for my university class. Help me outline the key points with supporting data.",
    "Can you help me write a professional email to my manager requesting a promotion? I've been at the company for 3 years and led two successful projects.",
]

RAG_TEMPLATES = [
    "Based on the following technical documentation, explain how to configure the authentication module:\n\n{context}\n\nSummarize the key configuration steps and any prerequisites.",
    "Given the following code review comments, identify the main issues and suggest fixes:\n\n{context}\n\nPrioritize the issues by severity.",
    "Using the provided API specification, write a Python function that calls the endpoint and handles errors:\n\n{context}\n\nInclude proper error handling and logging.",
    "Based on the following incident report, identify the root cause and recommend preventive measures:\n\n{context}\n\nStructure your response with Root Cause, Impact, and Recommendations sections.",
]

LONG_CONTEXT_TEMPLATES = [
    "I'm providing you with a lengthy technical document. Please:\n1. Summarize the main points in 3-5 bullet points\n2. Identify any contradictions or gaps\n3. Suggest improvements\n\nDocument:\n\n{context}",
    "Analyze the following codebase documentation and provide:\n1. Architecture overview\n2. Potential security concerns\n3. Performance optimization opportunities\n\nDocumentation:\n\n{context}",
    "Review the following meeting transcript and extract:\n1. Key decisions made\n2. Action items with owners\n3. Open questions that need follow-up\n\nTranscript:\n\n{context}",
]

LONG_GEN_TEMPLATES = [
    "Write a comprehensive guide on setting up a CI/CD pipeline for a Python web application. Cover: version control strategy, automated testing, deployment stages, monitoring, and rollback procedures.",
    "Create a detailed technical design document for a real-time chat application. Include: system architecture, database schema, API design, scalability considerations, and security measures.",
    "Write a thorough comparison of PostgreSQL vs MongoDB for a social media application. Cover: data modeling, query performance, scalability, consistency, and operational complexity.",
]

_TEMPLATES_BY_PROFILE = {
    "short_qa": SHORT_QA_TEMPLATES,
    "chat_balanced": CHAT_TEMPLATES,
    "rag_context": RAG_TEMPLATES,
    "long_context": LONG_CONTEXT_TEMPLATES,
    "long_generation": LONG_GEN_TEMPLATES,
}


def _get_seed() -> int | None:
    """Return deterministic seed if VLLM_SEED is set."""
    if VLLM_SEED:
        return int(VLLM_SEED)
    return None


def rand_text(length: int) -> str:
    """Generate random text of given character length (fallback)."""
    rng = random.Random(_get_seed())
    alphabet = string.ascii_letters + string.digits + "     ,.-:;\n"
    return "".join(rng.choices(alphabet, k=length))


def _fill_template(template: str, target_chars: int) -> str:
    """Expand a template to target_chars by repeating/filling context placeholders."""
    if "{context}" in template:
        # Fill context placeholder with repeated text to reach target size
        base = template.replace("{context}", "")
        filler_chars = max(0, target_chars - len(base))
        filler = rand_text(filler_chars)
        return template.replace("{context}", filler)
    elif len(template) < target_chars:
        # Pad short templates with additional random text
        padding = rand_text(target_chars - len(template))
        return template + "\n\n" + padding
    else:
        return template[:target_chars]


def random_prompt(profile_name: str) -> str:
    """Return a realistic prompt from the template pool for the given profile.

    For 'smoke' profile, falls back to rand_text() since it's just a quick check.
    """
    profile = PROFILES[profile_name]
    target_chars = int(profile["prompt_chars"])

    if profile_name == "smoke":
        return rand_text(target_chars)

    templates = _TEMPLATES_BY_PROFILE.get(profile_name)
    if not templates:
        return rand_text(target_chars)

    rng = random.Random(_get_seed())
    template = rng.choice(templates)
    return _fill_template(template, target_chars)


def build_messages(profile_name: str) -> List[Dict[str, str]]:
    """Build chat messages array for the given profile."""
    profile = PROFILES[profile_name]
    return [
        {"role": "system", "content": str(profile["system"])},
        {"role": "user", "content": random_prompt(profile_name)},
    ]


def build_payload(profile_name: str) -> Dict[str, Any]:
    """Build complete API request payload for the given profile."""
    profile = PROFILES[profile_name]
    return {
        "model": VLLM_MODEL,
        "messages": build_messages(profile_name),
        "max_tokens": int(profile["max_tokens"]),
        "temperature": VLLM_TEMPERATURE,
        "stream": False,
        "extra_body": {
            "top_k": VLLM_TOP_K,
        },
    }

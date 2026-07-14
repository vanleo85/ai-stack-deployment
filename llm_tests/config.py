"""Environment-based configuration for LLM load tests."""

import os

VLLM_HOST = os.getenv("VLLM_HOST", "http://localhost:8000")
VLLM_BASE_PATH = os.getenv("VLLM_BASE_PATH", "/v1/chat/completions")
VLLM_MODEL = os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "token-abc123")
VLLM_REQUEST_TIMEOUT = float(os.getenv("VLLM_REQUEST_TIMEOUT", "300"))
VLLM_TOP_K = int(os.getenv("VLLM_TOP_K", "40"))
VLLM_TEMPERATURE = float(os.getenv("VLLM_TEMPERATURE", "0.0"))
VLLM_SEED = os.getenv("VLLM_SEED", "")

# LLM Load Testing Package — Design Spec

**Date:** 2026-07-14
**Status:** Approved
**Scope:** Locust-based load testing for vLLM inference server

## Goal

Create an isolated, modular load testing package for the deployed vLLM inference server. The package must be self-contained — copy it to another project and it works.

## Context

- `docker-compose.yml` deploys vLLM with Qwen model on GPU
- Existing `llm_tests/locustfile.py` has 6 load profiles but is monolithic
- No documentation, no `requirements.txt`, no run scripts

## Structure

```
llm_tests/
├── __init__.py
├── locustfile.py          # locust entrypoint
├── profiles.py            # load profile definitions
├── utils.py               # prompt generation, payload building
├── config.py              # env-based configuration
├── requirements.txt       # locust + dependencies
├── .env.test.example      # template env vars for tests
├── README.md              # full documentation
└── run.sh                 # quick-start script
```

Plus root `README.md` with quick-start section linking to `llm_tests/README.md`.

## Modules

### `config.py`

Single source of truth for all env-based configuration:

| Variable | Default | Description |
|---|---|---|
| `VLLM_BASE_PATH` | `/v1/chat/completions` | API endpoint path |
| `VLLM_MODEL` | `Qwen/Qwen2.5-1.5B-Instruct` | Model name |
| `VLLM_API_KEY` | `token-abc123` | Bearer token |
| `VLLM_REQUEST_TIMEOUT` | `300` | Request timeout in seconds |
| `VLLM_TOP_K` | `40` | Top-K sampling parameter |
| `VLLM_TEMPERATURE` | `0.0` | Sampling temperature |

### `profiles.py`

Dictionary `PROFILES` with 6 load profiles:

| Profile | Prompt chars | Max tokens | Weight | System prompt focus |
|---|---|---|---|---|
| `smoke` | 200 | 64 | 1 | Concise assistant |
| `short_qa` | 600 | 128 | 3 | Short direct answers |
| `chat_balanced` | 1800 | 256 | 4 | General conversation |
| `rag_context` | 6000 | 192 | 2 | Context-based answers |
| `long_context` | 16000 | 256 | 1 | Long context reasoning |
| `long_generation` | 1200 | 1024 | 1 | Structured detailed answers |

Weights reflect realistic usage patterns (balanced chat is most common).

### `utils.py`

- `rand_text(length: int) -> str` — random text generation
- `build_messages(profile_name: str) -> List[Dict]` — chat messages assembly
- `build_payload(profile_name: str) Dict` — full API payload

### `locustfile.py`

- Class `VllmUser(HttpUser)` with `wait_time = between(0.1, 1.0)`
- One `@task` method per profile, decorated with `@tag(profile_name)`
- `run_profile()` handles request, validates response (status 200, valid JSON, has `choices`)
- Event listeners for test start/stop logging

### `requirements.txt`

```
locust>=2.20.0
```

### `run.sh`

Bash script with usage examples:
- Default UI mode: `locust -f locustfile.py --host http://localhost:8000`
- Tag-filtered: `--tags smoke`
- Headless: `--users 10 --spawn-rate 2 --run-time 60s --headless`

### `.env.test.example`

Template with all `VLLM_*` variables and comments.

## Documentation

### `llm_tests/README.md`

Full documentation:
1. Package description
2. Installation (`pip install -r requirements.txt`)
3. Profile descriptions table
4. Environment variables table
5. Run commands (UI, headless, tags)
6. Results interpretation (RPS, latency, percentiles)

### Root `README.md`

Quick-start section:
1. Deploy vLLM: `docker compose up -d`
2. Wait for health check
3. Run tests: `cd llm_tests && ./run.sh`
4. Link to `llm_tests/README.md` for details

## Out of Scope

- Streaming (SSE) testing
- Custom TPS metrics
- CI/CD integration
- Functional/smoke tests (pytest)
- Dockerized Locust

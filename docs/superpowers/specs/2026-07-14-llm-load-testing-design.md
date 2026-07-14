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
| `VLLM_HOST` | `http://localhost:8000` | vLLM server base URL |
| `VLLM_BASE_PATH` | `/v1/chat/completions` | API endpoint path |
| `VLLM_MODEL` | `Qwen/Qwen2.5-1.5B-Instruct` | Model name |
| `VLLM_API_KEY` | `token-abc123` | Bearer token |
| `VLLM_REQUEST_TIMEOUT` | `300` | Request timeout in seconds |
| `VLLM_TOP_K` | `40` | Top-K sampling parameter (via `extra_body`) |
| `VLLM_TEMPERATURE` | `0.0` | Sampling temperature |
| `VLLM_SEED` | `None` | Random seed for reproducible prompts (empty = random) |

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

- `rand_text(length: int) -> str` — random text generation (fallback)
- `random_prompt(profile_name: str) -> str` — realistic prompt from template pool, scaled to profile's `prompt_chars`
- `build_messages(profile_name: str) -> List[Dict]` — chat messages assembly using `random_prompt()`
- `build_payload(profile_name: str) -> Dict` — full API payload

Prompts are generated from curated templates per profile category (short QA, chat, RAG context, long context) rather than random characters. This produces realistic tokenization behavior. 3-5 templates per category, randomly selected at runtime. `rand_text()` retained as fallback for stress-testing edge cases.

### `locustfile.py`

- Class `VllmUser(HttpUser)` with `wait_time = between(1.0, 3.0)` — realistic user pacing
- Auth: `Authorization: Bearer {VLLM_API_KEY}` header set in `on_start()`
- One `@task` method per profile, decorated with `@tag(profile_name)`
- `run_profile()` validates: HTTP 200, valid JSON, non-empty `choices` array, presence of `usage` object (`prompt_tokens`, `completion_tokens`, `total_tokens`)
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

## Review Notes (Perplexity Reason, 2026-07-14)

### Round 1 — Applied:
- `wait_time` changed from `between(0.1, 1.0)` to `between(1.0, 3.0)` — more realistic pacing
- Added `VLLM_HOST` env var for base URL configuration
- Replaced `rand_text()` with prompt templates for realistic tokenization

### Round 1 — Rejected:
- Multiple User classes per profile — overkill, tags are sufficient
- Retry/backoff strategies — load testing, not chaos engineering
- Batching/observability env vars — server-side config
- Per-profile wait_time — uniform range is sufficient

### Round 2 — Applied:
- Clarified auth header format: `Authorization: Bearer <key>`
- Enhanced response validation: non-empty `choices` + `usage` object
- Added `VLLM_SEED` env var for reproducible prompts
- Documented template count: 3-5 per category
- Clarified `top_k` via `extra_body` (vLLM API specifics)

### Round 2 — Rejected:
- Two-tier validation (soft/strict) — overkill
- Observability hooks — out of scope (standard Locust metrics)
- Rate limiting/backoff — out of scope
- CI/CD mockable mode — out of scope
- Data privacy — test data only
- Ramp-up phase — `--spawn-rate` handles this

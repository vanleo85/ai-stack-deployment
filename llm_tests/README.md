# LLM Load Tests

Locust-based load testing package for vLLM inference servers.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy the env template and adjust values:

```bash
cp .env.test.example .env.test
```

| Variable | Default | Description |
|---|---|---|
| `VLLM_HOST` | `http://localhost:8000` | vLLM server base URL |
| `VLLM_BASE_PATH` | `/v1/chat/completions` | API endpoint path |
| `VLLM_MODEL` | `Qwen/Qwen2.5-1.5B-Instruct` | Model name |
| `VLLM_API_KEY` | `token-abc123` | Bearer token |
| `VLLM_REQUEST_TIMEOUT` | `300` | Request timeout (seconds) |
| `VLLM_TOP_K` | `40` | Top-K sampling |
| `VLLM_TEMPERATURE` | `0.0` | Sampling temperature |
| `VLLM_SEED` | *(empty)* | Seed for reproducible prompts |

## Load Profiles

| Profile | Prompt | Max tokens | Weight | Description |
|---|---|---|---|---|
| `smoke` | 200 chars | 64 | 1 | Quick sanity check |
| `short_qa` | 600 chars | 128 | 3 | Short Q&A |
| `chat_balanced` | 1800 chars | 256 | 4 | General conversation |
| `rag_context` | 6000 chars | 192 | 2 | RAG with context |
| `long_context` | 16000 chars | 256 | 1 | Long context reasoning |
| `long_generation` | 1200 chars | 1024 | 1 | Detailed generation |

Weight = relative frequency during test (higher = more requests).

## Running

### Web UI

```bash
./run.sh
# or
locust -f locustfile.py --host http://localhost:8000
```

Open http://localhost:8089, set number of users and spawn rate.

### Headless

```bash
./run.sh headless --users 10 --spawn-rate 2 --run-time 60s
```

### Smoke test only

```bash
./run.sh smoke --users 5 --run-time 30s
```

### Specific profiles (tags)

```bash
locust -f locustfile.py --host http://localhost:8000 --tags short_qa chat_balanced --headless
```

## Results

Locust outputs standard metrics:

- **RPS** — requests per second
- **Latency** — p50, p95, p99 response times (ms)
- **Failure rate** — percentage of failed requests

For CSV export:

```bash
locust -f locustfile.py --host http://localhost:8000 --headless --csv=results
```

This creates `results_stats.csv`, `results_failures.csv`, `results_stats_history.csv`.

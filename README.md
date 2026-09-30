# AI Stack Deployment

Deployment and testing infrastructure for LLM inference servers.

## Quick Start

### 1. Deploy vLLM

```bash
docker compose up -d
```

Wait for health check to pass (default: 180s start period).

### 2. GPU reranker (optional)

`reranker-gpu` is a GPU-accelerated twin of `reranker`: same TEI image family,
same model, same `POST /rerank` API — only the transport is faster. It shares the
host GPU with `vllm-qwen`, and a Compose GPU reservation grants *access* to the
device, not exclusive VRAM. Free the GPU first:

```bash
docker compose stop vllm-qwen
docker compose up -d reranker-gpu
curl http://localhost:6008/health
```

Smoke test (same payload shape as `build/test_models.md`):

```bash
curl http://localhost:6008/rerank \
  -H 'Content-Type: application/json' \
  -d '{"query": "что такое llama.cpp", "texts": ["llama.cpp — это C/C++ инференс LLM", "сегодня хорошая погода"], "top_n": 1}'
```

If you need both `vllm-qwen` and `reranker-gpu` at once, lower
`VLLM_GPU_MEMORY_UTILIZATION` (e.g. `0.85`) to leave VRAM for the reranker and
watch both services for OOM.

> **Image tag:** TEI GPU tags are architecture-specific — there is no
> `gpu-latest`. Set `RERANKER_GPU_IMAGE_TAG` to match your card (RTX 4090 →
> `89-<ver>`). The full GPU → tag table is in `.env.example`.

### 3. Run load tests

```bash
cd llm_tests
pip install -r requirements.txt
./run.sh
```

Open http://localhost:8089 for the Locust web UI.

See [llm_tests/README.md](llm_tests/README.md) for full documentation.

## Project Structure

```
├── docker-compose.yml      # vLLM deployment
├── .env.example            # Environment variables template
├── llm_tests/              # Load testing package
│   ├── locustfile.py       # Locust entrypoint
│   ├── profiles.py         # Load profiles
│   ├── utils.py            # Prompt generation
│   ├── config.py           # Env configuration
│   └── README.md           # Testing documentation
```

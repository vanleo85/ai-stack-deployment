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

Smoke test (`POST /rerank`, contract is `query` + `texts`):

```bash
curl http://localhost:6008/rerank \
  -H 'Content-Type: application/json' \
  -d '{"query": "что такое llama.cpp", "texts": ["llama.cpp — это C/C++ инференс LLM", "сегодня хорошая погода"]}'
```

Response is a plain JSON array sorted by descending `score`, all inputs returned:

```json
[{"index": 0, "score": 0.98}, {"index": 1, "score": 0.02}]
```

> **`top_n` is not implemented by TEI.** It appears in the older
> `build/test_models.md` examples, but the router ignores the field and returns
> every text — trim the list in the caller if you need top-N.

If you need both `vllm-qwen` and `reranker-gpu` at once, lower
`VLLM_GPU_MEMORY_UTILIZATION` (e.g. `0.85`) to leave VRAM for the reranker and
watch both services for OOM.

> **Image tag:** TEI GPU tags are architecture-specific — there is no
> `gpu-latest`. Set `RERANKER_GPU_IMAGE_TAG` to match your card (RTX 4090 →
> `89-<ver>`). The full GPU → tag table is in `.env.example`.

### 3. GPU embedding (optional)

`embedding-gpu` is the GPU twin of `embedding`: same TEI image family, same
model, same `POST /embed` API. The ops notes from the GPU reranker apply here
too — free the GPU first, and see the GPU → tag table in `.env.example`.

```bash
docker compose stop vllm-qwen
docker compose up -d embedding-gpu
curl http://localhost:6009/health
```

Smoke test (`POST /embed`, contract is `inputs`):

```bash
curl http://localhost:6009/embed \
  -H 'Content-Type: application/json' \
  -d '{"inputs": "что такое llama.cpp"}'
```

Response is `[[float x 1024]]`, L2-normalized (`normalize` defaults to `true`).
Pooling is read by TEI from the model's `1_Pooling/config.json` (CLS for
`bge-m3` — matching BAAI's own `sentence_pooling_method='cls'`), so no
`--pooling` flag is needed.

> **Long inputs are silently truncated.** TEI's `--auto-truncate` defaults to
> `true`, and `bge-m3` supports 8192 tokens — an over-long document is cut, not
> rejected. Chunk long documents client-side if full coverage matters. The same
> applies to the CPU `embedding` service.

> **Check quality against the CPU reference.** The GPU service runs `float16`
> (needed for Flash Attention) while the CPU one runs `float32`. Cosine
> similarity between `:6006` and `:6009` vectors for the same input should be
> ≈ 1.0 — if it drops noticeably, set `EMBEDDING_GPU_DTYPE=float32`.

Both GPU services fit on one card while `vllm-qwen` is off (~5 GB of 24 GB).

### 4. Run load tests

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

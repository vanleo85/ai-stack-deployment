# AI Stack Deployment

Deployment and testing infrastructure for LLM inference servers.

## Quick Start

### 1. Deploy vLLM

```bash
docker compose up -d
```

Wait for health check to pass (default: 180s start period).

### 2. Run load tests

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

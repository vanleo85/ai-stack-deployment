#!/usr/bin/env bash
# Quick-start script for LLM load tests
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load env if exists
if [ -f .env.test ]; then
    set -a
    source .env.test
    set +a
fi

HOST="${VLLM_HOST:-http://localhost:8000}"

usage() {
    cat <<EOF
Usage: $0 [command] [options]

Commands:
  ui          Start Locust web UI (default)
  headless    Run headless test
  smoke       Run smoke test only
  tags        List available tags

Options are passed directly to locust.

Examples:
  $0                                    # Web UI
  $0 headless --users 10 --run-time 60s # 10 users, 60 seconds
  $0 smoke --users 5 --run-time 30s     # Smoke test only
EOF
}

case "${1:-ui}" in
    ui)
        shift || true
        exec locust -f locustfile.py --host "$HOST" "$@"
        ;;
    headless)
        shift || true
        exec locust -f locustfile.py --host "$HOST" --headless "$@"
        ;;
    smoke)
        shift || true
        exec locust -f locustfile.py --host "$HOST" --tags smoke --headless "$@"
        ;;
    tags)
        echo "Available tags: smoke, short_qa, chat_balanced, rag_context, long_context, long_generation"
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Unknown command: $1"
        usage
        exit 1
        ;;
esac

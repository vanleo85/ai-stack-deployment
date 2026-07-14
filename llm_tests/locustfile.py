"""Locust load test entrypoint for vLLM inference server.

Usage:
    locust -f locustfile.py --host http://localhost:8000
    locust -f locustfile.py --host http://localhost:8000 --tags smoke
    locust -f locustfile.py --host http://localhost:8000 --users 10 --spawn-rate 2 --run-time 60s --headless
"""

from __future__ import annotations

import json

from locust import HttpUser, between, events, tag, task

from llm_tests.config import VLLM_API_KEY, VLLM_BASE_PATH, VLLM_HOST, VLLM_MODEL, VLLM_REQUEST_TIMEOUT
from llm_tests.profiles import TASK_WEIGHTS
from llm_tests.utils import build_payload


class VllmUser(HttpUser):
    wait_time = between(1.0, 3.0)

    def on_start(self):
        self.client.headers.update(
            {
                "Authorization": f"Bearer {VLLM_API_KEY}",
                "Content-Type": "application/json",
            }
        )

    def run_profile(self, profile_name: str):
        payload = build_payload(profile_name)
        request_name = f"chat:{profile_name}"
        with self.client.post(
            VLLM_BASE_PATH,
            data=json.dumps(payload),
            name=request_name,
            catch_response=True,
            timeout=VLLM_REQUEST_TIMEOUT,
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text[:400]}")
                return

            try:
                data = response.json()
            except Exception as exc:
                response.failure(f"Invalid JSON: {exc}")
                return

            if "choices" not in data or not data["choices"]:
                response.failure(f"Missing or empty choices: {str(data)[:400]}")
                return

            if "usage" not in data:
                response.failure(f"Missing usage in response: {str(data)[:400]}")
                return

            response.success()

    @tag("smoke")
    @task(TASK_WEIGHTS["smoke"])
    def profile_smoke(self):
        self.run_profile("smoke")

    @tag("short_qa")
    @task(TASK_WEIGHTS["short_qa"])
    def profile_short_qa(self):
        self.run_profile("short_qa")

    @tag("chat_balanced")
    @task(TASK_WEIGHTS["chat_balanced"])
    def profile_chat_balanced(self):
        self.run_profile("chat_balanced")

    @tag("rag_context")
    @task(TASK_WEIGHTS["rag_context"])
    def profile_rag_context(self):
        self.run_profile("rag_context")

    @tag("long_context")
    @task(TASK_WEIGHTS["long_context"])
    def profile_long_context(self):
        self.run_profile("long_context")

    @tag("long_generation")
    @task(TASK_WEIGHTS["long_generation"])
    def profile_long_generation(self):
        self.run_profile("long_generation")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(
        f"Starting load test: model={VLLM_MODEL}, "
        f"base_path={VLLM_BASE_PATH}"
    )
    print("Available tags: smoke, short_qa, chat_balanced, rag_context, long_context, long_generation")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test finished.")

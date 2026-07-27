#!/bin/sh
# Wrapper: adds optional flags based on environment variables
set -e

EXTRA_ARGS=""

if [ "${VLLM_ENFORCE_EAGER}" = "true" ]; then
  EXTRA_ARGS="${EXTRA_ARGS} --enforce-eager"
fi
if [ "${VLLM_ENABLE_CHUNKED_PREFILL}" = "true" ]; then
  EXTRA_ARGS="${EXTRA_ARGS} --enable-chunked-prefill"
fi
if [ "${VLLM_ENABLE_PREFIX_CACHING}" = "true" ]; then
  EXTRA_ARGS="${EXTRA_ARGS} --enable-prefix-caching"
fi

# Reasoning + Structured Output support for Qwen3 models
if [ "${VLLM_ENABLE_REASONING}" = "true" ]; then
  EXTRA_ARGS="${EXTRA_ARGS} --reasoning-parser qwen3"
  EXTRA_ARGS="${EXTRA_ARGS} --structured-outputs-config '{\"enable_in_reasoning\": true}'"
fi

exec vllm serve "$@" ${EXTRA_ARGS}

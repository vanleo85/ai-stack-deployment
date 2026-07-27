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

exec vllm serve "$@" ${EXTRA_ARGS}

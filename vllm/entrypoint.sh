#!/bin/sh
# Wrapper: adds --enforce-eager flag when VLLM_ENFORCE_EAGER=true
set -e

EXTRA_ARGS=""
if [ "${VLLM_ENFORCE_EAGER}" = "true" ]; then
  EXTRA_ARGS="--enforce-eager"
fi

exec vllm serve "$@" ${EXTRA_ARGS}

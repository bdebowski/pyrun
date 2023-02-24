#!/bin/bash

export PYRUNNER_NUM_WORKERS=4
export PYRUNNER_TIMEOUT_SEC=5
export PYRUNNER_MAXMEM_MB=512
export PYRUNNER_PORT=${1}

python server.py
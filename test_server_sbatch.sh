#!/bin/bash
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --time 0:05:00

PYRUNNER_SERVER_IP=${1}
PYRUNNER_SERVER_PORT=${2}

LOCALHOST=localhost
LOGIN_NODE=gra-login3

# Set up port forwarding to the server via the login node through any available port we can find
for ((i=0; i<10; ++i)); do
  LOCALPORT=$(shuf -i 1024-65535 -n 1)
  ssh $LOGIN_NODE -L $LOCALPORT:$PYRUNNER_SERVER_IP:$PYRUNNER_SERVER_PORT -N -f && break
done || { echo "Giving up forwarding port after $i attempts..."; exit 1; }

# Set environment variables for the python script
export PYRUNNER_SERVER_IP=$LOCALHOST
export PYRUNNER_SERVER_PORT=$LOCALPORT

# Activate Python environment
module load python/3.9
source venv/bin/activate
python tests/test_server.py

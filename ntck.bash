#!/bin/bash

set -ex -o pipefail

# Get the first active network interface for later.
INTERFACE=${INTERFACE:-$(ip -j link show | jq -r '.[] | select(.operstate == "UP") | .ifname' | head -n1)}
if [[ -z "$INTERFACE" ]]; then
    echo "couldn't find an interface which is UP"
    exit 1
fi
# Check that bpftrace can run.
bpftrace -e 'BEGIN { exit() }' >/dev/null

# Create a temporary directory for artifacts and outputs.
NTCK_DIR=${NTCK_DIR:-$(mktemp -d)}
gcc -o $NTCK_DIR/sendeth -O2 sendeth.c

# Check that a Python virtual env is active.
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "setting up temporary venv"
    python3 -m venv $NTCK_DIR/venv
    source $NTCK_DIR/venv/bin/activate
    pip install -r requirements.txt
fi

# Start collecting metrics.
bpftrace time_send_xmit.bt > $NTCK_DIR/comm_sendeth.trace &
BPFPID=$!
# Give bpftrace time to set up probes.
sleep 5

# Dump packets with a few processes concurrently.
echo "sending packets from concurrent processes"
$NTCK_DIR/sendeth $INTERFACE 1000 2000 &
$NTCK_DIR/sendeth $INTERFACE 1000 3000 &
$NTCK_DIR/sendeth $INTERFACE 1000 4000 &
$NTCK_DIR/sendeth $INTERFACE 1000 5000 &
$NTCK_DIR/sendeth $INTERFACE 1000 6000 &
# Wait to make sure they all get time to run,
# and to give any recording video time to be interesting.
sleep 5

# End the background job.
kill $BPFPID
wait -fn $BPFPID

# Convert the trace to a CSV of time deltas.
cat $NTCK_DIR/comm_sendeth.trace | python3 xmitdtoas.py > $NTCK_DIR/comm_sendeth.csv
# Plot the results.
python3 plot.py $NTCK_DIR/comm_sendeth.csv

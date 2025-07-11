#!/bin/bash

IPERF_SERVER_IP=$1
IPERF_LOG_FILE=$2

# Get source IP from uesimtun0
SRC_IP=$(ip addr show uesimtun0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

if [ -z "$SRC_IP" ]; then
    echo "Error: Could not find IP on interface uesimtun0"
    exit 2
fi

# Run iperf3
iperf3 -c "$IPERF_SERVER_IP" -u -t 40 -b 100M -B "$SRC_IP" -J > "$IPERF_LOG_FILE"

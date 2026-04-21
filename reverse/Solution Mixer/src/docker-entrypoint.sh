#!/bin/bash
set -e

# CTFd flag injection support
# CTFd typically injects flags via FLAG or CTFD_FLAG environment variable
# If provided, override the flag.txt file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /app/flag.txt
    echo "Flag injected from FLAG environment variable"
elif [ -n "$CTFD_FLAG" ]; then
    echo -n "$CTFD_FLAG" > /app/flag.txt
    echo "Flag injected from CTFD_FLAG environment variable"
else
    # For local testing, use the flag.txt that was copied during build
    if [ ! -f /app/flag.txt ]; then
        echo "ERROR: flag.txt not found and no FLAG/CTFD_FLAG environment variable set" >&2
        exit 1
    fi
    echo "Using flag.txt from build context"
fi

# Run the server
exec /app/SolutionMixerServer --host 0.0.0.0 --port 34512


#!/bin/bash
# Run batch generation in the background, writing progress to a log file.
# Usage: ./run_batch_background.sh [PRIORITY] [LIMIT]
# Example: ./run_batch_background.sh WEEK_1 20

PRIORITY="${1:-WEEK_1}"
LIMIT="${2:-}"

cd /home/z/my-project
mkdir -p logs

LOG="logs/batch-${PRIORITY}-$(date +%Y%m%d-%H%M%S).log"
echo "Starting batch: priority=$PRIORITY limit=$LIMIT" > "$LOG"
echo "Log: $LOG"

ARGS="--priority $PRIORITY"
if [ -n "$LIMIT" ]; then
  ARGS="$ARGS --limit $LIMIT"
fi

nohup python3 scripts/batch_generate.py $ARGS >> "$LOG" 2>&1 &
PID=$!
echo "Started PID $PID"
echo "$PID" > /tmp/batch-pid
echo "Tail the log with: tail -f $LOG"
echo "Check status with: ps -p $PID"

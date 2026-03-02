#!/bin/sh
set -eu

LOG_DIR="/Users/yufo/Documents/Projects_Local/flow2api/logs"
MAX_BYTES=$((10 * 1024 * 1024)) # 10MB
KEEP=10

rotate_one() {
  file="$1"
  [ -f "$file" ] || return 0

  size=$(stat -f%z "$file" 2>/dev/null || echo 0)
  if [ "$size" -lt "$MAX_BYTES" ]; then
    return 0
  fi

  # Shift old logs
  i=$KEEP
  while [ $i -gt 1 ]; do
    prev=$((i-1))
    if [ -f "$file.$prev.gz" ]; then
      mv "$file.$prev.gz" "$file.$i.gz"
    fi
    i=$prev
  done

  # Rotate current
  mv "$file" "$file.1"
  gzip -f "$file.1"
}

rotate_one "$LOG_DIR/flow2api.out.log"
rotate_one "$LOG_DIR/flow2api.err.log"

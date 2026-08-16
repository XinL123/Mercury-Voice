#!/bin/bash
# Launches MERCURY·VOICE with a tiny local server (with seek support)
# so the playlist can be analysed by the browser.
cd "$(dirname "$0")"
PID=$(lsof -ti tcp:8765)
if [ -n "$PID" ]; then kill $PID 2>/dev/null; sleep 0.3; fi
nohup python3 serve.py >/dev/null 2>&1 &
sleep 0.7
open "http://localhost:8765/reef-voice.html"
exit 0

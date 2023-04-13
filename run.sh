#!/bin/bash
"pip" install -r requirements.txt
"python" ./BackEnd/LogParserAPI.py & pids=$!
"python" -m http.server 8080 -d ./Frontend & pids+=" $!"

trap "kill $pids" SIGTERM SIGINT
wait $pids
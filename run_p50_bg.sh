#!/bin/bash
# Lance refetch_p50 en arrière-plan (déplacé dans scripts/archive/)
cd /home/claude/bestdateweather
python3 scripts/archive/refetch_p50.py >> /tmp/p50_log.txt 2>&1
echo "EXIT_CODE=$?" >> /tmp/p50_log.txt

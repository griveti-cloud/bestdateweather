#!/bin/bash
cd /home/claude/bestdateweather
python3 refetch_p50.py >> /tmp/p50_log.txt 2>&1
echo "EXIT_CODE=$?" >> /tmp/p50_log.txt

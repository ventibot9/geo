#!/bin/bash
cd /root/.openclaw/workspace-open-lead/geo-platform/scanner
PYTHONPATH=. python3 -m geo_scanner.cli "$@"

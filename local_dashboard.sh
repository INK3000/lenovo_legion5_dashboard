#!/usr/bin/env bash
# Launcher for local_dashboard.
# Place this file at /usr/local/bin/local_dashboard and chmod +x.
# The package itself lives at /usr/local/lib/local_dashboard/ (or wherever you put it).
exec python3 -m local_dashboard "$@"

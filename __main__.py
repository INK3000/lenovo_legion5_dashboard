#!/usr/bin/env python3
"""
Local Dashboard — battery monitor with conservation mode toggle.
Usage:
    python -m local_dashboard
    # or if installed to /usr/local/bin/local_dashboard:
    local_dashboard
"""
from .server import main

if __name__ == "__main__":
    main()

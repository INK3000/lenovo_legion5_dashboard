# local_dashboard

Minimal battery monitor dashboard — Python stdlib only, works fully offline.

## Features
- Live charge %, status, power draw, ETA (time to empty / time to full)
- Conservation mode toggle (Lenovo IdeaPad `ideapad_acpi`)
- Charge history chart with smart time axis (minutes ↔ hours)
- Top 10 processes by CPU / estimated power draw
- System uptime
- Dark industrial UI — IBM Plex Mono + Tailwind CSS, all offline

## Install

```bash
make
```

That's it. The Makefile will:
1. Download Tailwind JS and IBM Plex fonts into `local_dashboard/static/`
2. Copy the package to `/usr/local/lib/local_dashboard/`
3. Install and enable the systemd service
4. Start the service and verify it's running

Open in browser: **http://127.0.0.1:47652/**

## Other commands

```bash
make status     # show service status
make logs       # follow journald logs
make restart    # restart the service
make uninstall  # stop, disable, and remove everything
```

## Environment variables

Edit `/etc/systemd/system/local-dashboard.service`, then:
```bash
sudo systemctl daemon-reload && make restart
```

| Variable         | Default     | Description                           |
|------------------|-------------|---------------------------------------|
| `DASH_HOST`      | `127.0.0.1` | Bind address                          |
| `DASH_PORT`      | `47652`     | Port                                  |
| `BATTERY_NAME`   | `BAT0`      | Battery in `/sys/class/power_supply/` |
| `SAMPLE_SECONDS` | `10`        | Sampling interval in seconds          |
| `MAX_POINTS`     | ~4320       | Ring buffer size (~12h at 10s)        |

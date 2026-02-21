# local_dashboard

Minimal battery monitor dashboard — Python stdlib only (+ Tailwind CDN via browser).

## Features
- Live charge %, status badge, power draw, ETA (time to empty / time to full)
- Conservation mode toggle (Lenovo IdeaPad `ideapad_acpi`)
- Charge history chart with smart time axis (minutes ↔ hours)
- Top 10 processes by CPU / estimated power draw
- System uptime
- Dark industrial UI via Tailwind CSS + IBM Plex Mono

## Install

```bash
# 1. Copy the package
sudo cp -r local_dashboard /usr/local/lib/

# 2. Download Tailwind for offline use (once)
curl -sL https://cdn.tailwindcss.com -o local_dashboard/static/tailwind.js
sudo cp local_dashboard/static/tailwind.js /usr/local/lib/local_dashboard/static/tailwind.js

# 3. Copy and enable the systemd service
sudo cp local-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now local-dashboard

# 4. Check it's running
sudo systemctl status local-dashboard
```

> **Без интернета?** Если `tailwind.js` есть в `static/` — дашборд работает полностью офлайн.
> Если файла нет — автоматически подгружается с CDN (нужен интернет).

Open in browser: http://127.0.0.1:47652/

## Logs

```bash
journalctl -u local-dashboard -f
```

## Environment variables

| Variable         | Default     | Description                                        |
|------------------|-------------|----------------------------------------------------|
| `DASH_HOST`      | `127.0.0.1` | Bind address                                       |
| `DASH_PORT`      | `47652`     | Port                                               |
| `BATTERY_NAME`   | `BAT0`      | Battery name in `/sys/class/power_supply/`         |
| `SAMPLE_SECONDS` | `10`        | Sampling interval in seconds                       |
| `MAX_POINTS`     | ~4320       | Ring buffer size (~12h at 10s)                     |

To override, edit `/etc/systemd/system/local-dashboard.service` and run:
```bash
sudo systemctl daemon-reload && sudo systemctl restart local-dashboard
```

## Uninstall

```bash
sudo systemctl disable --now local-dashboard
sudo rm /etc/systemd/system/local-dashboard.service
sudo rm -rf /usr/local/lib/local_dashboard
```

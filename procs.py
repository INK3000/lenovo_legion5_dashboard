"""
Process power estimation.

Strategy (no root required):
  1. Read /proc/<pid>/stat for all processes twice with a short interval.
  2. Compute CPU% per process over that interval.
  3. Multiply by current total power_now → estimated watts per process.

This gives proportional attribution, not true per-process power measurement.
Result is cached and refreshed every PROC_INTERVAL seconds in a background thread.
"""

import os
import re
import time
import threading
from dataclasses import dataclass, field

PROC_INTERVAL = 15        # seconds between full scans
TOP_N         = 10        # max processes to return
MIN_CPU_PCT   = 0.1       # skip processes below this CPU%

_LOCK   = threading.Lock()
_RESULT: list[dict] = []   # [{name, pid, cpu_pct, est_w}]
_METHOD = "cpu"            # "cpu" always for now


@dataclass
class _ProcSnap:
    pid:  int
    name: str
    cpu_ticks: int         # utime + stime from /proc/<pid>/stat


def _read_proc_stat(pid: int) -> _ProcSnap | None:
    try:
        stat_path = f"/proc/{pid}/stat"
        with open(stat_path, "r") as f:
            raw = f.read()
        # comm can contain spaces/parens, parse carefully
        m = re.match(r"(\d+)\s+\((.+)\)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+)\s+(\d+)", raw)
        if not m:
            return None
        pid_  = int(m.group(1))
        name  = m.group(2)
        utime = int(m.group(3))
        stime = int(m.group(4))
        return _ProcSnap(pid=pid_, name=name, cpu_ticks=utime + stime)
    except Exception:
        return None


def _all_pids() -> list[int]:
    pids = []
    for entry in os.scandir("/proc"):
        if entry.is_dir() and entry.name.isdigit():
            pids.append(int(entry.name))
    return pids


def _snapshot() -> dict[int, _ProcSnap]:
    result = {}
    for pid in _all_pids():
        snap = _read_proc_stat(pid)
        if snap:
            result[pid] = snap
    return result


def _hz() -> int:
    try:
        import os as _os
        return _os.sysconf("SC_CLK_TCK")
    except Exception:
        return 100


def _read_total_watts() -> tuple[float, bool]:
    """
    Returns (watts, is_discharging).
    watts is meaningful only when discharging.
    """
    from . import config
    try:
        status = ""
        if os.path.exists(config.STATUS_PATH):
            with open(config.STATUS_PATH) as f:
                status = f.read().strip().lower()
        is_discharging = "discharg" in status

        if os.path.exists(config.POWER_NOW_PATH):
            v = int(open(config.POWER_NOW_PATH).read().strip())
            return abs(v) / 1_000_000.0, is_discharging
        if os.path.exists(config.CURRENT_NOW_PATH) and os.path.exists(config.VOLTAGE_NOW_PATH):
            µa = int(open(config.CURRENT_NOW_PATH).read().strip())
            µv = int(open(config.VOLTAGE_NOW_PATH).read().strip())
            return abs(µa * µv) / 1_000_000_000_000.0, is_discharging
    except Exception:
        pass
    return 0.0, False


def _scan_once():
    hz = _hz()
    snap1 = _snapshot()
    time.sleep(2.0)           # measure window
    snap2 = _snapshot()
    watts, is_discharging = _read_total_watts()

    # total ticks delta across all processes
    deltas: list[tuple[str, int, int]] = []   # (name, pid, delta_ticks)
    for pid, s2 in snap2.items():
        s1 = snap1.get(pid)
        if s1 is None:
            continue
        d = s2.cpu_ticks - s1.cpu_ticks
        if d > 0:
            deltas.append((s2.name, pid, d))

    total_delta = sum(d for _, _, d in deltas) or 1

    # cpu% and estimated watts per process
    entries = []
    for name, pid, d in deltas:
        cpu_pct = (d / total_delta) * 100.0
        if cpu_pct < MIN_CPU_PCT:
            continue
        est_w = (d / total_delta) * watts if is_discharging else None
        entries.append({
            "name":    name,
            "pid":     pid,
            "cpu_pct": round(cpu_pct, 1),
            "est_w":   round(est_w, 3) if est_w is not None else None,
        })

    entries.sort(key=lambda x: x["est_w"], reverse=True)
    entries = entries[:TOP_N]

    with _LOCK:
        _RESULT.clear()
        _RESULT.extend(entries)


def get_proc_stats() -> list[dict]:
    with _LOCK:
        return list(_RESULT)


def proc_sampler():
    """Background thread — runs forever."""
    while True:
        try:
            _scan_once()
        except Exception:
            pass
        time.sleep(PROC_INTERVAL)

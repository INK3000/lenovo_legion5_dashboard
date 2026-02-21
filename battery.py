import os
import time
import threading
from collections import deque
from . import config

DATA: deque = deque(maxlen=config.MAX_POINTS)
LOCK = threading.Lock()


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _read_int(path: str) -> int:
    return int(_read_text(path))


def _read_watts_or_none() -> float | None:
    try:
        if os.path.exists(config.POWER_NOW_PATH):
            return abs(_read_int(config.POWER_NOW_PATH)) / 1_000_000.0
        if os.path.exists(config.CURRENT_NOW_PATH) and os.path.exists(config.VOLTAGE_NOW_PATH):
            µa = _read_int(config.CURRENT_NOW_PATH)
            µv = _read_int(config.VOLTAGE_NOW_PATH)
            return abs(µa * µv) / 1_000_000_000_000.0
    except Exception:
        pass
    return None


def _read_capacity_wh() -> tuple[float | None, float | None]:
    """Returns (energy_now_wh, energy_full_wh) or (None, None)."""
    try:
        if os.path.exists(config.ENERGY_NOW_PATH) and os.path.exists(config.ENERGY_FULL_PATH):
            now  = _read_int(config.ENERGY_NOW_PATH)  / 1_000_000.0
            full = _read_int(config.ENERGY_FULL_PATH) / 1_000_000.0
            return now, full
        if os.path.exists(config.CURRENT_NOW_PATH) and os.path.exists(config.VOLTAGE_NOW_PATH):
            if os.path.exists(config.CHARGE_NOW_PATH) and os.path.exists(config.CHARGE_FULL_PATH):
                µv   = _read_int(config.VOLTAGE_NOW_PATH)
                c_now  = _read_int(config.CHARGE_NOW_PATH)
                c_full = _read_int(config.CHARGE_FULL_PATH)
                v = µv / 1_000_000.0
                now  = c_now  / 1_000_000.0 * v
                full = c_full / 1_000_000.0 * v
                return now, full
    except Exception:
        pass
    return None, None


CONSERVATION_CHARGE_LIMIT = 0.80  # ideapad caps charge at ~80%


def estimate_time_remaining(status: str, watts: float | None,
                             conservation: bool = False) -> float | None:
    """
    Returns estimated hours remaining (discharge) or until full (charge).
    When conservation=True, target charge ceiling is 80% of energy_full.
    Returns None if cannot estimate.
    """
    if watts is None or watts < 0.05:
        return None
    energy_now, energy_full = _read_capacity_wh()
    if energy_now is None:
        return None

    s = status.lower()
    if "discharg" in s:
        return energy_now / watts          # hours until empty

    if "charg" in s:
        target_wh = energy_full * (CONSERVATION_CHARGE_LIMIT if conservation else 1.0)
        remaining_wh = target_wh - energy_now
        if remaining_wh <= 0:
            return 0.0
        return remaining_wh / watts        # hours until target
    return None


def get_conservation_mode() -> bool | None:
    path = config.CONSERVATION_MODE_PATH
    if not os.path.exists(path):
        return None
    try:
        return _read_int(path) == 1
    except Exception:
        return None


def set_conservation_mode(enabled: bool) -> bool:
    """Write directly — works when running as root (e.g. via systemd service)."""
    try:
        with open(config.CONSERVATION_MODE_PATH, "w") as f:
            f.write("1" if enabled else "0")
        return True
    except Exception:
        return False


def sampler():
    while True:
        try:
            pct    = _read_int(config.CAPACITY_PATH)
            status = _read_text(config.STATUS_PATH) if os.path.exists(config.STATUS_PATH) else "unknown"
            w      = _read_watts_or_none()
            ts     = time.time()
            conservation = get_conservation_mode() or False
            eta    = estimate_time_remaining(status, w, conservation=conservation)
            with LOCK:
                DATA.append((ts, pct, w, status, eta))
        except Exception:
            pass
        time.sleep(config.SAMPLE_SECONDS)

import os

HOST = os.environ.get("DASH_HOST", "127.0.0.1")
PORT = int(os.environ.get("DASH_PORT", "47652"))
BAT = os.environ.get("BATTERY_NAME", "BAT0")
SAMPLE_SECONDS = float(os.environ.get("SAMPLE_SECONDS", "10"))
MAX_POINTS = int(os.environ.get("MAX_POINTS", str(int(12 * 60 * 60 / SAMPLE_SECONDS))))

CAPACITY_PATH    = f"/sys/class/power_supply/{BAT}/capacity"
STATUS_PATH      = f"/sys/class/power_supply/{BAT}/status"
POWER_NOW_PATH   = f"/sys/class/power_supply/{BAT}/power_now"
CURRENT_NOW_PATH = f"/sys/class/power_supply/{BAT}/current_now"
VOLTAGE_NOW_PATH = f"/sys/class/power_supply/{BAT}/voltage_now"
ENERGY_NOW_PATH  = f"/sys/class/power_supply/{BAT}/energy_now"   # µWh
ENERGY_FULL_PATH = f"/sys/class/power_supply/{BAT}/energy_full"  # µWh
CHARGE_NOW_PATH  = f"/sys/class/power_supply/{BAT}/charge_now"   # µAh (fallback)
CHARGE_FULL_PATH = f"/sys/class/power_supply/{BAT}/charge_full"  # µAh (fallback)

CONSERVATION_MODE_PATH = "/sys/bus/platform/drivers/ideapad_acpi/VPC2004:00/conservation_mode"

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sys
from underwriting.controls import KillSwitch

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"on", "off"}:
        raise SystemExit("Usage: python scripts/kill_switch.py on|off")
    enabled = sys.argv[1] == "on"
    KillSwitch().set(enabled)
    print(f"kill_switch_enabled={enabled}")

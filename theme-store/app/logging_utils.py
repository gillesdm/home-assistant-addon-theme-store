import json
import os
import sys
from datetime import datetime

LEVELS = ["debug", "info", "warning", "error"]


def get_log_level():
    lvl = os.environ.get("LOG_LEVEL", "info").lower()
    return lvl if lvl in LEVELS else "info"


def log(level: str, message: str, **fields):
    level = level.lower()
    if level not in LEVELS:
        level = "info"
    # Basic level filter
    priority = {"debug": 10, "info": 20, "warning": 30, "error": 40}
    if priority[level] < priority[get_log_level()]:
        return
    payload = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "level": level,
        "msg": message,
        **fields,
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()

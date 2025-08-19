import json
import os
import tempfile
from typing import Any, Dict, List

from .logging_utils import log

CATALOG_DIR = "/data/theme-store"
CATALOG_PATH = f"{CATALOG_DIR}/catalog.json"
CATALOG_SCHEMA_VERSION = 1


def ensure_catalog() -> Dict[str, Any]:
    """Ensure catalog file exists; if missing, initialize with defaults."""
    os.makedirs(CATALOG_DIR, exist_ok=True)
    if not os.path.exists(CATALOG_PATH):
        data = {"schema_version": CATALOG_SCHEMA_VERSION, "themes": []}
        _atomic_write_json(CATALOG_PATH, data)
        log("info", "catalog initialized", path=CATALOG_PATH)
        return data

    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        # If corrupted, back it up and re-init
        backup = f"{CATALOG_PATH}.corrupted"
        try:
            os.rename(CATALOG_PATH, backup)
            log("warning", "catalog corrupted, backed up", backup=backup, error=str(e))
        except Exception as e2:
            log("error", "failed to backup corrupted catalog", error=str(e2))
        data = {"schema_version": CATALOG_SCHEMA_VERSION, "themes": []}
        _atomic_write_json(CATALOG_PATH, data)
        return data

    # Migrate if needed (future-proof)
    if data.get("schema_version", 0) < CATALOG_SCHEMA_VERSION:
        data = _migrate(data)
        _atomic_write_json(CATALOG_PATH, data)
        log("info", "catalog migrated", to_version=CATALOG_SCHEMA_VERSION)
    return data


def _migrate(data: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder for future migrations
    data["schema_version"] = CATALOG_SCHEMA_VERSION
    return data


def _atomic_write_json(path: str, data: Dict[str, Any]) -> None:
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=dir_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # atomic on POSIX
    finally:
        # If replace failed, try to cleanup
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def read_catalog() -> Dict[str, Any]:
    return ensure_catalog()


def write_catalog(data: Dict[str, Any]) -> None:
    _atomic_write_json(CATALOG_PATH, data)

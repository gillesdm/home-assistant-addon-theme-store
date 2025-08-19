import os
import re
import shutil
import tempfile
import urllib.request
from typing import Optional, Tuple
from urllib.parse import urlparse

import yaml

from .logging_utils import log

CONFIG_THEMES_DIR = "/config/themes"


def ensure_config_dir() -> str:
    os.makedirs(CONFIG_THEMES_DIR, exist_ok=True)
    return CONFIG_THEMES_DIR


def _safe_theme_id(theme_id: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9_\-\.]+", theme_id or ""):
        raise ValueError("invalid_theme_id")
    return theme_id


def _write_atomic(path: str, data: str) -> None:
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=dir_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def _validate_yaml(content: str) -> dict:
    try:
        data = yaml.safe_load(content) or {}
        if not isinstance(data, dict):
            raise ValueError("theme_yaml_must_be_dict")
        return data
    except Exception as e:
        raise ValueError(f"invalid_yaml:{e}")


def _download_url(url: str, max_bytes: int = 2_000_000) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("unsupported_scheme")
    with urllib.request.urlopen(url, timeout=20) as resp:
        size = int(resp.headers.get("Content-Length", "0") or "0")
        if size and size > max_bytes:
            raise ValueError("file_too_large")
        content = resp.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise ValueError("file_too_large")
        return content.decode("utf-8", "replace")


def list_installed() -> list[dict]:
    ensure_config_dir()
    items = []
    for name in sorted(os.listdir(CONFIG_THEMES_DIR)):
        if not name.endswith(".yaml"):
            continue
        path = os.path.join(CONFIG_THEMES_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            data = {}
        items.append({"id": name[:-5], "path": path, "valid": isinstance(data, dict)})
    return items


def install_theme(
    theme_id: str, content: Optional[str] = None, url: Optional[str] = None
) -> Tuple[str, str]:
    ensure_config_dir()
    theme_id = _safe_theme_id(theme_id)

    if content is None and url is None:
        raise ValueError("content_or_url_required")
    if content is not None and url is not None:
        raise ValueError("provide_only_one_of_content_or_url")

    if url:
        log("info", "downloading_theme_yaml", id=theme_id, url=url)
        content = _download_url(url)

    assert content is not None
    _validate_yaml(content)  # raises if invalid

    dest = os.path.join(CONFIG_THEMES_DIR, f"{theme_id}.yaml")
    _write_atomic(dest, content)
    log("info", "theme_yaml_installed", id=theme_id, path=dest)
    return theme_id, dest


def uninstall_theme(theme_id: str) -> bool:
    ensure_config_dir()
    theme_id = _safe_theme_id(theme_id)
    path = os.path.join(CONFIG_THEMES_DIR, f"{theme_id}.yaml")
    if os.path.exists(path):
        os.remove(path)
        log("warning", "theme_yaml_removed", id=theme_id)
        return True
    return False

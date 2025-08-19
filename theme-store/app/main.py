import os
import time
from typing import List

from fastapi import FastAPI, HTTPException, Response

from .installer import install_theme, list_installed, uninstall_theme
from .logging_utils import log
from .models import (
    DeleteResult,
    InstalledTheme,
    InstallRequest,
    InstallResult,
    Theme,
    ThemeCreate,
)
from .storage import CATALOG_PATH, read_catalog, write_catalog

APP_VERSION = os.environ.get("APP_VERSION", "0.0.6")
START_TS = time.time()

app = FastAPI(title="Theme Store Add-on API", version=APP_VERSION)


@app.get("/healthz", status_code=204)
def healthz():
    return Response(status_code=204)


@app.get("/api/v1/info")
def info():
    uptime = int(time.time() - START_TS)
    return {
        "name": "theme-store-addon",
        "version": APP_VERSION,
        "uptime_seconds": uptime,
        "catalog_path": CATALOG_PATH,
    }


# Catalog
@app.get("/api/v1/themes", response_model=List[Theme])
def list_themes():
    cat = read_catalog()
    return cat.get("themes", [])


@app.post("/api/v1/themes", response_model=Theme, status_code=201)
def add_or_update_theme(payload: ThemeCreate):
    cat = read_catalog()
    themes = cat.setdefault("themes", [])
    for idx, t in enumerate(themes):
        if t["id"] == payload.id:
            themes[idx] = payload.dict()
            write_catalog(cat)
            log("info", "theme_updated", id=payload.id)
            return Theme(**themes[idx])
    themes.append(payload.dict())
    write_catalog(cat)
    log("info", "theme_added", id=payload.id)
    return Theme(**themes[-1])


@app.delete("/api/v1/themes/{theme_id}", response_model=DeleteResult)
def delete_theme(theme_id: str):
    cat = read_catalog()
    themes = cat.get("themes", [])
    new_list = [t for t in themes if t["id"] != theme_id]
    if len(new_list) == len(themes):
        raise HTTPException(status_code=404, detail="theme_not_found")
    cat["themes"] = new_list
    write_catalog(cat)
    log("warning", "theme_deleted", id=theme_id)
    return DeleteResult(status="deleted")


# Installer
@app.get("/api/v1/install", response_model=List[InstalledTheme])
def get_installed():
    items = list_installed()
    return [InstalledTheme(**x) for x in items]


@app.post("/api/v1/install", response_model=InstallResult, status_code=201)
def install(payload: InstallRequest):
    try:
        theme_id, path = install_theme(
            payload.id,
            content=payload.content,
            url=str(payload.url) if payload.url else None,
        )
        return InstallResult(id=theme_id, path=path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/v1/install/{theme_id}", response_model=DeleteResult)
def uninstall(theme_id: str):
    ok = uninstall_theme(theme_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not_installed")
    return DeleteResult(status="deleted")

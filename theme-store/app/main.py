import os
import time
from typing import List

from fastapi import FastAPI, HTTPException, Response

from .logging_utils import log
from .models import DeleteResult, Theme, ThemeCreate
from .storage import CATALOG_PATH, read_catalog, write_catalog

APP_VERSION = os.environ.get("APP_VERSION", "0.0.5")
START_TS = time.time()

app = FastAPI(title="Theme Store Add-on API", version=APP_VERSION)


@app.get("/healthz", status_code=204)
def healthz():
    return Response(status_code=204)


@app.get("/api/v1/info")
def info():
    uptime = int(time.time() - START_TS)
    log("debug", "info endpoint", uptime=uptime)
    return {
        "name": "theme-store-addon",
        "version": APP_VERSION,
        "uptime_seconds": uptime,
        "catalog_path": CATALOG_PATH,
    }


@app.get("/api/v1/themes", response_model=List[Theme])
def list_themes():
    cat = read_catalog()
    themes = cat.get("themes", [])
    log("info", "list_themes", count=len(themes))
    return themes


@app.post("/api/v1/themes", response_model=Theme, status_code=201)
def add_or_update_theme(payload: ThemeCreate):
    cat = read_catalog()
    themes = cat.setdefault("themes", [])
    # update if exists
    for idx, t in enumerate(themes):
        if t["id"] == payload.id:
            themes[idx] = payload.dict()
            write_catalog(cat)
            log("info", "theme_updated", id=payload.id)
            return Theme(**themes[idx])
    # otherwise add
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

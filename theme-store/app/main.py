import os
import time

from fastapi import FastAPI, Response

from .logging_utils import log
from .models import Theme

APP_VERSION = os.environ.get("APP_VERSION", "0.0.4")
START_TS = time.time()

app = FastAPI(title="Theme Store Add-on API", version=APP_VERSION)


@app.get("/healthz", status_code=204)
def healthz():
    return Response(status_code=204)


@app.get("/api/v1/info")
def info():
    uptime = int(time.time() - START_TS)
    log("debug", "info endpoint called", uptime=uptime)
    return {
        "name": "theme-store-addon",
        "version": APP_VERSION,
        "uptime_seconds": uptime,
    }


@app.get("/api/v1/themes", response_model=list[Theme])
def list_themes():
    log("info", "list_themes", count=0)
    return []

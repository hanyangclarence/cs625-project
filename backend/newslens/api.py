"""Single FastAPI server combining pipeline + feedback APIs.

Run with:
  uvicorn newslens.api:app --port 8787 --reload

Endpoints:
  POST /api/run             {topic, max_sources?, verify?} -> {job_id, topic_id}
  GET  /api/jobs/{job_id}   -> {status, progress[], topic_id, error?}
  POST /feedback            (mounted from feedback.api)
  POST /audit
  GET  /signals/{topic_id}
  GET  /audit/{topic_id}
"""

from __future__ import annotations

import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import run as run_module
from .feedback import store as fb_store

app = FastAPI(title="NewsLens API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Pipeline endpoints ------------------------------------------------------

JOBS: dict[str, dict[str, Any]] = {}
JOBS_LOCK = threading.Lock()
EXECUTOR = ThreadPoolExecutor(max_workers=2)


class RunRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    max_sources: int = Field(default=3, ge=1, le=12)
    verify: bool = False


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", s) or "topic"


def _do_run(job_id: str, topic: str, topic_id: str, max_sources: int, verify: bool) -> None:
    def progress(line: str) -> None:
        with JOBS_LOCK:
            JOBS[job_id]["progress"].append(line)

    try:
        run_module.run(
            topic=topic,
            topic_id=topic_id,
            max_sources=max_sources,
            verify=verify,
            on_progress=progress,
        )
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "done"
    except Exception as exc:  # noqa: BLE001
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = f"{type(exc).__name__}: {exc}"


@app.post("/api/run")
def start_run(req: RunRequest) -> dict[str, str]:
    topic_id = _slugify(req.topic)
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "running",
            "progress": [],
            "topic_id": topic_id,
            "topic": req.topic,
            "error": None,
        }
    EXECUTOR.submit(_do_run, job_id, req.topic, topic_id, req.max_sources, req.verify)
    return {"job_id": job_id, "topic_id": topic_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(404, "unknown job")
        return dict(job)


# ---- Feedback endpoints (kept from feedback/api.py) --------------------------


class Signal(BaseModel):
    topic_id: str
    view: Literal["cross-source", "claim-trace"]
    signal: Literal["+", "-"]
    claim_id: str | None = None
    source_id: str | None = None
    note: str | None = None


class AuditLabel(BaseModel):
    topic_id: str
    target: Literal["source", "claim", "evidence", "timeline"]
    target_id: str
    label: Literal["correct", "incorrect"]
    rationale: str | None = None


@app.post("/feedback")
def post_feedback(item: Signal) -> dict:
    fb_store.append_signal(item.topic_id, item.model_dump())
    return {"ok": True}


@app.post("/audit")
def post_audit(item: AuditLabel) -> dict:
    fb_store.append_audit(item.topic_id, item.model_dump())
    return {"ok": True}


@app.get("/signals/{topic_id}")
def get_signals(topic_id: str) -> list[dict]:
    return fb_store.read("signals", topic_id)


@app.get("/audit/{topic_id}")
def get_audit(topic_id: str) -> list[dict]:
    return fb_store.read("audit", topic_id)

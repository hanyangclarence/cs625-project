"""FastAPI server for collecting user feedback and expert audit labels.

Run with:
  uvicorn newslens.feedback.api:app --port 8787

Endpoints:
  POST /feedback  body: {topic_id, view, claim_id?, signal: '+'|'-', note?}
  POST /audit     body: {topic_id, target: 'source'|'claim'|'evidence'|'timeline',
                          target_id, label: 'correct'|'incorrect', rationale?}
  GET  /signals/{topic_id}
  GET  /audit/{topic_id}
"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import store

app = FastAPI(title="NewsLens feedback API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    if not item.topic_id:
        raise HTTPException(400, "topic_id required")
    store.append_signal(item.topic_id, item.model_dump())
    return {"ok": True}


@app.post("/audit")
def post_audit(item: AuditLabel) -> dict:
    if not item.topic_id:
        raise HTTPException(400, "topic_id required")
    store.append_audit(item.topic_id, item.model_dump())
    return {"ok": True}


@app.get("/signals/{topic_id}")
def get_signals(topic_id: str) -> list[dict]:
    return store.read("signals", topic_id)


@app.get("/audit/{topic_id}")
def get_audit(topic_id: str) -> list[dict]:
    return store.read("audit", topic_id)

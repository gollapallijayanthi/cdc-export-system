from fastapi import FastAPI, BackgroundTasks, Header
from datetime import datetime
from app.services.full_export import run_full_export

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/exports/full")
def full_export(
    background_tasks: BackgroundTasks,
    x_consumer_id: str = Header(...)
):
    background_tasks.add_task(run_full_export, x_consumer_id)

    return {
        "status": "started",
        "exportType": "full",
        "consumerId": x_consumer_id
    }
from app.services.incremental_export import run_incremental_export

@app.post("/exports/incremental")
def incremental_export(
    background_tasks: BackgroundTasks,
    x_consumer_id: str = Header(...)
):
    background_tasks.add_task(run_incremental_export, x_consumer_id)

    return {
        "status": "started",
        "exportType": "incremental",
        "consumerId": x_consumer_id
    }
from app.services.delta_export import run_delta_export

@app.post("/exports/delta")
def delta_export(
    background_tasks: BackgroundTasks,
    x_consumer_id: str = Header(...)
):
    background_tasks.add_task(run_delta_export, x_consumer_id)

    return {
        "status": "started",
        "exportType": "delta",
        "consumerId": x_consumer_id
    }
from app.database import SessionLocal
from app.models import Watermark
from fastapi import HTTPException

@app.get("/exports/watermark")
def get_watermark(x_consumer_id: str = Header(...)):
    db = SessionLocal()
    wm = db.query(Watermark).filter_by(consumer_id=x_consumer_id).first()
    db.close()

    if not wm:
        raise HTTPException(status_code=404, detail="No watermark found")

    return {
        "consumerId": wm.consumer_id,
        "lastExportedAt": wm.last_exported_at.isoformat()
    }
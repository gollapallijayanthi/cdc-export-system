import os
import time
import csv
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import User, Watermark


def run_delta_export(consumer_id: str):
    print(f"[DELTA] Export started for {consumer_id}")

    db = SessionLocal()

    
    watermark = db.query(Watermark).filter_by(consumer_id=consumer_id).first()

    
    if not watermark:
        print(f"[DELTA] No watermark found for {consumer_id}. Run full export first.")
        db.close()
        return

    last_ts = watermark.last_exported_at

    
    users = db.query(User).filter(User.updated_at > last_ts).all()

    rows = []
    max_ts = last_ts

    for u in users:
        if u.is_deleted:
            operation = "DELETE"
        elif u.created_at == u.updated_at:
            operation = "INSERT"
        else:
            operation = "UPDATE"

        rows.append([
            operation,
            u.id,
            u.name,
            u.email,
            u.created_at,
            u.updated_at,
            u.is_deleted
        ])

        if u.updated_at > max_ts:
            max_ts = u.updated_at

    filename = f"delta_{consumer_id}_{int(time.time())}.csv"
    file_path = os.path.join(os.getenv("EXPORT_DIR"), filename)

    
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["operation", "id", "name", "email", "created_at", "updated_at", "is_deleted"]
        )
        writer.writerows(rows)

    
    if rows:
        watermark.last_exported_at = max_ts
        watermark.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.close()

    print(f"[DELTA] Export completed for {consumer_id} with {len(rows)} rows")
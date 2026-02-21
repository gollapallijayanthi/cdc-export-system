import os
import time
from datetime import datetime, timezone
from app.database import SessionLocal
from app.models import User, Watermark
from app.utils.csv_writer import write_csv

def run_incremental_export(consumer_id: str):
    print(f"[INCREMENTAL] Export started for {consumer_id}")

    db = SessionLocal()

    watermark = db.query(Watermark).filter_by(consumer_id=consumer_id).first()
    last_ts = (
    watermark.last_exported_at
    if watermark
    else datetime.min.replace(tzinfo=timezone.utc)
)

    users = (
        db.query(User)
        .filter(User.updated_at > last_ts)
        .filter(User.is_deleted == False)
        .all()
    )

    print(f"[INCREMENTAL] Found {len(users)} updated users")

    rows = []
    max_ts = last_ts

    for u in users:
        rows.append([
            u.id,
            u.name,
            u.email,
            u.created_at,
            u.updated_at,
            u.is_deleted
        ])
        if u.updated_at > max_ts:
            max_ts = u.updated_at

    filename = f"incremental_{consumer_id}_{int(time.time())}.csv"
    file_path = os.path.join(os.getenv("EXPORT_DIR"), filename)

    write_csv(file_path, rows)
    print(f"[INCREMENTAL] CSV written: {filename}")

    # Update watermark ONLY if rows exist
    if users:
        if watermark:
            watermark.last_exported_at = max_ts
            watermark.updated_at = datetime.utcnow()
        else:
            db.add(Watermark(
                consumer_id=consumer_id,
                last_exported_at=max_ts,
                updated_at=datetime.utcnow()
            ))

    db.commit()
    db.close()

    print(f"[INCREMENTAL] Export completed for {consumer_id}")
import os
import time
from datetime import datetime
from app.database import SessionLocal
from app.models import User, Watermark
from app.utils.csv_writer import write_csv

def run_full_export(consumer_id: str):
    db = SessionLocal()

    users = db.query(User).filter(User.is_deleted == False).all()

    rows = []
    max_ts = None

    for u in users:
        rows.append([
            u.id,
            u.name,
            u.email,
            u.created_at,
            u.updated_at,
            u.is_deleted
        ])
        if not max_ts or u.updated_at > max_ts:
            max_ts = u.updated_at

    filename = f"full_{consumer_id}_{int(time.time())}.csv"
    file_path = os.path.join(os.getenv("EXPORT_DIR"), filename)

    write_csv(file_path, rows)

    
    if max_ts:
        watermark = db.query(Watermark).filter_by(consumer_id=consumer_id).first()
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

    return filename, len(rows)
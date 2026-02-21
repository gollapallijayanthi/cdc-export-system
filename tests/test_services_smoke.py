from datetime import datetime, timedelta

from app.services.full_export import run_full_export
from app.services.incremental_export import run_incremental_export
from app.services.delta_export import run_delta_export


# -------------------------------------------------
# Shared Dummy Session (no watermark case)
# -------------------------------------------------
class DummySession:
    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, *args, **kwargs):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def add(self, *args, **kwargs):
        pass

    def commit(self):
        pass

    def close(self):
        pass


# -------------------------------------------------
# Smoke tests
# -------------------------------------------------
def test_full_export_smoke(monkeypatch):
    monkeypatch.setenv("EXPORT_DIR", "/tmp")
    monkeypatch.setattr(
        "app.services.full_export.SessionLocal",
        lambda: DummySession()
    )
    run_full_export("test-consumer")


def test_incremental_export_smoke(monkeypatch):
    monkeypatch.setenv("EXPORT_DIR", "/tmp")
    monkeypatch.setattr(
        "app.services.incremental_export.SessionLocal",
        lambda: DummySession()
    )
    run_incremental_export("test-consumer")


def test_delta_export_smoke(monkeypatch):
    monkeypatch.setenv("EXPORT_DIR", "/tmp")
    monkeypatch.setattr(
        "app.services.delta_export.SessionLocal",
        lambda: DummySession()
    )
    run_delta_export("test-consumer")


# -------------------------------------------------
# Delta export WITH existing watermark (coverage boost)
# -------------------------------------------------
def test_delta_export_with_existing_watermark(monkeypatch):
    monkeypatch.setenv("EXPORT_DIR", "/tmp")

    class DummyWatermark:
        last_exported_at = datetime.utcnow() - timedelta(days=1)

    class DummyUser:
        id = 1
        name = "Test"
        email = "t@test.com"
        created_at = datetime.utcnow() - timedelta(days=2)
        updated_at = datetime.utcnow() - timedelta(hours=1)
        is_deleted = True  # force DELETE path

    class DummySessionWithWatermark:
        def query(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

        def filter_by(self, *args, **kwargs):
            return self

        def all(self):
            return [DummyUser()]

        def first(self):
            return DummyWatermark()

        def add(self, *args, **kwargs):
            pass

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(
        "app.services.delta_export.SessionLocal",
        lambda: DummySessionWithWatermark()
    )

    run_delta_export("existing-consumer")
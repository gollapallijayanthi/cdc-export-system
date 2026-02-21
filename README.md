
# CDC Export System – Application-Level Change Data Capture

## 📌 Objective

Build a **production-ready, containerized data export system** that uses **Change Data Capture (CDC)** principles to efficiently synchronize large datasets.

This project demonstrates:

- Stateful CDC using **watermarking**
- Efficient **full, incremental, and delta exports**
- Asynchronous background processing
- Handling large datasets (100,000+ rows)
- Production-grade containerization and testing

This system simulates real-world backend data pipelines used to sync operational databases with downstream consumers such as data warehouses, analytics systems, or microservices.

---

## 🧠 Background (CDC & Watermarking)

Exporting entire datasets repeatedly is inefficient for large tables.  
**Change Data Capture (CDC)** solves this by exporting **only data that has changed**.

This project implements **application-level CDC** using:

- `updated_at` timestamps
- Soft deletes (`is_deleted`)
- **Watermarks** (high-water marks per consumer)

Each consumer maintains its own export state, preventing:

- Duplicate exports
- Data loss
- Cross-consumer interference

---

## 🏗 Architecture Overview

```

Client
│
│ REST API
▼
FastAPI Application (Docker)
├── Full Export Service
├── Incremental Export Service
├── Delta Export Service
├── Watermark Manager
├── CSV Writer
└── Background Jobs
│
▼
PostgreSQL Database (Docker)
├── users
└── watermarks

```

- Docker Compose orchestrates services
- PostgreSQL stores users and consumer watermarks
- Exports run asynchronously
- CSV files are written to a shared volume (`output`)

---

## 🧰 Tech Stack

- **Language**: Python 3.10
- **Framework**: FastAPI
- **Database**: PostgreSQL 13
- **ORM**: SQLAlchemy
- **Containerization**: Docker, Docker Compose
- **Testing**: Pytest, pytest-cov

---

## 📂 Project Structure

```

cdc-export-system/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── services/
│   │   ├── full_export.py
│   │   ├── incremental_export.py
│   │   └── delta_export.py
│   └── utils/
│       └── csv_writer.py
├── seeds/
│   └── seed.sql
├── tests/
│   ├── test_health.py
│   └── test_services_smoke.py
├── output/               # CSV exports (gitignored)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md

````

---

## 🐳 Running the Project (One Command Setup)

### Prerequisites
- Docker
- Docker Compose

### Start the System

```bash
docker-compose up --build
````

### Verify Containers

```bash
docker-compose ps
```

**Expected Output**

* `db` → healthy
* `app` → running on port 8080

---

## ❤️ Health Check

```bash
curl http://localhost:8080/health
```

**Expected Response**

```json
{
  "status": "ok",
  "timestamp": "ISO_8601_TIMESTAMP"
}
```

---

## 🗄 Database Schema Verification

### Connect to Database

```bash
docker-compose exec db psql -U user -d mydatabase
```

### Verify Tables

```sql
\d users;
\d watermarks;
```

### users Table

| Column     | Type         | Description   |
| ---------- | ------------ | ------------- |
| id         | BIGINT       | Primary key   |
| name       | VARCHAR      | User name     |
| email      | VARCHAR      | Unique        |
| created_at | TIMESTAMP TZ | Creation time |
| updated_at | TIMESTAMP TZ | Update time   |
| is_deleted | BOOLEAN      | Soft delete   |

Index:

* `idx_users_updated_at` on `updated_at`

### watermarks Table

| Column           | Description           |
| ---------------- | --------------------- |
| consumer_id      | Unique consumer       |
| last_exported_at | Watermark timestamp   |
| updated_at       | Watermark update time |

---

## 🌱 Database Seeding (Automatic)

The database is automatically seeded on startup using `docker-entrypoint-initdb.d`.

### Seed Guarantees

* ≥ 100,000 users
* ≥ 1% soft-deleted users
* Timestamps spread across multiple days
* Idempotent seeding

### Verify Seed Data

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM users WHERE is_deleted = TRUE;
SELECT MIN(updated_at), MAX(updated_at) FROM users;
```

---

## 📤 Export APIs

All exports are **asynchronous** and write CSV files to `output/`.

---

### 🔹 Full Export

Exports all non-deleted users.

```bash
curl -X POST http://localhost:8080/exports/full \
  -H "X-Consumer-ID: consumer-1"
```

**Expected Behavior**

* CSV file created: `full_consumer-1_<timestamp>.csv`
* Watermark initialized or updated

---

### 🔹 Incremental Export

Exports users updated after the consumer’s watermark.

```bash
curl -X POST http://localhost:8080/exports/incremental \
  -H "X-Consumer-ID: consumer-1"
```

**Verification Steps**

1. Run full export
2. Update some users:

   ```sql
   UPDATE users SET updated_at = NOW() WHERE id IN (1,2,3);
   ```
3. Trigger incremental export
4. CSV contains only updated rows

---

### 🔹 Delta Export

Exports changes with operation type.

```bash
curl -X POST http://localhost:8080/exports/delta \
  -H "X-Consumer-ID: consumer-3"
```

**Operation Rules**

* `INSERT` → created_at == updated_at
* `UPDATE` → updated record
* `DELETE` → is_deleted = TRUE

**CSV Format**

```
operation,id,name,email,created_at,updated_at,is_deleted
```

---

## 💧 Watermark API

### Get Watermark

```bash
curl -H "X-Consumer-ID: consumer-1" \
  http://localhost:8080/exports/watermark
```

**Responses**

* `200 OK` → watermark exists
* `404 Not Found` → no watermark yet

---

## 🔐 Watermark Guarantees

* Each consumer has independent state
* Watermarks update **only after successful export**
* Failed exports do not advance watermarks
* Prevents data duplication and loss

---

## 📜 Logging

Key events are logged:

* Export started
* Rows exported
* Export completed
* Export blocked (no watermark)
* Errors (if any)

View logs:

```bash
docker logs cdc-export-system-app-1
```

---

## 🧪 Testing & Coverage

### Run Tests

```bash
docker-compose exec app pytest --cov=app
```

### Coverage Result

```
TOTAL COVERAGE: 84%
```

✔ Meets and exceeds the required **70% coverage**

---

## 🔐 Environment Variables

Documented in `.env.example`:

```
DATABASE_URL=postgresql://user:password@db:5432/mydatabase
PORT=8080
EXPORT_DIR=/app/output
```

---

## 📦 Submission Checklist (Completed)

* Dockerized application
* Docker Compose orchestration
* Database health checks
* CDC-enabled schema
* 100k+ seeded dataset
* Full / Incremental / Delta exports
* Consumer-specific watermarking
* Structured logging
* Health endpoint
* Test coverage ≥ 70%
* `.env.example` provided
* One-command startup

---

## 🏁 Final Notes

This project demonstrates real-world backend engineering skills including:

* Stateful data processing
* CDC design patterns
* Asynchronous job handling
* Scalable architecture principles
* Production-ready testing and deployment

It closely mirrors patterns used in modern data pipelines and backend systems.

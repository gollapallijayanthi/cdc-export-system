-- ===============================
-- USERS TABLE
-- ===============================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- Index for CDC performance
CREATE INDEX IF NOT EXISTS idx_users_updated_at ON users(updated_at);

-- ===============================
-- WATERMARKS TABLE
-- ===============================
CREATE TABLE IF NOT EXISTS watermarks (
    id SERIAL PRIMARY KEY,
    consumer_id VARCHAR(255) UNIQUE NOT NULL,
    last_exported_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- ===============================
-- SEED USERS (IDEMPOTENT)
-- ===============================
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM users) < 100000 THEN
        INSERT INTO users (name, email, created_at, updated_at, is_deleted)
        SELECT
            'User ' || gs,
            'user' || gs || '@example.com',
            NOW() - (random() * interval '14 days'),
            NOW() - (random() * interval '7 days'),
            (random() < 0.01)
        FROM generate_series(1, 100000) gs
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
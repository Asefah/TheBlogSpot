CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    user_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username     VARCHAR(50) NOT NULL UNIQUE,
    email        VARCHAR(255) NOT NULL UNIQUE,
    full_name    VARCHAR(255),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    followers    INTEGER NOT NULL DEFAULT 0,
    posts        INTEGER NOT NULL DEFAULT 0,
    comments     INTEGER NOT NULL DEFAULT 0,
    active       BOOLEAN NOT NULL DEFAULT TRUE
);
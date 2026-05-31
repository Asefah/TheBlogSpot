CREATE EXTENSION IF NOT EXISTS "pgcrypto";


CREATE TABLE IF NOT EXISTS users (
    user_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    full_name       VARCHAR(255),
    bio             TEXT,
    avatar_url      VARCHAR(500),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    active          BOOLEAN NOT NULL DEFAULT TRUE
);



--FOLLOW LOGIC
CREATE TABLE IF NOT EXISTS follows (
    follower_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    followee_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id)
    CHECK (follower_id <> followee_id) -- Prevent users from following themselves
);



--STREAK LOGIC
CREATE TABLE IF NOT EXISTS user_reading_streaks(
    user_id UUID    PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    current_streak  INTEGER NOT NULL DEFAULT 0,
    longest_streak  INTEGER NOT NULL DEFAULT 0,
    last_read_date  DATE,
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);


--USER POST CREATION LOGIC
CREATE TABLE IF NOT EXISTS user_post_creations (
    id UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID    NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    post_id UUID    NOT NULL,
    posts_published INTEGER NOT NULL DEFAULT 0,
    posts_created   INTEGER NOT NULL DEFAULT 0,
    last_post_date  DATE,
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);




--NOTIFICATIONS
CREATE TYPE notification_type AS ENUM (
    'new_follower',
    'new_post',
    'new_post_reaction',
    'new_comment',
    'new_comment_mention',
    'post_mention',
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id        UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    actor_id            UUID REFERENCES users(user_id) ON DELETE SET NULL,
    type                notification_type NOT NULL,
    post_id             UUID,
    read                BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_id, read, created_at DESC);




-- VIEW  (derived counts, replaces old counters)
CREATE OR REPLACE VIEW user_stats AS
SELECT
    u.user_id,
    u.username,
    COUNT(DISTINCT f_in.follower_id)  AS followers,
    COUNT(DISTINCT f_out.followee_id) AS following,
    COUNT(DISTINCT p.post_id)         AS total_posts,
    COUNT(DISTINCT CASE WHEN p.published THEN p.post_id END) AS published_posts,
    COUNT(DISTINCT CASE WHEN NOT p.published THEN p.post_id END) AS drafts,
    COUNT(DISTINCT c.comment_id)      AS comments
FROM users u
LEFT JOIN follows   f_in  ON f_in.followee_id  = u.user_id
LEFT JOIN follows   f_out ON f_out.follower_id = u.user_id
LEFT JOIN posts     p     ON p.author_id       = u.user_id AND p.published
LEFT JOIN comments  c     ON c.author_id       = u.user_id
GROUP BY u.user_id, u.username;




-- Patch users table
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS bio         TEXT,
    ADD COLUMN IF NOT EXISTS avatar_url  VARCHAR(500),
    ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMP NOT NULL DEFAULT NOW();

-- Drop the fragile counters (derive these from relations instead)
ALTER TABLE users
    DROP COLUMN IF EXISTS followers,
    DROP COLUMN IF EXISTS posts,
    DROP COLUMN IF EXISTS comments;
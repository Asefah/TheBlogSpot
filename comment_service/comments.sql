CREATE TABLE IF NOT EXISTS comments (
    comment_id   SERIAL PRIMARY KEY,
    post_id      VARCHAR NOT NULL,
    user_id      VARCHAR NOT NULL,
    username     VARCHAR(50) NOT NULL UNIQUE,
    content      VARCHAR(500) NOT NULL,
    likes        INTEGER NOT NULL DEFAULT 0,
    dislikes     INTEGER NOT NULL DEFAULT 0,
    edited_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

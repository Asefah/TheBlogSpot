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


CREATE TABLE post_reactions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    post_id UUID NOT NULL,
    comment_id UUID NOT NULL,
    reaction SMALLINT NOT NULL, -- 1 = like, -1 = dislike
    created_at TIMESTAMP DEFAULT now(),

    UNIQUE (user_id, post_id)
);


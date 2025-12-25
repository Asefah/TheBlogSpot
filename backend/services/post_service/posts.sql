CREATE TYPE post_category AS ENUM (
    'Lifestyle',
    'Food',
    'Travel',
    'Finance',
    'Technology',
    'Business',
    'Health and Fitness',
    'Other'
);


CREATE TABLE IF NOT EXISTS posts (
    post_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      VARCHAR NOT NULL,
    username     VARCHAR(50) NOT NULL UNIQUE,
    title        VARCHAR(200) NOT NULL,
    category     post_category NOT NULL DEFAULT 'Other',
    content      VARCHAR(5000) NOT NULL,
    likes        INTEGER NOT NULL DEFAULT 0,
    dislikes     INTEGER NOT NULL DEFAULT 0,
    edited_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

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

CREATE TYPE reaction_type AS ENUM (
    'insightful',
    'funny',
    'mind_blowing',
    'useful',
    'love',
    'hate',
    'dislike'
);


CREATE TABLE IF NOT EXISTS posts (
    post_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id    UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title        VARCHAR(300) NOT NULL,
    slug         VARCHAR(300) NOT NULL UNIQUE,
    category     post_category NOT NULL DEFAULT 'Other',
    content      TEXT NOT NULL,
    published    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP NOT NULL DEFAULT NOW(),
);

CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(published, created_at DESC);



-- POST REACTIONS TABLE
CREATE TABLE IF NOT EXISTS post_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    post_id     UUID NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    reaction    reaction_type NOT NULL,
    created_at  TIMESTAMP DEFAULT now(),

    UNIQUE (user_id, post_id)
);


CREATE INDEX IF NOT EXISTS idx_post_reactions_post ON post_reactions(post_id);

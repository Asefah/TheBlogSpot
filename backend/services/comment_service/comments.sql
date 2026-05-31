CREATE TABLE IF NOT EXISTS comments (
    comment_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id             UUID NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    author_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parent_comment_id   UUID REFERENCES comments(comment_id) ON DELETE CASCADE,
    content             TEXT NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    edited_at           TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_id);

--COMMENT REACTIONS
CREATE TABLE comment_reactions (
    reaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id  UUID NOT NULL REFERENCES comments(comment_id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    reaction    SMALLINT NOT NULL CHECK (reaction IN (1, -1)),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (comment_id, user_id)
);
 
CREATE INDEX IF NOT EXISTS idx_comment_reactions_comment ON comment_reactions(comment_id);


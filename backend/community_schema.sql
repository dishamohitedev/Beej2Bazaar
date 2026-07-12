-- ============================================================
-- Beej2Bazaar — Community Feed Schema Migration
-- Feature: Farmer Community Feed (Twitter/X Style)
-- Run this script in your Supabase SQL editor.
-- ============================================================


-- ============================================================
-- Table 1: community_posts
-- ============================================================
-- Stores all farmer-authored and system-generated posts.
-- post_type enforces strong typing (mirrors the PostType enum in models.py).
-- district / village / latitude / longitude enable nearby feed filtering
-- and proximity-based ranking in the RankingEngine.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.community_posts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,                  -- Author's user UUID (or SYSTEM_USER_ID for bot posts)
    author_name VARCHAR(100) NOT NULL,           -- Denormalised for fast reads without profile join
    post_type   VARCHAR(30) NOT NULL,            -- PostType enum: QUESTION, UPDATE, DISEASE, ALERT, ADVISORY, MARKET, TIP, SUCCESS_STORY
    title       VARCHAR(200),                    -- Optional short headline (Twitter-style)
    content     TEXT NOT NULL,                   -- Post body (max 500 chars enforced at app layer)
    image_url   TEXT,                            -- Optional image (disease photo, etc.)
    crop_id     UUID,                            -- Optional crop linkage
    district    VARCHAR(100),                    -- For nearby feed filtering & proximity ranking
    village     VARCHAR(100),                    -- Additional geo context
    latitude    NUMERIC(9,6),                    -- Reserved for haversine distance (future)
    longitude   NUMERIC(9,6),                    -- Reserved for haversine distance (future)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Enforce allowed post types at DB level (mirrors PostType enum)
    CONSTRAINT chk_post_type CHECK (
        post_type IN ('QUESTION','UPDATE','DISEASE','ALERT','ADVISORY','MARKET','TIP','SUCCESS_STORY')
    )
);

-- Index for category/type filtering (used by get_all with post_types filter)
CREATE INDEX IF NOT EXISTS idx_community_posts_post_type
    ON public.community_posts(post_type);

-- Index for district-based nearby feed queries
CREATE INDEX IF NOT EXISTS idx_community_posts_district
    ON public.community_posts(district);

-- Index for author's post history
CREATE INDEX IF NOT EXISTS idx_community_posts_user_id
    ON public.community_posts(user_id);

-- Index for time-ordered feed retrieval
CREATE INDEX IF NOT EXISTS idx_community_posts_created_at
    ON public.community_posts(created_at DESC);

-- RLS: Enable Row Level Security
ALTER TABLE public.community_posts ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Any authenticated user can read all posts
CREATE POLICY "community_posts_select"
    ON public.community_posts FOR SELECT
    TO authenticated
    USING (true);

-- RLS Policy: Authenticated users can insert their own posts
CREATE POLICY "community_posts_insert"
    ON public.community_posts FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = user_id::text);

-- RLS Policy: Users can only delete their own posts
CREATE POLICY "community_posts_delete"
    ON public.community_posts FOR DELETE
    TO authenticated
    USING (auth.uid()::text = user_id::text);

-- Allow service role (backend) to bypass RLS (for system posts)
-- This is automatically handled by using the SERVICE_ROLE key in admin_supabase.


-- ============================================================
-- Table 2: community_comments
-- ============================================================
-- Comments on community posts.
-- Ordered oldest-first for thread readability.
-- Cascades on post deletion.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.community_comments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id     UUID NOT NULL REFERENCES public.community_posts(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL,
    author_name VARCHAR(100) NOT NULL,   -- Denormalised for fast reads
    comment     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fetching all comments for a post (most common query)
CREATE INDEX IF NOT EXISTS idx_community_comments_post_id
    ON public.community_comments(post_id);

-- RLS
ALTER TABLE public.community_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "community_comments_select"
    ON public.community_comments FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "community_comments_insert"
    ON public.community_comments FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "community_comments_delete"
    ON public.community_comments FOR DELETE
    TO authenticated
    USING (auth.uid()::text = user_id::text);


-- ============================================================
-- Table 3: post_likes
-- ============================================================
-- Like relationship between users and posts.
-- UNIQUE(post_id, user_id) prevents duplicate likes at DB level.
-- This is the source of truth — likes_count is always computed
-- from this table, never cached in community_posts.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.post_likes (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id    UUID NOT NULL REFERENCES public.community_posts(id) ON DELETE CASCADE,
    user_id    UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Database-enforced uniqueness: one like per user per post
    CONSTRAINT unique_user_post_like UNIQUE (post_id, user_id)
);

-- Index for batch like counting (count_for_posts query)
CREATE INDEX IF NOT EXISTS idx_post_likes_post_id
    ON public.post_likes(post_id);

-- Index for checking if a user liked specific posts (liked_post_ids_for_user query)
CREATE INDEX IF NOT EXISTS idx_post_likes_user_id_post_id
    ON public.post_likes(user_id, post_id);

-- RLS
ALTER TABLE public.post_likes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "post_likes_select"
    ON public.post_likes FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "post_likes_insert"
    ON public.post_likes FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "post_likes_delete"
    ON public.post_likes FOR DELETE
    TO authenticated
    USING (auth.uid()::text = user_id::text);

"""
Feed Service
============
Read-side facade over the FeedEngine.

Responsibilities:
  - Fetch viewer profile and pass it to FeedEngine
  - Provide clean public methods that map to future API endpoints
  - Keep FeedEngine isolated from profile concerns

This service is intentionally thin — all feed assembly logic
lives in FeedEngine and RankingEngine.
"""

from __future__ import annotations

import logging

from app.community.feed_engine import FeedEngine
from app.community.models import Comment, FeedFilters, FeedPage, PostDetail
from app.community.ranking_engine import RankingEngine
from app.community.repositories.comment_repository import CommentRepository
from app.community.repositories.post_repository import PostRepository
from app.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class FeedService:
    """
    Public read-side API for the community feed.

    Constructor creates FeedEngine with a RankingEngine.
    For testing, inject a FeedEngine with a mock RankingEngine:
        FeedService(engine=FeedEngine(MockRankingEngine()))
    """

    def __init__(self, engine: FeedEngine | None = None) -> None:
        self.engine = engine or FeedEngine(RankingEngine())

    # -----------------------------------------------------------------------
    # Feed Methods
    # -----------------------------------------------------------------------

    def get_feed(self, viewer_id: str, filters: FeedFilters) -> FeedPage:
        """
        Returns the ranked, paginated community feed for a viewer.

        The viewer's profile (district, lat/lon) is fetched here and passed
        to the engine for proximity scoring.

        Args:
            viewer_id:  Authenticated farmer's UUID.
            filters:    FeedFilters (category, nearby_only, page, page_size).
        Returns:
            FeedPage with ranked posts.
        """
        logger.info(
            "FeedService.get_feed: viewer=%s category=%s nearby=%s page=%d",
            viewer_id, filters.category, filters.nearby_only, filters.page
        )

        # Fetch viewer profile for location-based proximity scoring
        viewer_profile = ProfileRepository.get_by_id(viewer_id)

        return self.engine.build_feed(
            viewer_id      = viewer_id,
            viewer_profile = viewer_profile or {},
            filters        = filters,
        )

    def get_nearby_feed(self, viewer_id: str, filters: FeedFilters) -> FeedPage:
        """
        Returns the nearby feed — same as get_feed but forces nearby_only=True.
        Convenience method that will map to GET /community/feed/nearby.

        Args:
            viewer_id:  Authenticated farmer's UUID.
            filters:    FeedFilters (nearby_only will be overridden to True).
        Returns:
            FeedPage of nearby posts, ranked.
        """
        filters = filters.model_copy(update={"nearby_only": True})
        return self.get_feed(viewer_id=viewer_id, filters=filters)

    def get_post_detail(self, post_id: str, viewer_id: str) -> PostDetail:
        """
        Returns a single post with its full comment thread.
        Maps to GET /community/post/{id}.

        Args:
            post_id:    UUID of the post.
            viewer_id:  Viewing farmer's UUID (used for is_liked_by_me).
        Returns:
            PostDetail with the FeedPost and all comments.
        Raises:
            ValueError if the post is not found.
        """
        raw = PostRepository.get_by_id(post_id)
        if not raw:
            raise ValueError(f"Post {post_id} not found.")

        from datetime import datetime, timezone
        from app.community.models import FeedPost, PostType
        from app.community.repositories.like_repository import LikeRepository

        # Hydrate counts
        likes_count    = LikeRepository.count_for_post(post_id)
        comments_count = CommentRepository.count_for_post(post_id)
        is_liked       = LikeRepository.has_liked(post_id=post_id, user_id=viewer_id)

        created_at_raw = raw.get("created_at", "")
        if isinstance(created_at_raw, str):
            try:
                created_at = datetime.fromisoformat(created_at_raw)
            except ValueError:
                created_at = datetime.now(tz=timezone.utc)
        else:
            created_at = created_at_raw or datetime.now(tz=timezone.utc)

        # Build viewer profile for ranking the single post (for rank_score display)
        viewer_profile = ProfileRepository.get_by_id(viewer_id) or {}
        from app.community.feed_engine import FeedEngine as _FE
        feed_post = _FE._map_to_feed_post(
            raw      = raw,
            likes    = likes_count,
            comments = comments_count,
            is_liked = is_liked,
        )

        # Apply rank_score even to single post detail
        from app.community.ranking_engine import RankingEngine as _RE
        ranked = _RE().rank(
            [feed_post],
            viewer_district = viewer_profile.get("district"),
        )
        feed_post = ranked[0] if ranked else feed_post

        # Fetch and map comments
        raw_comments = CommentRepository.get_for_post(post_id)
        comments = [
            Comment(
                id          = c["id"],
                post_id     = c["post_id"],
                user_id     = c["user_id"],
                author_name = c.get("author_name", "Farmer"),
                comment     = c["comment"],
                created_at  = datetime.fromisoformat(c["created_at"])
                               if isinstance(c.get("created_at"), str)
                               else c.get("created_at", datetime.now(tz=timezone.utc)),
            )
            for c in raw_comments
        ]

        logger.info(
            "FeedService.get_post_detail: post=%s viewer=%s likes=%d comments=%d",
            post_id, viewer_id, likes_count, len(comments)
        )

        return PostDetail(post=feed_post, comments=comments)

"""
Community Feed — Feed Engine
=============================
Orchestrates the full feed assembly pipeline:

    1. Fetch raw post rows from PostRepository
    2. Batch-enrich with like counts  (LikeRepository.count_for_posts)
    3. Batch-enrich with comment counts (CommentRepository.count_for_posts)
    4. Inject is_liked_by_me per post  (LikeRepository.liked_post_ids_for_user)
    5. Map raw dicts → FeedPost domain objects
    6. Pass to RankingEngine.rank()
    7. Apply pagination and return FeedPage

All DB round-trips are batched (3 total for the entire feed page),
avoiding N+1 query anti-patterns.

The FeedEngine is constructed with a RankingEngine dependency —
this follows Dependency Inversion (SOLID-D) and makes unit testing
trivial by injecting a mock RankingEngine.
"""

from __future__ import annotations

import logging
from datetime import datetime

from app.community.models import (
    CATEGORY_TO_POST_TYPES,
    FeedCategory,
    FeedFilters,
    FeedPage,
    FeedPost,
    PostType,
)
from app.community.ranking_engine import RankingEngine
from app.community.repositories.comment_repository import CommentRepository
from app.community.repositories.like_repository import LikeRepository
from app.community.repositories.post_repository import PostRepository

logger = logging.getLogger(__name__)


class FeedEngine:
    """
    Assembles the ranked, paginated community feed.

    Constructor Args:
        ranking_engine: Injected RankingEngine instance.
                        Swap for a mock in tests.
    """

    def __init__(self, ranking_engine: RankingEngine) -> None:
        self.ranking_engine = ranking_engine

    # -----------------------------------------------------------------------
    # Public Method
    # -----------------------------------------------------------------------

    def build_feed(
        self,
        viewer_id: str,
        viewer_profile: dict,
        filters: FeedFilters,
    ) -> FeedPage:
        """
        Runs the complete feed assembly pipeline.

        Args:
            viewer_id:       UUID of the farmer viewing the feed.
            viewer_profile:  Profile dict (needs district, latitude, longitude).
            filters:         Category, nearby_only, page, page_size.
        Returns:
            FeedPage with ranked, paginated posts.
        """
        viewer_district = viewer_profile.get("district") if viewer_profile else None
        viewer_lat      = viewer_profile.get("latitude")  if viewer_profile else None
        viewer_lon      = viewer_profile.get("longitude") if viewer_profile else None

        # Step 1 — Resolve post_type filter from FeedCategory
        post_types = self._resolve_post_types(filters.category)

        # Step 2 — Fetch raw posts from DB
        raw_posts = self._fetch_raw_posts(filters, post_types, viewer_district)
        logger.info("FeedEngine: fetched %d raw posts for viewer %s", len(raw_posts), viewer_id)

        if not raw_posts:
            return FeedPage(posts=[], page=filters.page, page_size=filters.page_size, total_count=0)

        # Step 3 — Batch-enrich engagement counts (2 DB queries total)
        post_ids     = [p["id"] for p in raw_posts]
        like_counts  = LikeRepository.count_for_posts(post_ids)
        comment_counts = CommentRepository.count_for_posts(post_ids)

        # Step 4 — Identify which posts the viewer has liked (1 DB query)
        liked_by_viewer = LikeRepository.liked_post_ids_for_user(viewer_id, post_ids)

        # Step 5 — Map raw dicts → FeedPost domain objects
        feed_posts = [
            self._map_to_feed_post(
                raw     = row,
                likes   = like_counts.get(row["id"], 0),
                comments= comment_counts.get(row["id"], 0),
                is_liked= row["id"] in liked_by_viewer,
            )
            for row in raw_posts
        ]

        # Step 6 — Rank posts
        ranked = self.ranking_engine.rank(
            posts           = feed_posts,
            viewer_district = viewer_district,
            viewer_lat      = viewer_lat,
            viewer_lon      = viewer_lon,
        )

        # Step 7 — Paginate
        total_count = len(ranked)
        start = (filters.page - 1) * filters.page_size
        end   = start + filters.page_size
        page_posts = ranked[start:end]

        logger.info(
            "FeedEngine: returning page %d/%d (%d posts) of %d total",
            filters.page,
            -(-total_count // filters.page_size),  # ceiling division
            len(page_posts),
            total_count,
        )

        return FeedPage(
            posts       = page_posts,
            page        = filters.page,
            page_size   = filters.page_size,
            total_count = total_count,
        )

    # -----------------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------------

    def _resolve_post_types(self, category: FeedCategory) -> list[str] | None:
        """
        Maps a FeedCategory to the list of PostType string values
        to filter by. Returns None for ALL (no filter applied).
        """
        types = CATEGORY_TO_POST_TYPES.get(category, list(PostType))
        if category == FeedCategory.ALL:
            return None  # No filter — fetch everything
        return [t.value for t in types]

    def _fetch_raw_posts(
        self,
        filters: FeedFilters,
        post_types: list[str] | None,
        viewer_district: str | None,
    ) -> list[dict]:
        """
        Dispatches to the correct repository method based on filters.
        """
        if filters.nearby_only and viewer_district:
            return PostRepository.get_by_district(
                district   = viewer_district,
                post_types = post_types,
            )
        return PostRepository.get_all(post_types=post_types)

    @staticmethod
    def _map_to_feed_post(
        raw:      dict,
        likes:    int,
        comments: int,
        is_liked: bool,
    ) -> FeedPost:
        """
        Converts a raw Supabase row dict into a typed FeedPost domain object.

        The created_at field from Supabase comes as an ISO-8601 string;
        we parse it here so the RankingEngine works with proper datetime objects.
        """
        created_at_raw = raw.get("created_at", "")
        if isinstance(created_at_raw, str):
            try:
                created_at = datetime.fromisoformat(created_at_raw)
            except ValueError:
                created_at = datetime.utcnow()
        else:
            created_at = created_at_raw

        return FeedPost(
            id             = raw["id"],
            user_id        = raw["user_id"],
            author_name    = raw.get("author_name", "Unknown Farmer"),
            post_type      = PostType(raw["post_type"]),
            title          = raw.get("title"),
            content        = raw.get("content", ""),
            image_url      = raw.get("image_url"),
            crop_id        = raw.get("crop_id"),
            district       = raw.get("district"),
            village        = raw.get("village"),
            latitude       = raw.get("latitude"),
            longitude      = raw.get("longitude"),
            likes_count    = likes,
            comments_count = comments,
            is_liked_by_me = is_liked,
            rank_score     = 0.0,   # injected by RankingEngine in next step
            created_at     = created_at,
        )

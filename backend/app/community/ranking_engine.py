"""
Community Feed — Ranking Engine
================================
Deterministic, configurable, AI-free feed ranking.

Design Principles:
- All weights and thresholds are class-level constants → easy to tune
  without changing logic.
- No randomness, no AI, no ML — purely mathematical with clear audit trail.
- Each scoring method is isolated (SRP) and independently testable.
- RankingEngine is Open/Closed: extend TYPE_PRIORITY or modifiers
  by changing configuration, not the algorithm.

Score Formula:
    rank_score = base_score + recency_bonus + proximity_bonus + engagement_bonus

Maximum theoretical score:  100 + 15 + 12 + 18 = 145
(ensures ADVISORY always outranks SUCCESS_STORY even at maximum engagement)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import ClassVar

from app.community.models import FeedPost, PostType

logger = logging.getLogger(__name__)


class RankingEngine:
    """
    Assigns a `rank_score` to each FeedPost and returns the list sorted
    by rank_score descending. Equal scores are broken by created_at DESC
    (newer post wins tie).

    Usage:
        engine = RankingEngine()
        ranked_posts = engine.rank(posts, viewer_district="Pune",
                                   viewer_lat=18.5, viewer_lon=73.8)
    """

    # -----------------------------------------------------------------------
    # Configuration — Tier 1: Post Type Base Scores (0–100)
    # Edit these values to reconfigure priority without touching logic.
    # -----------------------------------------------------------------------
    TYPE_PRIORITY: ClassVar[dict[PostType, float]] = {
        PostType.ADVISORY:      100.0,  # Government advisory — highest priority
        PostType.DISEASE:        90.0,  # Disease alert
        PostType.ALERT:          85.0,  # Weather / pest alert
        PostType.MARKET:         70.0,  # Mandi market update
        PostType.UPDATE:         60.0,  # General farm update
        PostType.QUESTION:       50.0,  # Farmer question
        PostType.TIP:            45.0,  # Farming tip
        PostType.SUCCESS_STORY:  40.0,  # Success story — lowest base
    }

    # -----------------------------------------------------------------------
    # Configuration — Tier 2: Recency Bonuses (hours → bonus points)
    # -----------------------------------------------------------------------
    RECENCY_BONUS_2H:  ClassVar[float] = 15.0
    RECENCY_BONUS_24H: ClassVar[float] =  8.0
    RECENCY_BONUS_7D:  ClassVar[float] =  2.0

    # -----------------------------------------------------------------------
    # Configuration — Tier 3: Proximity Bonuses
    # -----------------------------------------------------------------------
    PROXIMITY_SAME_DISTRICT: ClassVar[float] = 12.0
    PROXIMITY_SAME_STATE:    ClassVar[float] =  5.0  # reserved for future use

    # -----------------------------------------------------------------------
    # Configuration — Tier 4: Engagement Bonuses
    # -----------------------------------------------------------------------
    LIKE_BONUS_PER_LIKE:      ClassVar[float] = 0.5
    LIKE_BONUS_CAP:           ClassVar[float] = 10.0
    COMMENT_BONUS_PER_COMMENT: ClassVar[float] = 1.0
    COMMENT_BONUS_CAP:        ClassVar[float] =  8.0

    # -----------------------------------------------------------------------
    # Public Interface
    # -----------------------------------------------------------------------

    def rank(
        self,
        posts: list[FeedPost],
        viewer_district: str | None = None,
        viewer_lat: float | None = None,
        viewer_lon: float | None = None,
    ) -> list[FeedPost]:
        """
        Scores and sorts posts by rank_score descending.

        Args:
            posts: List of FeedPost objects (already enriched with likes/comments).
            viewer_district: The viewing farmer's district for proximity scoring.
            viewer_lat: Viewer latitude (reserved for future haversine use).
            viewer_lon: Viewer longitude (reserved for future haversine use).
        Returns:
            New list of FeedPost objects with rank_score filled, sorted
            by rank_score DESC, then created_at DESC as tiebreaker.
        """
        now = datetime.now(tz=timezone.utc)
        scored: list[FeedPost] = []

        for post in posts:
            score = self._compute_score(post, now, viewer_district)
            # Return a copy with rank_score injected (immutable model pattern)
            scored.append(post.model_copy(update={"rank_score": score}))

        # Sort: rank_score DESC, then created_at DESC (deterministic tiebreaker)
        scored.sort(
            key=lambda p: (-p.rank_score, -p.created_at.timestamp())
        )

        logger.debug(
            "RankingEngine: scored %d posts | viewer_district=%s",
            len(scored), viewer_district
        )
        return scored

    # -----------------------------------------------------------------------
    # Private Scoring Methods — each has single responsibility
    # -----------------------------------------------------------------------

    def _compute_score(
        self,
        post: FeedPost,
        now: datetime,
        viewer_district: str | None,
    ) -> float:
        """Aggregates all scoring components into a single rank_score."""
        base       = self._base_score(post.post_type)
        recency    = self._recency_bonus(post.created_at, now)
        proximity  = self._proximity_bonus(post.district, viewer_district)
        engagement = self._engagement_bonus(post.likes_count, post.comments_count)

        total = base + recency + proximity + engagement
        logger.debug(
            "Post %s [%s]: base=%.1f recency=%.1f proximity=%.1f engagement=%.1f → %.1f",
            post.id, post.post_type, base, recency, proximity, engagement, total
        )
        return round(total, 2)

    def _base_score(self, post_type: PostType) -> float:
        """
        Returns the priority base score for a post type.
        Unknown types default to the lowest score (SUCCESS_STORY level).
        """
        return self.TYPE_PRIORITY.get(post_type, 40.0)

    def _recency_bonus(self, created_at: datetime, now: datetime) -> float:
        """
        Awards bonus points based on how recent the post is.
        Ensures fresh content is surfaced, but doesn't override type priority.

        Thresholds:
            ≤ 2 hours  → +15
            ≤ 24 hours → +8
            ≤ 7 days   → +2
            > 7 days   → +0
        """
        # Normalise to UTC-aware datetime for comparison
        post_ts = created_at
        if post_ts.tzinfo is None:
            post_ts = post_ts.replace(tzinfo=timezone.utc)

        age_hours = (now - post_ts).total_seconds() / 3600

        if age_hours <= 2:
            return self.RECENCY_BONUS_2H
        if age_hours <= 24:
            return self.RECENCY_BONUS_24H
        if age_hours <= 168:   # 7 days
            return self.RECENCY_BONUS_7D
        return 0.0

    def _proximity_bonus(
        self,
        post_district: str | None,
        viewer_district: str | None,
    ) -> float:
        """
        Awards a bonus when the post originates from the viewer's district.
        Falls back to 0 if either district is unknown.

        Future improvement: use haversine distance on lat/lon for a
        graduated proximity score instead of a binary district match.
        """
        if not post_district or not viewer_district:
            return 0.0
        if post_district.strip().lower() == viewer_district.strip().lower():
            return self.PROXIMITY_SAME_DISTRICT
        return 0.0

    def _engagement_bonus(self, likes_count: int, comments_count: int) -> float:
        """
        Awards bonus points for post engagement (likes + comments).
        Both components are capped to prevent viral posts from
        drowning out authoritative but low-engagement advisories.

        Caps:
            Like bonus    → max +10  (at 20 likes)
            Comment bonus → max +8   (at 8 comments)
        """
        like_bonus    = min(likes_count    * self.LIKE_BONUS_PER_LIKE,     self.LIKE_BONUS_CAP)
        comment_bonus = min(comments_count * self.COMMENT_BONUS_PER_COMMENT, self.COMMENT_BONUS_CAP)
        return like_bonus + comment_bonus

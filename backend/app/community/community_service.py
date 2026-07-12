"""
Community Service
=================
The single public orchestrator for the entire Farmer Community Feed feature.

This is the ONLY class that external modules (routers, other services) should
import. It delegates all work to PostService and FeedService.

Integration Hooks:
  publish_disease_alert()   ← called by DiseaseService after detection
  publish_market_update()   ← called by market data pipeline
  publish_weather_alert()   ← called by weather monitoring service

All integration methods are fire-and-forget safe: they catch and log
all exceptions so the calling service is never impacted by a community
publishing failure.

Future AI integration points (Gemini):
  - Translation of posts         → add translate_post() here
  - Summarization of discussions → add summarize_thread() here
  - Toxicity / spam detection    → add moderate_post() hook in create_post()
  NOTE: Gemini must NEVER influence feed ranking or auto-generate posts.
"""

from __future__ import annotations

import logging

from app.community.feed_service import FeedService
from app.community.models import (
    Comment,
    CommentCreate,
    FeedFilters,
    FeedPage,
    FeedPost,
    LikeToggleResult,
    PostCreate,
    PostDetail,
    PostType,
)
from app.community.post_service import PostService

logger = logging.getLogger(__name__)


class CommunityService:
    """
    Facade over PostService and FeedService.

    Instantiate once and reuse (lightweight — no DB connections held):
        community = CommunityService()
    """

    def __init__(self) -> None:
        # FeedService holds FeedEngine + RankingEngine state
        self._feed_service = FeedService()
        # PostService methods are all @staticmethod — called directly on the class

    # -----------------------------------------------------------------------
    # Feed — Read Operations
    # -----------------------------------------------------------------------

    def get_feed(self, viewer_id: str, filters: FeedFilters) -> FeedPage:
        """
        Returns the ranked, paginated community feed.
        Maps to: GET /community/feed
        """
        return self._feed_service.get_feed(viewer_id=viewer_id, filters=filters)

    def get_nearby_feed(self, viewer_id: str, filters: FeedFilters) -> FeedPage:
        """
        Returns the nearby-only ranked feed (posts from viewer's district first).
        Maps to: GET /community/feed/nearby
        """
        return self._feed_service.get_nearby_feed(viewer_id=viewer_id, filters=filters)

    def get_post_detail(self, post_id: str, viewer_id: str) -> PostDetail:
        """
        Returns a single post with its full comment thread.
        Maps to: GET /community/post/{id}
        """
        return self._feed_service.get_post_detail(post_id=post_id, viewer_id=viewer_id)

    # -----------------------------------------------------------------------
    # Posts — Write Operations
    # -----------------------------------------------------------------------

    def create_post(self, user_id: str, data: PostCreate) -> FeedPost:
        """
        Creates a new farmer-authored community post.
        Maps to: POST /community/post
        """
        return PostService.create_post(user_id=user_id, data=data)  # @staticmethod

    def delete_post(self, user_id: str, post_id: str) -> None:
        """
        Deletes a farmer's own post.
        Maps to: DELETE /community/post/{id}
        """
        PostService.delete_post(user_id=user_id, post_id=post_id)  # @staticmethod

    def toggle_like(self, post_id: str, user_id: str) -> LikeToggleResult:
        """
        Likes or unlikes a post.
        Maps to: POST /community/post/{id}/like
        """
        return PostService.toggle_like(post_id=post_id, user_id=user_id)  # @staticmethod

    def add_comment(self, post_id: str, user_id: str, data: CommentCreate) -> "Comment":
        """
        Adds a comment to a post.
        Maps to: POST /community/post/{id}/comment
        """
        return PostService.add_comment(post_id=post_id, user_id=user_id, data=data)  # @staticmethod

    # -----------------------------------------------------------------------
    # System Integration Hooks
    # -----------------------------------------------------------------------
    # These methods are the ONLY sanctioned way for other modules to inject
    # content into the community feed. Gemini / AI is NEVER called here.
    # -----------------------------------------------------------------------

    def publish_disease_alert(
        self,
        disease_name: str,
        crop_name:    str,
        district:     str | None = None,
        image_url:    str | None = None,
        crop_id:      str | None = None,
        confidence:   float | None = None,
    ) -> FeedPost | None:
        """
        Publishes a disease alert post to the community feed.
        Called by DiseaseService after a confirmed detection.

        Example content:
            "⚠️ Disease Alert: Late Blight detected in Tomato crop.
             Confidence: 94%. Farmers in Pune district should inspect
             their crops immediately."

        Args:
            disease_name: e.g. "Late Blight"
            crop_name:    e.g. "Tomato"
            district:     Farmer's district for proximity ranking.
            image_url:    The disease detection image URL.
            crop_id:      UUID of the affected crop.
            confidence:   AI detection confidence (0–1 or 0–100).
        Returns:
            Created FeedPost or None if publishing failed.
        """
        confidence_pct = (
            f" Confidence: {round(confidence * 100)}%." if confidence is not None else ""
        )
        district_note = f" Farmers in {district} district should inspect their crops immediately." \
                        if district else ""

        content = (
            f"⚠️ Disease Alert: {disease_name} detected in {crop_name} crop."
            f"{confidence_pct}{district_note}"
        )
        title = f"🦠 {disease_name} in {crop_name}"

        logger.info(
            "CommunityService: publishing disease alert [%s / %s] for district=%s",
            disease_name, crop_name, district
        )
        return PostService.create_system_post(
            post_type = PostType.DISEASE,
            content   = content,
            title     = title,
            district  = district,
            image_url = image_url,
            crop_id   = crop_id,
        )

    def publish_market_update(
        self,
        commodity:  str,
        price:      float,
        market:     str,
        district:   str | None = None,
        unit:       str = "quintal",
    ) -> FeedPost | None:
        """
        Publishes a mandi market price update to the feed.
        Called by the market data pipeline after price collection.

        Example content:
            "📊 Mandi Update: Tomato price at Pune APMC is ₹1,240/quintal today."

        Args:
            commodity:  e.g. "Tomato"
            price:      Modal price (INR).
            market:     Mandi/market name.
            district:   District for proximity ranking.
            unit:       Price unit (default: quintal).
        Returns:
            Created FeedPost or None if publishing failed.
        """
        content = (
            f"📊 Mandi Update: {commodity} price at {market} is "
            f"₹{price:,.0f}/{unit} today."
        )
        title = f"📈 {commodity} — ₹{price:,.0f}/{unit}"

        logger.info(
            "CommunityService: publishing market update [%s @ %s] district=%s",
            commodity, market, district
        )
        return PostService.create_system_post(
            post_type = PostType.MARKET,
            content   = content,
            title     = title,
            district  = district,
        )

    def publish_weather_alert(
        self,
        description: str,
        district:    str | None = None,
        severity:    str = "Moderate",
    ) -> FeedPost | None:
        """
        Publishes a weather alert to the community feed.
        Called by the weather monitoring service.

        Example content:
            "🌩️ Weather Alert: Heavy rainfall expected in Pune district.
             Severity: High. Delay irrigation activities for the next 48 hours."

        Args:
            description: Weather event description.
            district:    Target district.
            severity:    "Low" | "Moderate" | "High" | "Extreme".
        Returns:
            Created FeedPost or None if publishing failed.
        """
        district_note = f" in {district} district" if district else ""
        content = (
            f"🌩️ Weather Alert{district_note}: {description} "
            f"Severity: {severity}."
        )
        title = f"⛈️ Weather Alert — {district or 'All Districts'}"

        logger.info(
            "CommunityService: publishing weather alert district=%s severity=%s",
            district, severity
        )
        return PostService.create_system_post(
            post_type = PostType.ALERT,
            content   = content,
            title     = title,
            district  = district,
        )

    def publish_government_advisory(
        self,
        title:    str,
        content:  str,
        district: str | None = None,
    ) -> FeedPost | None:
        """
        Publishes a government/official advisory.
        Can be called by any integration that receives official advisories.

        Args:
            title:    Short headline for the advisory.
            content:  Full advisory text (keep under 500 chars for feed style).
            district: Target district (None = national advisory).
        Returns:
            Created FeedPost or None if publishing failed.
        """
        logger.info(
            "CommunityService: publishing government advisory district=%s", district
        )
        return PostService.create_system_post(
            post_type = PostType.ADVISORY,
            content   = content,
            title     = title,
            district  = district,
        )

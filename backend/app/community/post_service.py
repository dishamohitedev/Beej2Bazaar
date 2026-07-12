"""
Post Service
============
Handles all write-side operations for community posts:
  - Creating farmer posts
  - Creating system-generated posts (disease alerts, market updates, weather)
  - Deleting posts
  - Toggling likes
  - Adding comments

All business logic lives here; repositories only touch the DB.

Integration Hook:
  `create_system_post()` is a fire-and-forget entry point called by other
  feature modules (DiseaseService, WeatherService, MarketService).
  It must never raise to the calling service — all exceptions are swallowed
  and logged.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import HTTPException

from app.community.models import (
    Comment,
    CommentCreate,
    FeedPost,
    LikeToggleResult,
    PostCreate,
    PostType,
)
from app.community.repositories.comment_repository import CommentRepository
from app.community.repositories.like_repository import LikeRepository
from app.community.repositories.post_repository import PostRepository
from app.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# System actor — posts created by automated modules use this sentinel ID.
# This must exist as a user in your Supabase auth.users table, or you can
# use a special UUID and handle it at the display layer.
# -------------------------------------------------------------------------
SYSTEM_USER_ID   = "00000000-0000-0000-0000-000000000000"
SYSTEM_AUTHOR_NAME = "🌾 Beej2Bazaar System"


class PostService:
    """
    Write-side operations for community posts.
    Depends on:
      - PostRepository (community_posts table)
      - CommentRepository (community_comments table)
      - LikeRepository (post_likes table)
      - ProfileRepository (to get author name and geo-data)
    """

    # -----------------------------------------------------------------------
    # Post Creation
    # -----------------------------------------------------------------------

    @staticmethod
    def create_post(user_id: str, data: PostCreate) -> FeedPost:
        """
        Creates a new farmer-authored post.

        Enriches the post with the author's name and geo-location
        from their profile so the feed can surface nearby posts.

        Args:
            user_id: Authenticated farmer's UUID.
            data:    Validated PostCreate payload.
        Returns:
            The created FeedPost domain object.
        Raises:
            HTTPException(404) if the user profile is not found.
        """
        # Fetch author profile for name + location enrichment
        profile = ProfileRepository.get_by_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")

        author_name = profile.get("full_name") or "Farmer"

        payload = {
            "user_id":     user_id,
            "author_name": author_name,
            "post_type":   data.post_type.value,
            "content":     data.content,
            "title":       data.title,
            "image_url":   data.image_url,
            "crop_id":     data.crop_id,
            # Enrich with location from profile
            "district":    profile.get("district"),
            "village":     profile.get("village"),
            "latitude":    profile.get("latitude"),
            "longitude":   profile.get("longitude"),
        }

        row = PostRepository.create(payload)
        logger.info("PostService: farmer %s created post %s [%s]", user_id, row["id"], data.post_type)
        return PostService._row_to_feed_post(row)

    @staticmethod
    def create_system_post(
        post_type:   PostType,
        content:     str,
        title:       str | None    = None,
        district:    str | None    = None,
        image_url:   str | None    = None,
        crop_id:     str | None    = None,
    ) -> FeedPost | None:
        """
        Creates a system-generated post (disease alert, weather alert,
        market update, government advisory).

        This method MUST be called in a fire-and-forget try/except block
        by the calling service — it must never propagate exceptions.

        Args:
            post_type:  Must be DISEASE, ALERT, ADVISORY, or MARKET.
            content:    The post body text.
            title:      Optional short headline.
            district:   Target district for proximity ranking (can be None for national).
            image_url:  Optional image (e.g. disease detection photo).
            crop_id:    Optional linked crop UUID.
        Returns:
            The created FeedPost, or None if creation failed.
        """
        try:
            payload = {
                "user_id":     SYSTEM_USER_ID,
                "author_name": SYSTEM_AUTHOR_NAME,
                "post_type":   post_type.value,
                "content":     content,
                "title":       title,
                "image_url":   image_url,
                "crop_id":     crop_id,
                "district":    district,
                "village":     None,
                "latitude":    None,
                "longitude":   None,
            }
            row = PostRepository.create(payload)
            logger.info(
                "PostService: system post created: %s [%s] district=%s",
                row["id"], post_type, district
            )
            return PostService._row_to_feed_post(row)
        except Exception as exc:
            # Never crash the calling service
            logger.error("PostService.create_system_post failed: %s", exc, exc_info=True)
            return None

    # -----------------------------------------------------------------------
    # Post Deletion
    # -----------------------------------------------------------------------

    @staticmethod
    def delete_post(user_id: str, post_id: str) -> None:
        """
        Deletes a post. Ownership is enforced — farmers can only
        delete their own posts.

        Args:
            user_id:  The requesting farmer's UUID.
            post_id:  The post to delete.
        Raises:
            HTTPException(404) if the post doesn't exist or doesn't
            belong to this farmer.
        """
        deleted = PostRepository.delete(post_id=post_id, user_id=user_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Post not found or you do not have permission to delete it."
            )
        logger.info("PostService: user %s deleted post %s", user_id, post_id)

    # -----------------------------------------------------------------------
    # Like / Unlike
    # -----------------------------------------------------------------------

    @staticmethod
    def toggle_like(post_id: str, user_id: str) -> LikeToggleResult:
        """
        Toggles a like on a post (like if not liked, unlike if already liked).

        Args:
            post_id: The post to like/unlike.
            user_id: The farmer performing the action.
        Returns:
            LikeToggleResult with updated like count and liked state.
        Raises:
            HTTPException(404) if the post does not exist.
        """
        # Ensure post exists
        post = PostRepository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")

        already_liked = LikeRepository.has_liked(post_id=post_id, user_id=user_id)

        if already_liked:
            LikeRepository.remove(post_id=post_id, user_id=user_id)
            liked = False
            logger.debug("PostService: user %s unliked post %s", user_id, post_id)
        else:
            LikeRepository.add(post_id=post_id, user_id=user_id)
            liked = True
            logger.debug("PostService: user %s liked post %s", user_id, post_id)

        # Fetch updated count
        new_count = LikeRepository.count_for_post(post_id)
        return LikeToggleResult(post_id=post_id, liked=liked, likes_count=new_count)

    # -----------------------------------------------------------------------
    # Comments
    # -----------------------------------------------------------------------

    @staticmethod
    def add_comment(post_id: str, user_id: str, data: CommentCreate) -> Comment:
        """
        Adds a comment to a post.

        Args:
            post_id:  The post being commented on.
            user_id:  The commenting farmer's UUID.
            data:     Validated CommentCreate payload.
        Returns:
            The created Comment domain object.
        Raises:
            HTTPException(404) if the post does not exist.
        """
        # Ensure post exists
        post = PostRepository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")

        # Get commenter's name
        profile = ProfileRepository.get_by_id(user_id)
        author_name = (profile.get("full_name") if profile else None) or "Farmer"

        payload = {
            "post_id":     post_id,
            "user_id":     user_id,
            "author_name": author_name,
            "comment":     data.comment,
        }
        row = CommentRepository.add(payload)
        logger.info("PostService: user %s commented on post %s", user_id, post_id)

        # Map raw row to typed Comment domain object
        created_at_raw = row.get("created_at", "")
        if isinstance(created_at_raw, str):
            try:
                from datetime import datetime, timezone
                created_at = datetime.fromisoformat(created_at_raw)
            except ValueError:
                from datetime import datetime, timezone
                created_at = datetime.now(tz=timezone.utc)
        else:
            from datetime import datetime, timezone
            created_at = created_at_raw or datetime.now(tz=timezone.utc)

        return Comment(
            id          = row["id"],
            post_id     = row["post_id"],
            user_id     = row["user_id"],
            author_name = row.get("author_name", "Farmer"),
            comment     = row["comment"],
            created_at  = created_at,
        )

    # -----------------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _row_to_feed_post(row: dict) -> FeedPost:
        """
        Converts a raw Supabase row into a minimal FeedPost.
        Engagement counts are 0 at creation time — FeedEngine enriches
        these at read time.
        """
        created_at_raw = row.get("created_at", "")
        if isinstance(created_at_raw, str):
            try:
                created_at = datetime.fromisoformat(created_at_raw)
            except ValueError:
                created_at = datetime.now(tz=timezone.utc)
        else:
            created_at = created_at_raw or datetime.now(tz=timezone.utc)

        return FeedPost(
            id             = row["id"],
            user_id        = row["user_id"],
            author_name    = row.get("author_name", "Farmer"),
            post_type      = PostType(row["post_type"]),
            title          = row.get("title"),
            content        = row.get("content", ""),
            image_url      = row.get("image_url"),
            crop_id        = row.get("crop_id"),
            district       = row.get("district"),
            village        = row.get("village"),
            latitude       = row.get("latitude"),
            longitude      = row.get("longitude"),
            likes_count    = 0,
            comments_count = 0,
            is_liked_by_me = False,
            rank_score     = 0.0,
            created_at     = created_at,
        )

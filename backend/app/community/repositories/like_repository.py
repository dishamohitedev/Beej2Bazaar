"""
Like Repository
===============
Single responsibility: all database operations on the `post_likes` table.

The `post_likes` table has a UNIQUE(post_id, user_id) constraint so
duplicate likes are rejected at the database level.
"""

from __future__ import annotations

import logging

from app.database.supabase import admin_supabase

logger = logging.getLogger(__name__)

TABLE = "post_likes"


class LikeRepository:
    """
    Data access layer for post_likes.
    """

    @staticmethod
    def add(post_id: str, user_id: str) -> dict:
        """
        Inserts a like record.
        The DB UNIQUE constraint prevents duplicates.

        Args:
            post_id: The post being liked.
            user_id: The user liking the post.
        Returns:
            The created like row.
        Raises:
            Exception if the like already exists (duplicate key violation).
        """
        response = (
            admin_supabase
            .table(TABLE)
            .insert({"post_id": post_id, "user_id": user_id})
            .execute()
        )
        return response.data[0]

    @staticmethod
    def remove(post_id: str, user_id: str) -> bool:
        """
        Removes a like record.

        Args:
            post_id: The post to unlike.
            user_id: The user unliking the post.
        Returns:
            True if a row was removed, False if the like did not exist.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .delete()
            .eq("post_id", post_id)
            .eq("user_id", user_id)
            .execute()
        )
        return len(response.data) > 0

    @staticmethod
    def has_liked(post_id: str, user_id: str) -> bool:
        """
        Checks whether a user has already liked a post.

        Args:
            post_id: The post to check.
            user_id: The user to check.
        Returns:
            True if the user has liked this post, False otherwise.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .select("id")
            .eq("post_id", post_id)
            .eq("user_id", user_id)
            .execute()
        )
        return len(response.data) > 0

    @staticmethod
    def count_for_post(post_id: str) -> int:
        """
        Returns the total like count for a single post.

        Args:
            post_id: The post UUID.
        Returns:
            Integer like count.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .select("id", count="exact")
            .eq("post_id", post_id)
            .execute()
        )
        return response.count or 0

    @staticmethod
    def count_for_posts(post_ids: list[str]) -> dict[str, int]:
        """
        Batch-fetches like counts for multiple posts in a single query.
        Avoids N+1 queries in the FeedEngine enrichment step.

        Args:
            post_ids: List of post UUIDs.
        Returns:
            Dict mapping post_id -> like count.
        """
        if not post_ids:
            return {}

        response = (
            admin_supabase
            .table(TABLE)
            .select("post_id")
            .in_("post_id", post_ids)
            .execute()
        )

        counts: dict[str, int] = {}
        for row in (response.data or []):
            pid = row["post_id"]
            counts[pid] = counts.get(pid, 0) + 1

        return counts

    @staticmethod
    def liked_post_ids_for_user(user_id: str, post_ids: list[str]) -> set[str]:
        """
        Returns the subset of post_ids that a specific user has liked.
        Used by FeedEngine to inject `is_liked_by_me` efficiently.

        Args:
            user_id: The viewing user.
            post_ids: The list of post IDs visible in the current feed page.
        Returns:
            Set of post_ids liked by this user.
        """
        if not post_ids:
            return set()

        response = (
            admin_supabase
            .table(TABLE)
            .select("post_id")
            .eq("user_id", user_id)
            .in_("post_id", post_ids)
            .execute()
        )
        return {row["post_id"] for row in (response.data or [])}

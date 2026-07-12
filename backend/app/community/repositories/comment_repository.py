"""
Comment Repository
==================
Single responsibility: all database operations on the `community_comments` table.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.database.supabase import admin_supabase

logger = logging.getLogger(__name__)

TABLE = "community_comments"


class CommentRepository:
    """
    Data access layer for community_comments.
    """

    @staticmethod
    def add(data: dict) -> dict:
        """
        Inserts a new comment.

        Args:
            data: Dict with post_id, user_id, author_name, comment.
        Returns:
            The created comment row.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .insert(data)
            .execute()
        )
        return response.data[0]

    @staticmethod
    def get_for_post(post_id: str, limit: int = 100) -> list[dict]:
        """
        Fetches all comments for a given post, oldest first.
        Oldest-first ordering (ASC) matches the Twitter-style thread view.

        Args:
            post_id: The parent post's UUID.
            limit: Row cap.
        Returns:
            List of comment dicts ordered by created_at ASC.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .select("*")
            .eq("post_id", post_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return response.data or []

    @staticmethod
    def count_for_post(post_id: str) -> int:
        """
        Returns the total number of comments for a post.
        Used by FeedEngine to enrich FeedPost.comments_count.

        Args:
            post_id: The parent post's UUID.
        Returns:
            Integer comment count.
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
        Batch-fetches comment counts for multiple posts in a single query.
        Much more efficient than calling count_for_post() in a loop.

        Args:
            post_ids: List of post UUIDs.
        Returns:
            Dict mapping post_id -> comment count.
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

        # Aggregate counts from the flat list of rows
        counts: dict[str, int] = {}
        for row in (response.data or []):
            pid = row["post_id"]
            counts[pid] = counts.get(pid, 0) + 1

        return counts

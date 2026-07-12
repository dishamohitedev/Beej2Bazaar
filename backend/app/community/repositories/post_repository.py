"""
Post Repository
===============
Single responsibility: all database operations on the `community_posts` table.
No business logic here — just clean, typed data access methods.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.database.supabase import admin_supabase

logger = logging.getLogger(__name__)

TABLE = "community_posts"


class PostRepository:
    """
    Data access layer for community_posts.
    All methods are static — no state is held at the instance level.
    """

    @staticmethod
    def create(data: dict) -> dict:
        """
        Inserts a new post record.

        Args:
            data: Dict containing all required post fields.
        Returns:
            The created post row as a dict.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .insert(data)
            .execute()
        )
        return response.data[0]

    @staticmethod
    def get_by_id(post_id: str) -> Optional[dict]:
        """
        Fetches a single post by its primary key.

        Returns:
            The post dict or None if not found.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .select("*")
            .eq("id", post_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None

    @staticmethod
    def get_all(post_types: Optional[list[str]] = None, limit: int = 200) -> list[dict]:
        """
        Fetches all posts, optionally filtered by a list of post_type values.
        Returns raw rows — no ranking applied here.

        The FeedEngine is responsible for ranking and pagination.

        Args:
            post_types: Optional list of PostType string values to filter by.
            limit: Hard upper cap on rows fetched (prevents runaway queries).
        Returns:
            List of post dicts ordered by created_at DESC.
        """
        query = (
            admin_supabase
            .table(TABLE)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
        )
        if post_types:
            query = query.in_("post_type", post_types)

        response = query.execute()
        return response.data or []

    @staticmethod
    def get_by_district(district: str, post_types: Optional[list[str]] = None, limit: int = 100) -> list[dict]:
        """
        Fetches posts from a specific district.
        Used to build the nearby feed.

        Args:
            district: The viewer's district string.
            post_types: Optional type filter.
            limit: Row cap.
        Returns:
            List of post dicts ordered by created_at DESC.
        """
        query = (
            admin_supabase
            .table(TABLE)
            .select("*")
            .eq("district", district)
            .order("created_at", desc=True)
            .limit(limit)
        )
        if post_types:
            query = query.in_("post_type", post_types)

        response = query.execute()
        return response.data or []

    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> list[dict]:
        """
        Fetches all posts created by a specific user.
        Used for profile/activity views.

        Args:
            user_id: The author's user ID.
        Returns:
            List of post dicts ordered by created_at DESC.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    @staticmethod
    def delete(post_id: str, user_id: str) -> bool:
        """
        Deletes a post by ID, scoped to the author.
        Ownership check is enforced at the DB query level (eq user_id).

        Args:
            post_id: The post to delete.
            user_id: Must match the post's user_id.
        Returns:
            True if a row was deleted, False if not found or unauthorized.
        """
        response = (
            admin_supabase
            .table(TABLE)
            .delete()
            .eq("id", post_id)
            .eq("user_id", user_id)
            .execute()
        )
        return len(response.data) > 0

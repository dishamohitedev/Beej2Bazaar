"""
Community Feed — Domain Models
================================
Pure Pydantic models and enums. No DB imports, no HTTP imports.
This is the single source of truth for all community data shapes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PostType(str, Enum):
    """
    Strongly typed post classifications.

    Twitter/X style — every post must declare its intent so the
    RankingEngine can assign the correct base priority score.
    """
    QUESTION      = "QUESTION"       # Farmer asking for help / advice
    UPDATE        = "UPDATE"         # General farm update / observation
    DISEASE       = "DISEASE"        # Disease alert (may be auto-generated)
    ALERT         = "ALERT"          # Weather / pest alert
    ADVISORY      = "ADVISORY"       # Government / official advisory
    MARKET        = "MARKET"         # Mandi / market price update
    TIP           = "TIP"            # Practical farming tip
    SUCCESS_STORY = "SUCCESS_STORY"  # Farmer sharing a success


class FeedCategory(str, Enum):
    """
    UI-facing category filters. Each maps to one or more PostType values.
    See FeedFilters for the mapping.
    """
    ALL                 = "ALL"
    QUESTIONS           = "QUESTIONS"
    DISEASE_ALERTS      = "DISEASE_ALERTS"
    GOVERNMENT_ADVISORIES = "GOVERNMENT_ADVISORIES"
    MARKET_UPDATES      = "MARKET_UPDATES"
    WEATHER_ALERTS      = "WEATHER_ALERTS"
    FARMING_TIPS        = "FARMING_TIPS"
    SUCCESS_STORIES     = "SUCCESS_STORIES"


# Category → PostType(s) mapping — used by FeedEngine to build DB query filters
CATEGORY_TO_POST_TYPES: dict[FeedCategory, list[PostType]] = {
    FeedCategory.ALL:                   list(PostType),
    FeedCategory.QUESTIONS:             [PostType.QUESTION],
    FeedCategory.DISEASE_ALERTS:        [PostType.DISEASE],
    FeedCategory.GOVERNMENT_ADVISORIES: [PostType.ADVISORY],
    FeedCategory.MARKET_UPDATES:        [PostType.MARKET],
    FeedCategory.WEATHER_ALERTS:        [PostType.ALERT],
    FeedCategory.FARMING_TIPS:          [PostType.TIP],
    FeedCategory.SUCCESS_STORIES:       [PostType.SUCCESS_STORY],
}

# ---------------------------------------------------------------------------
# Core Domain Models
# ---------------------------------------------------------------------------


class FeedPost(BaseModel):
    """
    The canonical feed post returned to consumers.
    rank_score and is_liked_by_me are injected by FeedEngine — they are
    never persisted to the database.
    """
    id:             str
    user_id:        str
    author_name:    str
    post_type:      PostType
    title:          Optional[str]   = None
    content:        str
    image_url:      Optional[str]   = None
    crop_id:        Optional[str]   = None
    district:       Optional[str]   = None
    village:        Optional[str]   = None
    latitude:       Optional[float] = None
    longitude:      Optional[float] = None
    likes_count:    int             = 0
    comments_count: int             = 0
    is_liked_by_me: bool            = False  # injected at feed layer
    rank_score:     float           = 0.0    # injected by RankingEngine
    created_at:     datetime


class Comment(BaseModel):
    """A comment on a community post."""
    id:          str
    post_id:     str
    user_id:     str
    author_name: str
    comment:     str
    created_at:  datetime


class Like(BaseModel):
    """A like relationship between a user and a post."""
    id:         str
    post_id:    str
    user_id:    str
    created_at: datetime


# ---------------------------------------------------------------------------
# Input / Request Models
# ---------------------------------------------------------------------------


class PostCreate(BaseModel):
    """Payload for creating a new post."""
    post_type: PostType
    content:   str = Field(..., min_length=1, max_length=500)
    title:     Optional[str]  = Field(None, max_length=200)
    image_url: Optional[str]  = None
    crop_id:   Optional[str]  = None


class CommentCreate(BaseModel):
    """Payload for adding a comment to a post."""
    comment: str = Field(..., min_length=1, max_length=300)


class FeedFilters(BaseModel):
    """
    Query filters for the community feed.
    Defaults produce the standard ranked all-category feed.
    """
    category:    FeedCategory = FeedCategory.ALL
    nearby_only: bool         = False
    page:        int          = Field(1, ge=1)
    page_size:   int          = Field(20, ge=1, le=50)


# ---------------------------------------------------------------------------
# Output Models
# ---------------------------------------------------------------------------


class PostDetail(BaseModel):
    """A single post with its full comment thread."""
    post:     FeedPost
    comments: List[Comment] = Field(default_factory=list)


class FeedPage(BaseModel):
    """
    Paginated feed response.
    total_count is the number of posts after category/nearby filtering
    (before pagination), used by the UI to determine if more pages exist.
    """
    posts:       List[FeedPost]
    page:        int
    page_size:   int
    total_count: int

    @property
    def has_next(self) -> bool:
        return (self.page * self.page_size) < self.total_count


class LikeToggleResult(BaseModel):
    """Returned after toggling a like on a post."""
    post_id:     str
    liked:       bool   # True = now liked, False = now unliked
    likes_count: int

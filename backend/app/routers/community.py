"""
Community Router
================
HTTP layer for the Farmer Community Feed feature.

All business logic lives in CommunityService — this router only:
  1. Validates incoming request shapes (via Pydantic models in app.community.models)
  2. Extracts the authenticated user from the token
  3. Delegates to CommunityService
  4. Returns the typed response

Endpoints
---------
GET  /community/feed               → Ranked, paginated feed (supports category + nearby filters)
GET  /community/feed/nearby        → Shortcut: nearby-only ranked feed
GET  /community/post/{post_id}     → Single post + full comment thread
POST /community/post               → Create a new farmer post
DELETE /community/post/{post_id}   → Delete own post
POST /community/post/{post_id}/like     → Toggle like on a post
POST /community/post/{post_id}/comment  → Add a comment to a post
"""

from __future__ import annotations

import logging
import mimetypes
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.community.community_service import CommunityService
from app.community.models import (
    Comment,
    CommentCreate,
    FeedCategory,
    FeedFilters,
    FeedPage,
    FeedPost,
    LikeToggleResult,
    PostCreate,
    PostDetail,
)
from app.core.config import settings
from app.database.supabase import admin_supabase
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/community",
    tags=["Community"],
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STORAGE_BUCKET   = "community-media"
MAX_FILE_SIZE_MB = 5
ALLOWED_TYPES    = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# ---------------------------------------------------------------------------
# Singleton service — lightweight, holds no DB connections
# ---------------------------------------------------------------------------
_service = CommunityService()

# ---------------------------------------------------------------------------
# Image Upload Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/upload-image",
    summary="Upload an image for a community post",
    description=(
        "Uploads an image to Supabase Storage (community-media bucket). "
        "Accepted formats: JPEG, PNG, WebP, GIF. Max size: 5 MB. "
        "Returns the public URL to pass as `image_url` when creating a post."
    ),
    status_code=status.HTTP_200_OK,
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    current_user=Depends(get_current_user),
):
    # --- Validate MIME type ---
    content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type}'. Allowed: JPEG, PNG, WebP, GIF.",
        )

    # --- Read and validate file size ---
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB.",
        )

    # --- Build a unique storage path ---
    ext = (file.filename or "image").rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp", "gif"}:
        ext = "jpg"
    unique_filename = f"{current_user.id}/{uuid.uuid4()}.{ext}"

    # --- Upload to Supabase Storage ---
    try:
        admin_supabase.storage.from_(STORAGE_BUCKET).upload(
            path        = unique_filename,
            file        = contents,
            file_options= {"content-type": content_type, "upsert": "false"},
        )
    except Exception as exc:
        logger.error("upload_image: Supabase Storage upload failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image upload failed. Please try again.",
        )

    # --- Build the public URL ---
    public_url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{unique_filename}"
    )

    logger.info(
        "upload_image: user=%s uploaded %s (%.2f MB) → %s",
        current_user.id, unique_filename, size_mb, public_url,
    )
    return {"image_url": public_url, "filename": unique_filename, "size_mb": round(size_mb, 2)}


# ---------------------------------------------------------------------------
# Feed — Read Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/feed",
    response_model=FeedPage,
    summary="Get ranked community feed",
    description=(
        "Returns the ranked, paginated community feed for the authenticated farmer. "
        "Supports filtering by category and restricting to nearby (same-district) posts. "
        "Posts are scored by type priority + recency + proximity + engagement."
    ),
)
def get_feed(
    category: FeedCategory = Query(
        FeedCategory.ALL,
        description="Filter by post category (ALL returns everything).",
    ),
    nearby_only: bool = Query(
        False,
        description="If true, only return posts from the viewer's district.",
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(20, ge=1, le=50, description="Number of posts per page."),
    current_user=Depends(get_current_user),
):
    filters = FeedFilters(
        category=category,
        nearby_only=nearby_only,
        page=page,
        page_size=page_size,
    )
    logger.info(
        "GET /community/feed user=%s category=%s nearby=%s page=%d",
        current_user.id, category, nearby_only, page,
    )
    return _service.get_feed(viewer_id=current_user.id, filters=filters)


@router.get(
    "/feed/nearby",
    response_model=FeedPage,
    summary="Get nearby community feed",
    description=(
        "Convenience endpoint that forces nearby_only=True. "
        "Returns posts from the same district as the authenticated farmer, ranked."
    ),
)
def get_nearby_feed(
    category: FeedCategory = Query(FeedCategory.ALL),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user=Depends(get_current_user),
):
    filters = FeedFilters(
        category=category,
        nearby_only=True,
        page=page,
        page_size=page_size,
    )
    logger.info(
        "GET /community/feed/nearby user=%s category=%s page=%d",
        current_user.id, category, page,
    )
    return _service.get_nearby_feed(viewer_id=current_user.id, filters=filters)


@router.get(
    "/post/{post_id}",
    response_model=PostDetail,
    summary="Get post detail with comment thread",
    description="Returns a single post enriched with like/comment counts, is_liked_by_me, and its full comment thread.",
)
def get_post_detail(
    post_id: str,
    current_user=Depends(get_current_user),
):
    logger.info("GET /community/post/%s user=%s", post_id, current_user.id)
    try:
        return _service.get_post_detail(post_id=post_id, viewer_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ---------------------------------------------------------------------------
# Posts — Write Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/post",
    response_model=FeedPost,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new community post",
    description=(
        "Creates a new farmer-authored post. The author's name and district are "
        "automatically fetched from their profile. Content is capped at 500 characters."
    ),
)
def create_post(
    data: PostCreate,
    current_user=Depends(get_current_user),
):
    logger.info(
        "POST /community/post user=%s type=%s",
        current_user.id, data.post_type,
    )
    return _service.create_post(user_id=current_user.id, data=data)


@router.delete(
    "/post/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete own post",
    description="Deletes a post. Only the original author can delete their own posts.",
)
def delete_post(
    post_id: str,
    current_user=Depends(get_current_user),
):
    logger.info("DELETE /community/post/%s user=%s", post_id, current_user.id)
    _service.delete_post(user_id=current_user.id, post_id=post_id)


# ---------------------------------------------------------------------------
# Engagement Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/post/{post_id}/like",
    response_model=LikeToggleResult,
    summary="Toggle like on a post",
    description=(
        "Likes the post if the user hasn't liked it yet; unlikes it if they have. "
        "Returns the updated like count and the current liked state."
    ),
)
def toggle_like(
    post_id: str,
    current_user=Depends(get_current_user),
):
    logger.info("POST /community/post/%s/like user=%s", post_id, current_user.id)
    return _service.toggle_like(post_id=post_id, user_id=current_user.id)


@router.post(
    "/post/{post_id}/comment",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a post",
    description=(
        "Adds a comment to the specified post. The commenter's name is fetched from "
        "their profile. Comments are limited to 300 characters."
    ),
)
def add_comment(
    post_id: str,
    data: CommentCreate,
    current_user=Depends(get_current_user),
):
    logger.info(
        "POST /community/post/%s/comment user=%s",
        post_id, current_user.id,
    )
    return _service.add_comment(
        post_id=post_id,
        user_id=current_user.id,
        data=data,
    )

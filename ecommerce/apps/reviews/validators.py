"""
Reviews App Validators

Custom validation logic for ratings, owner limits, and duplicate checks.
"""

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.reviews import constants

User = get_user_model()


def validate_rating(value: Decimal) -> None:
    """
    Validate that rating is between 1-5 and in 0.5 increments.

    Args:
        value: Rating value to validate

    Raises:
        ValidationError: If rating is out of range or not in 0.5 increments
    """
    if value < constants.MIN_RATING or value > constants.MAX_RATING:
        raise ValidationError(constants.ERR_INVALID_RATING)

    # Check if rating is in 0.5 increments (e.g., 1.0, 1.5, 2.0, etc.)
    if (value * 2) % 1 != 0:
        raise ValidationError(constants.ERR_RATING_STEP)


def validate_review_title_length(value: str) -> None:
    """
    Validate review title length.

    Args:
        value: Title string to validate

    Raises:
        ValidationError: If title exceeds maximum length
    """
    if len(value) > constants.REVIEW_TITLE_MAX_LENGTH:
        raise ValidationError(constants.ERR_TITLE_TOO_LONG)


def validate_review_comment_length(value: str) -> None:
    """
    Validate review comment length.

    Args:
        value: Comment string to validate

    Raises:
        ValidationError: If comment exceeds maximum length
    """
    if len(value) > constants.REVIEW_COMMENT_MAX_LENGTH:
        raise ValidationError(constants.ERR_COMMENT_TOO_LONG)


def validate_reply_comment_length(value: str) -> None:
    """
    Validate reply comment length.

    Args:
        value: Reply string to validate

    Raises:
        ValidationError: If reply exceeds maximum length
    """
    if len(value) > constants.REPLY_COMMENT_MAX_LENGTH:
        raise ValidationError(constants.ERR_REPLY_TOO_LONG)

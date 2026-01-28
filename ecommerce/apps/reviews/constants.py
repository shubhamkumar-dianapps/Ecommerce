"""
Reviews App Constants

Centralized configuration for field lengths, ratings, pagination, and messages.
"""

# Field Lengths
REVIEW_TITLE_MAX_LENGTH: int = 100
REVIEW_COMMENT_MAX_LENGTH: int = 2000
REPLY_COMMENT_MAX_LENGTH: int = 1000

# Rating Configuration
MIN_RATING: int = 1
MAX_RATING: int = 5
RATING_DECIMAL_PLACES: int = 1  # Allows 4.5, 3.5, etc.
RATING_MAX_DIGITS: int = 2

# Pagination
DEFAULT_REVIEWS_PAGE_SIZE: int = 10
MAX_REVIEWS_PAGE_SIZE: int = 50
DEFAULT_REPLIES_PAGE_SIZE: int = 5
MAX_REPLIES_PAGE_SIZE: int = 20

# Owner Review Limit
MAX_OWNER_REVIEWS_PER_PRODUCT: int = 1

# Messages
MSG_REVIEW_CREATED: str = "Review submitted successfully"
MSG_REVIEW_UPDATED: str = "Review updated successfully"
MSG_REVIEW_DELETED: str = "Review deleted successfully"
MSG_OWNER_REVIEW_LIMIT: str = (
    f"Product owners can only submit {MAX_OWNER_REVIEWS_PER_PRODUCT} review per product"
)
MSG_DUPLICATE_REVIEW: str = "You have already reviewed this product"
MSG_LIKE_ADDED: str = "Review liked successfully"
MSG_LIKE_REMOVED: str = "Like removed successfully"
MSG_DUPLICATE_LIKE: str = "You have already liked this review"
MSG_REPLY_CREATED: str = "Reply posted successfully"
MSG_REPLY_UPDATED: str = "Reply updated successfully"
MSG_REPLY_DELETED: str = "Reply deleted successfully"
MSG_REPLY_PERMISSION_DENIED: str = (
    "Only product owner or verified shopkeepers can reply to reviews"
)
MSG_NOT_REVIEW_OWNER: str = "You can only edit your own reviews"
MSG_NOT_REPLY_OWNER: str = "You can only edit your own replies"

# Validation Messages
ERR_INVALID_RATING: str = f"Rating must be between {MIN_RATING} and {MAX_RATING}"
ERR_RATING_STEP: str = "Rating must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)"
ERR_TITLE_TOO_LONG: str = f"Title cannot exceed {REVIEW_TITLE_MAX_LENGTH} characters"
ERR_COMMENT_TOO_LONG: str = (
    f"Comment cannot exceed {REVIEW_COMMENT_MAX_LENGTH} characters"
)
ERR_REPLY_TOO_LONG: str = f"Reply cannot exceed {REPLY_COMMENT_MAX_LENGTH} characters"

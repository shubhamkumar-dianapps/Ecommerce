"""
Review Serializers

Production-ready serializers for reviews with comprehensive validation.
"""

from decimal import Decimal
from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.reviews.models import Review, ReviewLike, ReviewReply
from apps.reviews import constants

User = get_user_model()


class ReviewLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for review likes.

    Read-only serializer for displaying like information.
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ReviewLike
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "created_at",
        ]
        read_only_fields = fields

    def get_user_name(self, obj: ReviewLike) -> str:
        """Get user's display name"""
        if hasattr(obj.user, "customerprofile"):
            return obj.user.customerprofile.full_name
        elif hasattr(obj.user, "shopkeeperprofile"):
            return obj.user.shopkeeperprofile.shop_name
        return obj.user.email


class ReviewReplySerializer(serializers.ModelSerializer):
    """
    Serializer for review replies.

    Features:
    - User display name
    - Active status
    - Timestamps
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    is_product_owner = serializers.SerializerMethodField()

    class Meta:
        model = ReviewReply
        fields = [
            "id",
            "review",
            "user",
            "user_name",
            "user_email",
            "is_product_owner",
            "comment",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "review",
            "user",
            "is_product_owner",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj: ReviewReply) -> str:
        """Get user's display name"""
        if hasattr(obj.user, "customerprofile"):
            return obj.user.customerprofile.full_name
        elif hasattr(obj.user, "shopkeeperprofile"):
            return obj.user.shopkeeperprofile.shop_name
        return obj.user.email

    def get_is_product_owner(self, obj: ReviewReply) -> bool:
        """Check if reply is from product owner"""
        return obj.review.product.shopkeeper == obj.user


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing reviews.

    Features:
    - User display information
    - Helpful count (likes)
    - Owner review flag
    - Current user has liked flag
    - Reply count
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "product_name",
            "user",
            "user_name",
            "user_email",
            "rating",
            "title",
            "comment",
            "is_active",
            "is_owner_review",
            "is_verified_purchase",
            "helpful_count",
            "user_has_liked",
            "reply_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "helpful_count",
            "is_owner_review",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj: Review) -> str:
        """Get user's display name"""
        if hasattr(obj.user, "customerprofile"):
            return obj.user.customerprofile.full_name
        elif hasattr(obj.user, "shopkeeperprofile"):
            return obj.user.shopkeeperprofile.shop_name
        return obj.user.email

    def get_user_has_liked(self, obj: Review) -> bool:
        """Check if current user has liked this review using prefetched data"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # Use prefetched likes if available
            if (
                hasattr(obj, "_prefetched_objects_cache")
                and "likes" in obj._prefetched_objects_cache
            ):
                return any(like.user_id == request.user.id for like in obj.likes.all())
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_reply_count(self, obj: Review) -> int:
        """Get number of active replies from prefetched data"""
        if hasattr(obj, "active_replies"):
            return len(obj.active_replies)
        return obj.replies.filter(is_active=True).count()


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single review with replies.

    Features:
    - All review information
    - List of all likes
    - List of all active replies
    """

    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    likes = ReviewLikeSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "product_name",
            "user",
            "user_name",
            "user_email",
            "rating",
            "title",
            "comment",
            "is_active",
            "is_owner_review",
            "is_verified_purchase",
            "helpful_count",
            "user_has_liked",
            "likes",
            "replies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "helpful_count",
            "is_owner_review",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj: Review) -> str:
        """Get user's display name"""
        if hasattr(obj.user, "customerprofile"):
            return obj.user.customerprofile.full_name
        elif hasattr(obj.user, "shopkeeperprofile"):
            return obj.user.shopkeeperprofile.shop_name
        return obj.user.email

    def get_user_has_liked(self, obj: Review) -> bool:
        """Check if current user has liked this review using prefetched data"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # Use prefetched likes if available
            if (
                hasattr(obj, "_prefetched_objects_cache")
                and "likes" in obj._prefetched_objects_cache
            ):
                return any(like.user_id == request.user.id for like in obj.likes.all())
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_replies(self, obj: Review):
        """Get only active replies from prefetched data"""
        if hasattr(obj, "active_replies"):
            return ReviewReplySerializer(
                obj.active_replies, many=True, context=self.context
            ).data
        # Fallback if not prefetched
        active_replies = obj.replies.filter(is_active=True)
        return ReviewReplySerializer(
            active_replies, many=True, context=self.context
        ).data


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating reviews.

    Features:
    - Rating validation (1-5, 0.5 increments)
    - Owner review limit check
    - No duplicate review check
    - Field length validation
    """

    class Meta:
        model = Review
        fields = [
            "product",
            "rating",
            "title",
            "comment",
        ]

    def validate_rating(self, value: Decimal) -> Decimal:
        """
        Validate rating is between 1-5 in 0.5 increments.

        Args:
            value: Rating value

        Returns:
            Validated rating

        Raises:
            ValidationError: If rating is invalid
        """
        if value < Decimal(str(constants.MIN_RATING)) or value > Decimal(
            str(constants.MAX_RATING)
        ):
            raise serializers.ValidationError(constants.ERR_INVALID_RATING)

        # Check 0.5 increments
        if (value * 2) % 1 != 0:
            raise serializers.ValidationError(constants.ERR_RATING_STEP)

        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate review data.

        Checks:
        - No duplicate review (on create)
        - Owner review limit (on create)

        Args:
            attrs: Validated attributes

        Returns:
            Validated attributes

        Raises:
            ValidationError: If validation fails
        """
        request = self.context.get("request")
        product = attrs.get("product")

        # Only validate on create, not update
        if not self.instance:
            # Check for duplicate review
            if Review.objects.filter(product=product, user=request.user).exists():
                raise serializers.ValidationError(
                    {"non_field_errors": [constants.MSG_DUPLICATE_REVIEW]}
                )

            # Check owner review limit
            if product.shopkeeper == request.user:
                owner_review_count = Review.objects.filter(
                    product=product, is_owner_review=True
                ).count()

                if owner_review_count >= constants.MAX_OWNER_REVIEWS_PER_PRODUCT:
                    raise serializers.ValidationError(
                        {"non_field_errors": [constants.MSG_OWNER_REVIEW_LIMIT]}
                    )

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Review:
        """
        Create review with user from request.

        Args:
            validated_data: Validated review data

        Returns:
            Created review instance
        """
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)

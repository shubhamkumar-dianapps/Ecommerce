"""
Address Views

ViewSet for address CRUD operations with filtering and pagination.
"""

from typing import Any
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.addresses.models import Address
from apps.addresses.serializers import (
    AddressSerializer,
    AddressListSerializer,
    SetDefaultSerializer,
)
from apps.addresses.permissions import IsAddressOwner
from apps.addresses.pagination import AddressPagination
from apps.addresses import constants


class AddressViewSet(viewsets.ModelViewSet):
    """
    Address management viewset.

    Endpoints:
        GET    /api/v1/addresses/              - List user addresses
        POST   /api/v1/addresses/              - Create new address
        GET    /api/v1/addresses/{id}/         - Get specific address
        PUT    /api/v1/addresses/{id}/         - Update address (full)
        PATCH  /api/v1/addresses/{id}/         - Update address (partial)
        DELETE /api/v1/addresses/{id}/         - Delete address
        POST   /api/v1/addresses/{id}/set-default/ - Set as default

    Features:
        - Pagination (default: 5 per page)
        - Filtering by address_type, is_default, city
        - Ordering by created_at, is_default
        - Only user's own addresses visible
        - Cannot delete default address
    """

    permission_classes = [permissions.IsAuthenticated, IsAddressOwner]
    pagination_class = AddressPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["address_type", "is_default", "city", "country"]
    ordering_fields = ["created_at", "updated_at", "is_default"]
    ordering = ["-is_default", "-created_at"]

    def get_queryset(self):
        """
        Get addresses for current user only.

        Returns:
            QuerySet: Filtered address queryset
        """
        return Address.objects.filter(user=self.request.user).select_related("user")

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        Returns:
            Serializer class
        """
        if self.action == "list":
            return AddressListSerializer
        elif self.action == "set_default":
            return SetDefaultSerializer
        return AddressSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create new address.

        Args:
            request: HTTP request

        Returns:
            Response: Created address data with 201 status
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": constants.ADDRESS_CREATED_SUCCESS, "address": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update address.

        Args:
            request: HTTP request

        Returns:
            Response: Updated address data
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"message": constants.ADDRESS_UPDATED_SUCCESS, "address": serializer.data}
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Delete address.

        Prevents deletion of default address.

        Args:
            request: HTTP request

        Returns:
            Response: Success message or error
        """
        instance = self.get_object()

        # Prevent deletion of default address
        if instance.is_default:
            return Response(
                {"error": constants.CANNOT_DELETE_DEFAULT},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(
            {"message": constants.ADDRESS_DELETED_SUCCESS},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=["post"])
    def set_default(self, request: Request, pk: Any = None) -> Response:
        """
        Set this address as default.

        POST /api/v1/addresses/{id}/set-default/

        Args:
            request: HTTP request
            pk: Address primary key

        Returns:
            Response: Success message with updated address
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return full address data
        address_serializer = AddressSerializer(instance)
        return Response(
            {
                "message": constants.DEFAULT_ADDRESS_UPDATED,
                "address": address_serializer.data,
            }
        )

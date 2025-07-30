"""Domain events for users bounded context."""

from typing import Any, Dict, Optional

from src.shared.domain.events import DomainEvent


class UserCreated(DomainEvent):
    """Event raised when a user is created."""

    user_id: str
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
        }


class UserUpdated(DomainEvent):
    """Event raised when a user is updated."""

    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
        }


class UserDeactivated(DomainEvent):
    """Event raised when a user is deactivated."""

    user_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "reason": self.reason,
        }


class CustomerCreated(DomainEvent):
    """Event raised when a customer is created."""

    customer_id: str
    user_id: str
    shipping_address: str
    billing_address: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "customer_id": self.customer_id,
            "user_id": self.user_id,
            "shipping_address": self.shipping_address,
            "billing_address": self.billing_address,
        }


class CustomerAddressAdded(DomainEvent):
    """Event raised when an address is added to a customer."""

    customer_id: str
    address_type: str  # "shipping" or "billing"
    address: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "customer_id": self.customer_id,
            "address_type": self.address_type,
            "address": self.address,
        }


class SellerCreated(DomainEvent):
    """Event raised when a seller is created."""

    seller_id: str
    user_id: str
    company_name: str
    company_description: Optional[str] = None
    website: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "seller_id": self.seller_id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "company_description": self.company_description,
            "website": self.website,
        }


class SellerVerified(DomainEvent):
    """Event raised when a seller is verified."""

    seller_id: str
    verified_by: str
    verification_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "seller_id": self.seller_id,
            "verified_by": self.verified_by,
            "verification_notes": self.verification_notes,
        }


class SellerUnverified(DomainEvent):
    """Event raised when a seller is unverified."""

    seller_id: str
    unverified_by: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "seller_id": self.seller_id,
            "unverified_by": self.unverified_by,
            "reason": self.reason,
        }

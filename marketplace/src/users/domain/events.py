"""Domain events for users bounded context."""

# Python imports
from typing import Any, Dict, Optional

# Local imports
from src.shared.domain.events import DomainEvent


class UserCreated(DomainEvent):
    """
    Event raised when a user is created.
    
    Attributes:
        user_id: The ID of the user.
        email: The email of the user.
        first_name: The first name of the user.
        last_name: The last name of the user.
        phone_number: The phone number of the user.
    """

    user_id: str
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when a user is updated.
    
    Attributes:
        user_id: The ID of the user.
        first_name: The first name of the user.
        last_name: The last name of the user.
        phone_number: The phone number of the user.
    """

    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when a user is deactivated.
    
    Attributes:
        user_id: The ID of the user.
        reason: The reason for deactivation.
    """

    user_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when a customer is created.
    
    Attributes:
        customer_id: The ID of the customer.
        user_id: The ID of the user.
        shipping_address: The shipping address of the customer.
        billing_address: The billing address of the customer.
    """

    customer_id: str
    user_id: str
    shipping_address: str
    billing_address: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an address is added to a customer.
    
    Attributes:
        customer_id: The ID of the customer.
        address_type: The type of address.
        address: The address.
    """

    customer_id: str
    address_type: str  # "shipping" or "billing"
    address: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when a seller is created.
    
    Attributes:
        seller_id: The ID of the seller.
        user_id: The ID of the user.
        company_name: The name of the company.
        company_description: The description of the company.
        website: The website of the company.
    """

    seller_id: str
    user_id: str
    company_name: str
    company_description: Optional[str] = None
    website: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when a seller is verified.
    
    Attributes:
        seller_id: The ID of the seller.
        verified_by: The ID of the user who verified the seller.
        verification_notes: The notes from the verification.
    """

    seller_id: str
    verified_by: str
    verification_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when a seller is unverified.
    
    Attributes:
        seller_id: The ID of the seller.
        unverified_by: The ID of the user who unverified the seller.
        reason: The reason for unverification.
    """

    seller_id: str
    unverified_by: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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

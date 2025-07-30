"""Notifications API controllers."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.notifications.application.services import NotificationService
from src.notifications.infrastructure.repositories import (
    InMemoryNotificationRepository,
    InMemoryNotificationBatchRepository,
    InMemoryNotificationSubscriptionRepository,
)

# Pydantic models for API
class SendNotificationRequest(BaseModel):
    """Request model for sending a notification."""
    recipient_id: str
    notification_type: str
    title: str
    content: str
    priority: str = "normal"
    metadata: Optional[dict] = None

class CreateBatchRequest(BaseModel):
    """Request model for creating a notification batch."""
    batch_name: str
    notifications: List[SendNotificationRequest]

class NotificationResponse(BaseModel):
    """Response model for notification data."""
    id: str
    recipient_id: str
    notification_type: str
    title: str
    content: str
    priority: str
    status: str
    metadata: Optional[dict] = None
    created_at: str
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None

class BatchResponse(BaseModel):
    """Response model for batch data."""
    id: str
    batch_name: str
    total_notifications: int
    status: str
    created_at: str
    completed_at: Optional[str] = None

class CreateSubscriptionRequest(BaseModel):
    """Request model for creating a notification subscription."""
    user_id: str
    notification_types: List[str]
    channels: List[str]
    preferences: Optional[dict] = None

class SubscriptionResponse(BaseModel):
    """Response model for subscription data."""
    id: str
    user_id: str
    notification_types: List[str]
    channels: List[str]
    preferences: Optional[dict] = None
    is_active: bool
    created_at: str
    updated_at: str

class RetryNotificationRequest(BaseModel):
    """Request model for retrying a failed notification."""
    reason: Optional[str] = None

# Dependency injection
def get_notification_service() -> NotificationService:
    """Get notification service instance."""
    notification_repo = InMemoryNotificationRepository()
    batch_repo = InMemoryNotificationBatchRepository()
    subscription_repo = InMemoryNotificationSubscriptionRepository()
    return NotificationService(notification_repo, batch_repo, subscription_repo)

# Router
router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    request: SendNotificationRequest,
    service: NotificationService = Depends(get_notification_service)
) -> NotificationResponse:
    """Send a single notification."""
    try:
        notification = await service.send_notification(
            recipient_id=request.recipient_id,
            notification_type=request.notification_type,
            title=request.title,
            content=request.content,
            priority=request.priority,
            metadata=request.metadata,
        )
        
        return NotificationResponse(
            id=notification.id.value,
            recipient_id=notification.recipient.value,
            notification_type=notification.template.notification_type.value,
            title=notification.template.title.value,
            content=notification.template.content.value,
            priority=notification.priority.value,
            status=notification.status.value,
            metadata=notification.metadata,
            created_at=notification.created_at.isoformat(),
            sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
            delivered_at=notification.delivered_at.isoformat() if notification.delivered_at else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/batch", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    request: CreateBatchRequest,
    service: NotificationService = Depends(get_notification_service)
) -> BatchResponse:
    """Create a batch of notifications."""
    try:
        batch = await service.create_batch(
            batch_name=request.batch_name,
            notifications=[
                {
                    "recipient_id": n.recipient_id,
                    "notification_type": n.notification_type,
                    "title": n.title,
                    "content": n.content,
                    "priority": n.priority,
                    "metadata": n.metadata,
                }
                for n in request.notifications
            ]
        )
        
        return BatchResponse(
            id=batch.id.value,
            batch_name=batch.batch_name,
            total_notifications=batch.total_notifications,
            status=batch.status.value,
            created_at=batch.created_at.isoformat(),
            completed_at=batch.completed_at.isoformat() if batch.completed_at else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/batch/{batch_id}/start")
async def start_batch_processing(
    batch_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    """Start processing a notification batch."""
    try:
        batch = await service.start_batch_processing(batch_id)
        return {
            "batch_id": batch.id.value,
            "status": batch.status.value,
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/batch/{batch_id}/complete")
async def complete_batch(
    batch_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    """Complete a notification batch."""
    try:
        batch = await service.complete_batch(batch_id)
        return {
            "batch_id": batch.id.value,
            "status": batch.status.value,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service)
) -> NotificationResponse:
    """Get a notification by ID."""
    try:
        notification = await service.get_notification(notification_id)
        return NotificationResponse(
            id=notification.id.value,
            recipient_id=notification.recipient.value,
            notification_type=notification.template.notification_type.value,
            title=notification.template.title.value,
            content=notification.template.content.value,
            priority=notification.priority.value,
            status=notification.status.value,
            metadata=notification.metadata,
            created_at=notification.created_at.isoformat(),
            sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
            delivered_at=notification.delivered_at.isoformat() if notification.delivered_at else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{notification_id}/mark-sent")
async def mark_notification_sent(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as sent."""
    try:
        notification = await service.mark_notification_sent(notification_id)
        return {
            "notification_id": notification.id.value,
            "status": notification.status.value,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{notification_id}/mark-delivered")
async def mark_notification_delivered(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as delivered."""
    try:
        notification = await service.mark_notification_delivered(notification_id)
        return {
            "notification_id": notification.id.value,
            "status": notification.status.value,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{notification_id}/mark-failed")
async def mark_notification_failed(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as failed."""
    try:
        notification = await service.mark_notification_failed(notification_id)
        return {
            "notification_id": notification.id.value,
            "status": notification.status.value,
            "failed_at": notification.failed_at.isoformat() if notification.failed_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{notification_id}/retry")
async def retry_notification(
    notification_id: str,
    request: RetryNotificationRequest,
    service: NotificationService = Depends(get_notification_service)
):
    """Retry a failed notification."""
    try:
        notification = await service.retry_notification(
            notification_id=notification_id,
            reason=request.reason,
        )
        return {
            "notification_id": notification.id.value,
            "status": notification.status.value,
            "retry_count": notification.retry_count,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    service: NotificationService = Depends(get_notification_service)
) -> SubscriptionResponse:
    """Create a notification subscription."""
    try:
        subscription = await service.create_subscription(
            user_id=request.user_id,
            notification_types=request.notification_types,
            channels=request.channels,
            preferences=request.preferences,
        )
        
        return SubscriptionResponse(
            id=subscription.id.value,
            user_id=subscription.user_id,
            notification_types=subscription.notification_types,
            channels=subscription.channels,
            preferences=subscription.preferences,
            is_active=subscription.is_active,
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/subscriptions/user/{user_id}", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    user_id: str,
    service: NotificationService = Depends(get_notification_service)
) -> List[SubscriptionResponse]:
    """Get all subscriptions for a user."""
    try:
        subscriptions = await service.get_user_subscriptions(user_id)
        return [
            SubscriptionResponse(
                id=subscription.id.value,
                user_id=subscription.user_id,
                notification_types=subscription.notification_types,
                channels=subscription.channels,
                preferences=subscription.preferences,
                is_active=subscription.is_active,
                created_at=subscription.created_at.isoformat(),
                updated_at=subscription.updated_at.isoformat(),
            )
            for subscription in subscriptions
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/pending", response_model=List[NotificationResponse])
async def get_pending_notifications(
    service: NotificationService = Depends(get_notification_service)
) -> List[NotificationResponse]:
    """Get all pending notifications."""
    try:
        notifications = await service.get_pending_notifications()
        return [
            NotificationResponse(
                id=notification.id.value,
                recipient_id=notification.recipient.value,
                notification_type=notification.template.notification_type.value,
                title=notification.template.title.value,
                content=notification.template.content.value,
                priority=notification.priority.value,
                status=notification.status.value,
                metadata=notification.metadata,
                created_at=notification.created_at.isoformat(),
                sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
                delivered_at=notification.delivered_at.isoformat() if notification.delivered_at else None,
            )
            for notification in notifications
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/failed", response_model=List[NotificationResponse])
async def get_failed_notifications(
    service: NotificationService = Depends(get_notification_service)
) -> List[NotificationResponse]:
    """Get all failed notifications."""
    try:
        notifications = await service.get_failed_notifications()
        return [
            NotificationResponse(
                id=notification.id.value,
                recipient_id=notification.recipient.value,
                notification_type=notification.template.notification_type.value,
                title=notification.template.title.value,
                content=notification.template.content.value,
                priority=notification.priority.value,
                status=notification.status.value,
                metadata=notification.metadata,
                created_at=notification.created_at.isoformat(),
                sent_at=notification.sent_at.isoformat() if notification.sent_at else None,
                delivered_at=notification.delivered_at.isoformat() if notification.delivered_at else None,
            )
            for notification in notifications
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 
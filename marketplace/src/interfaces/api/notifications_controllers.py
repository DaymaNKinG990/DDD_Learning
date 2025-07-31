"""Notifications API controllers."""

# Python imports
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Local imports
from src.notifications.application.services import NotificationService
from src.notifications.infrastructure.repositories import (
    InMemoryNotificationRepository,
    InMemoryNotificationBatchRepository,
    InMemoryNotificationSubscriptionRepository,
)


# Pydantic models for API
class SendNotificationRequest(BaseModel):
    """
    Request model for sending a notification.

    Attributes:
        recipient_id (str): The ID of the recipient.
        notification_type (str): The type of notification.
        title (str): The title of the notification.
        content (str): The content of the notification.
        priority (str): The priority of the notification.
        metadata (Optional[dict]): The metadata of the notification.
    """

    recipient_id: str
    notification_type: str
    title: str
    content: str
    priority: str = "normal"
    metadata: Optional[dict] = None


class CreateBatchRequest(BaseModel):
    """
    Request model for creating a notification batch.

    Attributes:
        batch_name (str): The name of the batch.
        notifications (List[SendNotificationRequest]): The list of notifications to send.
    """

    batch_name: str
    notifications: List[SendNotificationRequest]


class NotificationResponse(BaseModel):
    """
    Response model for notification data.

    Attributes:
        id (str): The ID of the notification.
        recipient_id (str): The ID of the recipient.
        notification_type (str): The type of notification.
        title (str): The title of the notification.
        content (str): The content of the notification.
        priority (str): The priority of the notification.
        status (str): The status of the notification.
        metadata (Optional[dict]): The metadata of the notification.
        created_at (str): The creation date and time of the notification.
        sent_at (Optional[str]): The date and time the notification was sent.
        delivered_at (Optional[str]): The date and time the notification was delivered.
    """

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
    """
    Response model for batch data.

    Attributes:
        id (str): The ID of the batch.
        batch_name (str): The name of the batch.
        total_notifications (int): The total number of notifications in the batch.
        status (str): The status of the batch.
        created_at (str): The creation date and time of the batch.
        completed_at (Optional[str]): The date and time the batch was completed.
    """

    id: str
    batch_name: str
    total_notifications: int
    status: str
    created_at: str
    completed_at: Optional[str] = None


class CreateSubscriptionRequest(BaseModel):
    """
    Request model for creating a notification subscription.

    Attributes:
        user_id (str): The ID of the user.
        notification_types (List[str]): The types of notifications to subscribe to.
        channels (List[str]): The channels to send notifications to.
        preferences (Optional[dict]): The preferences of the subscription.
    """

    user_id: str
    notification_types: List[str]
    channels: List[str]
    preferences: Optional[dict] = None


class SubscriptionResponse(BaseModel):
    """
    Response model for subscription data.

    Attributes:
        id (str): The ID of the subscription.
        user_id (str): The ID of the user.
        notification_types (List[str]): The types of notifications to subscribe to.
        channels (List[str]): The channels to send notifications to.
        preferences (Optional[dict]): The preferences of the subscription.
        is_active (bool): Whether the subscription is active.
        created_at (str): The creation date and time of the subscription.
        updated_at (str): The date and time the subscription was updated.
    """

    id: str
    user_id: str
    notification_types: List[str]
    channels: List[str]
    preferences: Optional[dict] = None
    is_active: bool
    created_at: str
    updated_at: str


class RetryNotificationRequest(BaseModel):
    """
    Request model for retrying a failed notification.

    Attributes:
        reason (Optional[str]): The reason for retrying the notification.
    """

    reason: Optional[str] = None


# Dependency injection
def get_notification_service() -> NotificationService:
    """
    Get notification service instance.

    Returns:
        NotificationService: The notification service instance.
    """

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
    """
    Send a single notification.

    Args:
        request (SendNotificationRequest): The request object containing notification details.
        service (NotificationService): The notification service instance.

    Returns:
        NotificationResponse: The response object containing notification details.
    """

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
    """
    Create a batch of notifications.

    Args:
        request (CreateBatchRequest): The request object containing batch details.
        service (NotificationService): The notification service instance.

    Returns:
        BatchResponse: The response object containing batch details.
    """

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
) -> dict[str, str]:
    """
    Start processing a notification batch.

    Args:
        batch_id (str): The ID of the batch.
        service (NotificationService): The notification service instance.

    Returns:
        dict[str, str]: The response object containing batch details.
    """

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
) -> dict[str, str]:
    """
    Complete a notification batch.

    Args:
        batch_id (str): The ID of the batch.
        service (NotificationService): The notification service instance.

    Returns:
        dict[str, str]: The response object containing batch details.
    """

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
    """
    Get a notification by ID.

    Args:
        notification_id (str): The ID of the notification.
        service (NotificationService): The notification service instance.

    Returns:
        NotificationResponse: The response object containing notification details.
    """

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
) -> dict[str, str]:
    """
    Mark a notification as sent.

    Args:
        notification_id (str): The ID of the notification.
        service (NotificationService): The notification service instance.

    Returns:
        dict[str, str]: The response object containing notification details.
    """

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
) -> dict[str, str]:
    """
    Mark a notification as delivered.

    Args:
        notification_id (str): The ID of the notification.
        service (NotificationService): The notification service instance.

    Returns:
        dict[str, str]: The response object containing notification details.
    """

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
) -> dict[str, str]:
    """
    Mark a notification as failed.

    Args:
        notification_id (str): The ID of the notification.
        service (NotificationService): The notification service instance.

    Returns:
        dict[str, str]: The response object containing notification details.
    """

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
) -> dict[str, str]:
    """
    Retry a failed notification.

    Args:
        notification_id (str): The ID of the notification.
        request (RetryNotificationRequest): The request object containing retry details.
        service (NotificationService): The notification service instance.

    Returns:
        dict[str, str]: The response object containing notification details.
    """

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
    """
    Create a notification subscription.

    Args:
        request (CreateSubscriptionRequest): The request object containing subscription details.
        service (NotificationService): The notification service instance.

    Returns:
        SubscriptionResponse: The response object containing subscription details.
    """

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
    """
    Get all subscriptions for a user.

    Args:
        user_id (str): The ID of the user.
        service (NotificationService): The notification service instance.

    Returns:
        List[SubscriptionResponse]: The response object containing subscription details.
    """

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
    """
    Get all pending notifications.

    Args:
        service (NotificationService): The notification service instance.

    Returns:
        List[NotificationResponse]: The response object containing notification details.
    """
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
    """
    Get all failed notifications.

    Args:
        service (NotificationService): The notification service instance.

    Returns:
        List[NotificationResponse]: The response object containing notification details.
    """
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
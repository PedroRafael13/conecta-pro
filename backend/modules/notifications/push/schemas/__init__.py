"""Schemas do módulo Push Notifications.

Sprint 37 - Push Notifications Mobile.
"""

from modules.notifications.push.schemas.push_schemas import (
    ActionButtonSchema,
    CampaignAnalyticsResponse,
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignResponse,
    CampaignUpdateRequest,
    DeviceListResponse,
    DeviceRegisterRequest,
    DeviceResponse,
    DeviceUpdateRequest,
    MetricsQueryRequest,
    MetricsSummaryResponse,
    NotificationResponse,
    SegmentCreateRequest,
    SegmentResponse,
    SegmentRuleSchema,
    SendPushRequest,
    SendPushResponse,
    TopicResponse,
    TopicSubscribeRequest,
    TopicUnsubscribeRequest,
)

__all__ = [
    # Device
    "DeviceRegisterRequest",
    "DeviceUpdateRequest",
    "DeviceResponse",
    "DeviceListResponse",
    # Campaign
    "ActionButtonSchema",
    "CampaignCreateRequest",
    "CampaignUpdateRequest",
    "CampaignResponse",
    "CampaignListResponse",
    # Notification
    "SendPushRequest",
    "SendPushResponse",
    "NotificationResponse",
    # Segment
    "SegmentRuleSchema",
    "SegmentCreateRequest",
    "SegmentResponse",
    # Analytics
    "MetricsQueryRequest",
    "MetricsSummaryResponse",
    "CampaignAnalyticsResponse",
    # Topic
    "TopicSubscribeRequest",
    "TopicUnsubscribeRequest",
    "TopicResponse",
]

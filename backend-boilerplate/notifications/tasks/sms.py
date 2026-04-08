"""
Generic SMS sending module - No task queue dependencies.

Projects can integrate with their choice of task queue (django-rq, Celery, etc.)
by creating their own task wrappers around these functions.

Project-specific logic (like saving to Notification model) should be handled
in the project's own task wrappers.
"""
import json
import logging

import urllib3
from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_phone(phone):
    """
    Normalize phone number format.
    
    Args:
        phone (str): Phone number to normalize
        
    Returns:
        str: Formatted phone number (e.g., 256XXXXXXXXX)
    """
    if not phone:
        return None
    
    # Extract last 9 digits and prepend country code
    return f"256{phone[-9:]}"


def send_sms(
    phone,
    message,
    country_code="256",
    **kwargs
):
    """
    Generic SMS sending function (synchronous).
    
    This function handles SMS transmission only, with no project-specific dependencies.
    Projects should handle notification logging, user lookups, etc. in their own wrappers.
    
    Args:
        phone (str): Phone number to send to
        message (str): SMS message content
        country_code (str): Country code prefix (default: "256")
        **kwargs: Additional arguments (for future extensibility)
    
    Returns:
        dict: Response from SMS service
        
    Raises:
        ValueError: If phone or message is empty
    """
    if not phone:
        logger.warning("SMS send failed: No phone number provided")
        raise ValueError("Phone number is required")
    
    if not message:
        logger.warning("SMS send failed: No message content provided")
        raise ValueError("Message content is required")
    
    try:
        # Normalize phone number
        formatted_phone = normalize_phone(phone)
        if not formatted_phone:
            raise ValueError("Invalid phone number format")
        
        # Send SMS via external service
        http = urllib3.PoolManager()
        resp = http.request(
            "GET",
            f"{settings.NOTIFICATIONS_SERVICE_URL}/sms/",
            fields={
                "textmessage": message,
                "phonenumber": formatted_phone,
            }
        )
        
        if resp.data:
            return json.loads(resp.data.decode("utf-8"))
        return {"status": "sent", "phone": formatted_phone}
        
    except Exception as e:
        logger.error(f"Error sending SMS to {phone}: {str(e)}")
        raise


def send_sms_async_wrapper(*args, **kwargs):
    """
    Wrapper for async task execution.
    
    Projects should create their own task decorators using this function.
    
    Example for django-rq with Notification logging:
    
        from django_rq import job
        from django.contrib.contenttypes.models import ContentType
        from your_auth.models import User
        from your_notifications.models import Notification
        from backend_boilerplate.notifications.tasks.sms import send_sms_async_wrapper
        
        @job("sms_queue")
        def send_sms_task(phone, message, content_type=None, object_id=None):
            # Project-specific: Log notification
            try:
                user = User.objects.get(phone_number__endswith=phone[-9:])
                if content_type and object_id:
                    Notification.objects.create(
                        user=user,
                        message=message,
                        created_by=user,
                        content_type=content_type,
                        object_id=object_id,
                    )
            except User.DoesNotExist:
                logger.warning(f"User not found for phone {phone}")
            
            # Generic: Send SMS
            return send_sms_async_wrapper(phone, message)
    
    Example for Celery with Notification logging:
    
        from celery import shared_task
        from django.contrib.contenttypes.models import ContentType
        from your_auth.models import User
        from your_notifications.models import Notification
        from backend_boilerplate.notifications.tasks.sms import send_sms_async_wrapper
        
        @shared_task(bind=True, retry_on_error=True)
        def send_sms_task(self, phone, message, content_type=None, object_id=None):
            try:
                # Project-specific: Log notification
                try:
                    user = User.objects.get(phone_number__endswith=phone[-9:])
                    if content_type and object_id:
                        Notification.objects.create(
                            user=user,
                            message=message,
                            created_by=user,
                            content_type=content_type,
                            object_id=object_id,
                        )
                except User.DoesNotExist:
                    logger.warning(f"User not found for phone {phone}")
                
                # Generic: Send SMS
                return send_sms_async_wrapper(phone, message)
                
            except Exception as exc:
                raise self.retry(exc=exc)
    """
    return send_sms(*args, **kwargs)


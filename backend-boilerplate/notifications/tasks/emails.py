import logging

from backend_boilerplate.notifications.emails import handle_email

logger = logging.getLogger(__name__)


def send_email(
    subject,
    recipients=None,
    sender_email=None,
    html=False,
    template_name=None,
    context=None,
    attachment_file=None,
    from_template=False,
    html_message=None,
    **kwargs
):
    """
    Generic email sending function (synchronous).
    
    This function handles both positional and keyword arguments for flexibility.
    No task queue dependencies - projects add their own async integration.
    
    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        sender_email (str): Sender email address
        html (bool): Whether to send as HTML
        template_name (str): Template name if using templates
        context (dict): Template context
        attachment_file (list): Files to attach
        from_template (bool): Whether to render from template
        html_message (str): Pre-rendered HTML message
        **kwargs: Additional arguments passed to handle_email
    
    Returns:
        list: Response data from email service
    """
    if not recipients:
        return []
    
    recipients = [email for email in recipients if email]
    
    if not recipients:
        logger.warning("No valid recipients provided for email send")
        return []
    
    try:
        result = handle_email(
            subject=subject,
            to_emails=recipients,
            sender_email=sender_email,
            html=html,
            template_name=template_name,
            context=context or {},
            attachment_file=attachment_file or [],
            from_template=from_template,
            html_message=html_message,
            **kwargs
        )
        return result
    except Exception as e:
        logger.error(f"Error sending email to {recipients}: {str(e)}")
        raise


def send_email_async_wrapper(*args, **kwargs):
    """
    Wrapper for async task execution.
    
    Projects should create their own task decorators using this function.
    Example for django-rq:
    
        from django_rq import job
        
        @job("email_queue")
        def send_email_task(*args, **kwargs):
            return send_email_async_wrapper(*args, **kwargs)
    
    Example for Celery:
    
        from celery import shared_task
        
        @shared_task(bind=True, retry_on_error=True)
        def send_email_task(self, *args, **kwargs):
            try:
                return send_email_async_wrapper(*args, **kwargs)
            except Exception as exc:
                raise self.retry(exc=exc)
    """
    return send_email(*args, **kwargs)

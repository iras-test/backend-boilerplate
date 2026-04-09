from django.template.loader import render_to_string
from django.conf import settings
import urllib3
import json
import logging

logger = logging.getLogger(__name__)


# Send email through service api
def handle_email(
    subject,
    to_emails: list,
    sender_email,
    html=False,
    template_name=None,
    context=None,
    attachment_file=[],
    from_template=False,
    html_message=None,
):
    """
    constructs an email message and handles actual sending
    """
    if from_template:
        return handle_email_templates(
            subject=subject,
            to_emails=to_emails,
            sender_email=sender_email,
            html=html,
            html_message=html_message,
            attachment_file=attachment_file,
        )

    html_message = None
    if html and template_name:
        html_message = render_to_string(template_name, context)

    attachments = (
        attachment_file if isinstance(attachment_file, list) else [attachment_file]
    )
    attachments = {
        f"attachments[{index}]": data for index, data in enumerate(attachments)
    }

    http = urllib3.PoolManager()

    data = []

    for email in to_emails:

        resp = http.request(
            "POST",
            f"{settings.NOTIFICATIONS_SERVICE_URL}/email/",
            fields={
                "sender_email": sender_email,
                "html_message": html_message,
                "subject": subject,
                "to": email,
                **attachments,
            },
        )

        if resp.data:
            data.append(json.loads(resp.data.decode("utf-8")))

    return data


def handle_email_templates(
    subject,
    to_emails: list,
    sender_email,
    html=False,
    html_message=None,
    attachment_file=[],
):
    """
    constructs an email message and handles actual sending
    """
    attachments = (
        attachment_file if isinstance(attachment_file, list) else [attachment_file]
    )
    attachments = {
        f"attachments[{index}]": data for index, data in enumerate(attachments)
    }

    http = urllib3.PoolManager()

    data = []

    for email in to_emails:

        resp = http.request(
            "POST",
            f"{settings.NOTIFICATIONS_SERVICE_URL}/email/",
            fields={
                "sender_email": sender_email,
                "html_message": html_message,
                "subject": subject,
                "to": email,
                **attachments,
            },
        )

        if resp.data:
            try:
                data.append(json.loads(resp.data.decode("utf-8")))
            except json.JSONDecodeError:
                logger.error(
                    "Invalid JSON response for email to %s (status %s): %s",
                    email,
                    resp.status,
                    resp.data.decode("utf-8"),
                )

    return data
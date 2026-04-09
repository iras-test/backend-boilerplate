import logging

from django.conf import settings
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from backend_boilerplate.notifications.tasks.emails import send_email
from backend_boilerplate.notifications.template_renderer import TemplateRenderer
from backend_boilerplate.scrutiny.models import LevelActionNotificationTemplate, ScrutinyWorkflowConfigurable, WorkFlow, WorkflowAction
from backend_boilerplate.utils.constants import WORKFLOW_ACTION_TYPE_APPROVE, WORKFLOW_ACTION_TYPE_BACKWARD, WORKFLOW_ACTION_TYPE_FORWARD, WORKFLOW_ACTION_TYPE_REJECT


logger = logging.getLogger(__name__)
User = settings.AUTH_USER_MODEL


class ScrutinyWorkflowEngine:

    def __init__(
        self,
        instance,
        workflow_name: str,
        requesting_user,
        action_name: str,
        on_approved_callback=None,
        on_rejected_callback=None,
        on_pending_callback=None,
        created_by=None,
        pending_status: str | None = None,
        approved_status: str | None = None,
        rejected_status: str | None = None,
    ):
        self.instance = instance
        self.workflow_name = workflow_name
        self.requesting_user = requesting_user
        self.action_name = action_name
        self.on_approved_callback = on_approved_callback
        self.on_rejected_callback = on_rejected_callback
        self.on_pending_callback = on_pending_callback
        self.created_by = created_by
        self.pending_status = pending_status
        self.approved_status = approved_status
        self.rejected_status = rejected_status

        self._workflow = None
        self._level_config = None
        self._next_level_config = None
        self._action_obj = None
        self._current_level = None
        self._owner = None

    @transaction.atomic
    def execute(self):
        self._resolve_context()
        self._resolve_action()
        self._resolve_next_level_config()
        self._assert_user_has_role()
        self._assert_action_is_allowed_at_level()
        self._route()

    def _resolve_context(self):
        self._workflow = WorkFlow.objects.filter(
            name=self.workflow_name, is_active=True
        ).first()

        if not self._workflow:
            raise ValidationError(
                {"workflow": f"Workflow '{self.workflow_name}' not found or inactive."}
            )

        self._current_level = getattr(self.instance, "current_scrutiny_level", 1)
        self._owner = getattr(self.instance, "created_by", None) or self.created_by

        self._level_config = (
            ScrutinyWorkflowConfigurable.objects.prefetch_related(
                "actors", "allowed_actions"
            )
            .filter(
                workflow=self._workflow,
                scrutiny_level=self._current_level,
                is_active=True,
            )
            .first()
        )

        if not self._level_config:
            raise ValidationError(
                {
                    "workflow": (
                        f"No active configuration found for level {self._current_level} "
                        f"in workflow '{self.workflow_name}'."
                    )
                }
            )

    def _resolve_action(self):
        self._action_obj = WorkflowAction.objects.filter(
            name=self.action_name, is_active=True
        ).first()

        if not self._action_obj:
            raise ValidationError(
                {
                    "action": f"Action '{self.action_name}' does not exist or is inactive."
                }
            )

    def _resolve_next_level_config(self):
        next_level = self._current_level + 1
        self._next_level_config = self._get_level_config(next_level)

    def _assert_user_has_role(self):
        if not self._level_config.actors.exists():
            raise ValidationError(
                {
                    "workflow": (
                        f"Level {self._current_level} of '{self.workflow_name}' "
                        f"has no actors configured."
                    )
                }
            )

        if not self._level_config.user_can_act(self.requesting_user):
            raise PermissionDenied(
                f"You are not assigned as an actor at level "
                f"{self._current_level} of '{self.workflow_name}'."
            )

    def _assert_action_is_allowed_at_level(self):
        if self._action_obj.action_type == WORKFLOW_ACTION_TYPE_BACKWARD:
            return
        if self._action_obj.action_type == WORKFLOW_ACTION_TYPE_REJECT:
            return

        if not self._next_level_config:
            raise ValidationError(
                {
                    "workflow": (
                        f"No configuration found for the next level after {self._current_level} "
                        f"in workflow '{self.workflow_name}'."
                    )
                }
            )
        if not self._next_level_config.is_action_allowed(self.action_name):
            allowed = list(
                self._next_level_config.allowed_actions.filter(
                    is_active=True
                ).values_list("name", flat=True)
            )
            raise PermissionDenied(
                f"Action '{self.action_name}' is not permitted at level "
                f"{self._current_level + 1} of '{self.workflow_name}'. "
                f"Allowed: {allowed}."
            )

    def _route(self):
        dispatch = {
            WORKFLOW_ACTION_TYPE_APPROVE: self._apply_approved,
            WORKFLOW_ACTION_TYPE_REJECT: self._apply_rejected,
            WORKFLOW_ACTION_TYPE_FORWARD: self._apply_pending,
            WORKFLOW_ACTION_TYPE_BACKWARD: self._apply_send_back,
        }
        handler = dispatch.get(self._action_obj.action_type)
        if not handler:
            raise ValidationError(
                {
                    "action": (
                        f"Unknown action_type '{self._action_obj.action_type}' "
                        f"on action '{self.action_name}'."
                    )
                }
            )
        handler()

    def _apply_pending(self):
        next_level = self._current_level + 1

        self.instance.status = self.pending_status or self._action_obj.name
        self.instance.current_scrutiny_level = next_level

        if hasattr(self.instance, "sent_back"):
            self.instance.sent_back = False

            self.instance.save(
                update_fields=["status", "current_scrutiny_level", "sent_back"]
            )
        else:
            self.instance.save(update_fields=["status", "current_scrutiny_level"])

        logger.info(
            "Forwarded — instance=%s workflow='%s' level %s → %s",
            self.instance.pk,
            self.workflow_name,
            self._current_level,
            next_level,
        )

        if self.on_pending_callback:
            self.on_pending_callback(self.instance)

        if not self._next_level_config:
            logger.warning(
                "No config for level %s in '%s'. No notification sent.",
                next_level,
                self.workflow_name,
            )
            return

        # Get who to notify for the next level and send emails
        notification = self._get_notification_template()

        if not notification:
            return

        if (
            notification.notify_actors
            or not notification.notification_recipients.exists()
        ):
            # Fall back to actors if notify_actors is set OR no explicit recipients configured
            recipients = self._users_for_level(self._next_level_config)
        else:
            recipients = notification.notification_recipients.filter(is_active=True)

        for user in recipients:
            self._send_email(
                recipient=user
            )

    def _apply_send_back(self):
        target_level = self._action_obj.target_level

        target_config = self._get_level_config(target_level)
        target_status = (
            target_config.allowed_actions.filter(
                action_type=WORKFLOW_ACTION_TYPE_FORWARD, is_active=True
            )
            .values_list("name", flat=True)
            .first()
        )

        self.instance.status = target_status
        self.instance.current_scrutiny_level = target_level
        self.instance.sent_back = True
        self.instance.save(
            update_fields=["status", "current_scrutiny_level"]
            + (["sent_back"] if hasattr(self.instance, "sent_back") else [])
        )

        self._send_email(
            recipient=self._owner
        )

        target_config = self._get_level_config(target_level)
        if target_config:
            for user in self._users_for_level(target_config):
                if user != self._owner:
                    self._send_email(
                        recipient=user
                    )

    def _apply_approved(self):
        next_level = self._current_level + 1
        self.instance.current_scrutiny_level = next_level
        self.instance.status = self.approved_status or "approved"
        self.instance.save(update_fields=["status", "current_scrutiny_level"])

        if self.on_approved_callback:
            self.on_approved_callback(self.instance)

        notification = self._get_notification_template()

        if notification and notification.notification_recipients.exists():
            recipients = notification.notification_recipients.filter(is_active=True)
            for user in recipients:
                self._send_email(
                    recipient=user
                )
            # Only send to owner separately if not already in recipients
            if notification.notify_owner and self._owner:
                if not recipients.filter(pk=self._owner.pk).exists():
                    self._send_email(
                        recipient=self._owner
                    )
        else:
            # No explicit recipients — owner is the default, notify_owner is irrelevant here
            self._send_email(
                recipient=self._owner
            )


    def _apply_rejected(self):
        self.instance.status = self.rejected_status or "rejected"
        self.instance.save(update_fields=["status"])

        logger.info(
            "Rejected — instance=%s workflow='%s'",
            self.instance.pk,
            self.workflow_name,
        )

        if self.on_rejected_callback:
            self.on_rejected_callback(self.instance)

        notification = self._get_notification_template()

        if notification and notification.notification_recipients.exists():
            recipients = notification.notification_recipients.filter(is_active=True)
            for user in recipients:
                self._send_email(
                    recipient=user
                )
            if notification.notify_owner and self._owner:
                if not recipients.filter(pk=self._owner.pk).exists():
                    self._send_email(
                        recipient=self._owner
                    )
        else:
            self._send_email(
                recipient=self._owner
            )

    def _get_notification_template(self) -> LevelActionNotificationTemplate | None:
        """
        Look up the configured notification template for the current action
        at the current level.
        """
        next_level = self._current_level + 1
        level_config = ScrutinyWorkflowConfigurable.objects.prefetch_related(
                "actors", "allowed_actions"
            ).filter(
                workflow=self._workflow,
                scrutiny_level=next_level,
                is_active=True,
            ).first()

        return (
            LevelActionNotificationTemplate.objects.filter(
                level_config=level_config,
                action=self._action_obj,
            )
            .select_related("notification_template")
            .first()
        )

    def _send_email(
        self,
        recipient,
    ):
        if not recipient:
            return

        email_address = getattr(recipient, "email", None)
        if not email_address:
            return

        notification = self._get_notification_template()
        template = notification.notification_template if notification else None

        if not (template and template.enabled):
            return

        context = TemplateRenderer.build_generic_context(self.instance, recipient)
        subject, html = TemplateRenderer.render_email_template(template, context)

        def send_fn():
            send_email(
                subject,
                [email_address],
                settings.EMAIL_HOST_USER,
                html=True,
                from_template=True,
                html_message=html,
            )

        try:
            transaction.on_commit(send_fn)
        except Exception as exc:
            logger.error(
                "Failed to queue email to %s for instance=%s: %s",
                email_address,
                self.instance.pk,
                exc,
            )

    def _get_level_config(self, level: int):
        return (
            ScrutinyWorkflowConfigurable.objects.prefetch_related("actors")
            .filter(
                workflow=self._workflow,
                scrutiny_level=level,
                is_active=True,
            )
            .first()
        )

    @staticmethod
    def _users_for_level(level_config):
        return level_config.actors.filter(is_active=True)

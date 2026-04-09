import uuid

from django.db import models
from backend_boilerplate.configurables.models import NotificationSettings
from backend_boilerplate.utils.constants import WORKFLOW_ACTION_TYPE_BACKWARD, WORKFLOW_ACTION_TYPE_CHOICES, WORKFLOW_ACTION_TYPE_FORWARD
from backend_boilerplate.utils.managers import ActiveManager
from backend_boilerplate.utils.models import BaseModel
from django.conf import settings


class WorkflowAbstractModel(BaseModel):
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta(BaseModel.Meta):
        abstract = True


class WorkFlow(WorkflowAbstractModel):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True


    def __str__(self):
        return self.name

    @property
    def number_of_levels(self):
        return (
            ScrutinyWorkflowConfigurable.objects.filter(workflow=self, is_active=True)
            .values_list("scrutiny_level", flat=True)
            .distinct()
            .count()
        )


class WorkflowAction(WorkflowAbstractModel):
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)
    action_type = models.CharField(
        max_length=20,
        choices=WORKFLOW_ACTION_TYPE_CHOICES,
        default=WORKFLOW_ACTION_TYPE_FORWARD,
    )
    target_level = models.IntegerField(
        null=True,
        blank=True,
        help_text=(
            "Set this to send a submission back to a specific prior level. "
            "Leave NULL for normal forward/approve/reject routing."
        ),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.label} ({self.action_type})"

    @property
    def is_send_back(self) -> bool:
        """True when this forward action is actually a send-back to a prior level."""
        return self.action_type == WORKFLOW_ACTION_TYPE_BACKWARD


class ScrutinyWorkflowConfigurable(WorkflowAbstractModel):
    workflow = models.ForeignKey(
        WorkFlow,
        on_delete=models.DO_NOTHING,
        related_name="configs",
    )
    scrutiny_level = models.IntegerField(default=1)
    level_description = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    actors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="scrutiny_workflow_configs",
        help_text="Actors who can perform actions at this level.",
    )
    allowed_actions = models.ManyToManyField(
        WorkflowAction,
        related_name="level_configs",
        help_text="All actions that may be performed at this level (across all roles).",
    )

    class Meta:
        unique_together = ("workflow", "scrutiny_level")
        abstract = True

    def __str__(self):
        return f"{self.workflow.name} | Level {self.scrutiny_level}"

    @property
    def user_can_act(self, user) -> bool:
        return self.actors.filter(pk=user.pk).exists()

    @property
    def is_action_allowed(self, action_name: str) -> bool:
        """Check action is configured for this level and is active."""
        return self.allowed_actions.filter(name=action_name, is_active=True).exists()

    @property
    def get_actors_at_level(self):
        return self.actors.filter(is_active=True)


class LevelActionNotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level_config = models.ForeignKey(
        ScrutinyWorkflowConfigurable,
        on_delete=models.CASCADE,
        related_name="notification_templates",
    )
    action = models.ForeignKey(
        WorkflowAction,
        on_delete=models.CASCADE,
        related_name="notification_templates",
    )
    notification_template = models.ForeignKey(
        NotificationSettings,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="level_bindings",
    )
    notification_recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="scrutiny_workflow_config_notification_recipients",
        help_text="Users that should be notified when escalation occurs. this is mandatory for the case of",
    )
    notify_actors = models.BooleanField(
        default=False,
        help_text="Notify the actors configured at the target/next level.",
    )
    notify_owner = models.BooleanField(
        default=False,
        help_text="Notify the owner/creator of the submission.",
    )

    class Meta:
        unique_together = ("level_config", "action")
        ordering = ("level_config", "action")
        abstract = True

    def __str__(self):
        return f"{self.level_config} | {self.action.name}"
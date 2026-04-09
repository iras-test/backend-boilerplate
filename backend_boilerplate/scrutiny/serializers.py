from rest_framework import serializers

from backend_boilerplate.scrutiny.models import LevelActionNotificationTemplate, ScrutinyWorkflowConfigurable, WorkFlow, WorkflowAction
from backend_boilerplate.user_mgmt.serializers import SimplestUserSerializer
from backend_boilerplate.utils.serializers import ActivityModelSerializer, CreateOnlyCurrentUserDefault, NestedModelSerializer



class WorkFlowSerializer(ActivityModelSerializer):
    created_by = SimplestUserSerializer(
        required=False,
        default=CreateOnlyCurrentUserDefault(),
    )
    number_of_levels = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkFlow
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "is_active",
            "number_of_levels"
        ]

class WorkflowListSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkFlow
        fields = ["id", "name", "is_active", "description", "number_of_levels"]

class WorkflowActionSerializer(ActivityModelSerializer):
    created_by = SimplestUserSerializer(
        required=False,
        default=CreateOnlyCurrentUserDefault(),
    )

    class Meta:
        model = WorkflowAction
        fields = [
            "id",
            "name",
            "label",
            "is_active",
            "created_by",
            "action_type",
            "target_level",
        ]
        read_only_fields = ["created_by"]

class SimplifiedWorkflowActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowAction
        fields = ["id", "name", "action_type", "label"]


class WorkflowActionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowAction
        fields = [
            "id",
            "name",
            "label",
            "is_active",
            "action_type",
            "target_level",
            "created_at",
            "updated_at",
        ]

class LevelActionNotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelActionNotificationTemplate
        exclude = ["level_config"]


class ScrutinyWorkflowConfigurableSerializer(ActivityModelSerializer, NestedModelSerializer):
    created_by = SimplestUserSerializer(
        required=False,
        default=CreateOnlyCurrentUserDefault(),
    )
    workflow_name = serializers.CharField(source="workflow.name", read_only=True)
    action_details = SimplifiedWorkflowActionSerializer(
        source="allowed_actions", many=True, read_only=True
    )
    actor_details = SimplestUserSerializer(source="actors", many=True, read_only=True)

    notification_templates = LevelActionNotificationTemplateSerializer(
        many=True, required=False
    )

    class Meta:
        model = ScrutinyWorkflowConfigurable
        fields = [
            "id",
            "workflow_name",
            "workflow",
            "scrutiny_level",
            "allowed_actions",
            "actors",
            "level_description",
            "is_active",
            "action_details",
            "actor_details",
            "notification_templates",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def save_nested_notification_templates(
        self, data, instance, created=False, **kwargs
    ):
        if data is None:
            return

        incoming_actions = {t["action"] for t in data if t.get("action")}
        instance.notification_templates.exclude(action__in=incoming_actions).delete()

        for template in data:
            template = dict(template)
            recipients = template.pop("notification_recipients", [])
            obj, _ = LevelActionNotificationTemplate.objects.update_or_create(
                level_config=instance,
                action=template["action"],
                defaults=template,
            )
            if recipients is not None:
                obj.notification_recipients.set(recipients)


class ScrutinyWorkflowConfigurableListSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source="workflow.name")
    action_details = SimplifiedWorkflowActionSerializer(
        source="allowed_actions", many=True, read_only=True
    )
    actor_details = SimplestUserSerializer(source="actors", many=True, read_only=True)

    class Meta:
        model = ScrutinyWorkflowConfigurable
        fields = [
            "id",
            "workflow_name",
            "scrutiny_level",
            "level_description",
            "is_active",
            "action_details",
            "actor_details",
            "notification_templates",
            "created_at",
            "updated_at",
        ]


class ConfigsByRoleSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source="workflow.name")
    action_details = SimplifiedWorkflowActionSerializer(
        source="allowed_actions", many=True, read_only=True
    )

    class Meta:
        model = ScrutinyWorkflowConfigurable
        fields = [
            "id",
            "workflow_name",
            "scrutiny_level",
            "level_description",
            "is_active",
            "action_details",
        ]

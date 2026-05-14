from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from backend_boilerplate.utils.views import BaseViewSet


class BaseScrutinyWorkflowConfigurableViewSet(BaseViewSet):
    """
    Override in project:
        queryset, serializer_class, filterset_class,
        list_serializer_class, configs_by_role_serializer_class,
        simplified_action_serializer_class
    """

    list_serializer_class = None
    configs_by_role_serializer_class = None
    simplified_action_serializer_class = None

    def get_serializer_class(self):
        if self.action == "list" and self.list_serializer_class:
            return self.list_serializer_class
        return self.serializer_class

    @action(detail=False, methods=["get"], url_path="by-actor")
    def get_workflow_config_by_actor(self, request):
        actor_id = request.query_params.get("actor_id")
        workflow_name = request.query_params.get("workflow_name")
        level = request.query_params.get("level")

        if not actor_id or not workflow_name or not level:
            return Response(
                {"detail": "actor_id, workflow_name and level are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        config = (
            self.get_queryset()
            .filter(
                actors__id=actor_id,
                workflow__name=workflow_name,
                scrutiny_level=level,
            )
            .first()
        )

        if not config:
            return Response(
                {"detail": "No config found for this actor at this level."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.configs_by_role_serializer_class(config)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="current-level-actions")
    def current_level_actions(self, request):
        actor_id = request.query_params.get("actor_id")
        workflow_name = request.query_params.get("workflow_name")
        current_level = request.query_params.get("current_level")

        if not all([actor_id, workflow_name, current_level]):
            return Response(
                {"detail": "actor_id, workflow_name and current_level are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_config = (
            self.get_queryset()
            .filter(
                actors__id=actor_id,
                workflow__name=workflow_name,
                scrutiny_level=current_level,
            )
            .first()
        )

        if not current_config:
            return Response(
                {"detail": "No config found for this actor at the current level."},
                status=status.HTTP_404_NOT_FOUND,
            )

        current_level_actions = current_config.allowed_actions.filter(
            is_active=True,
        )

        serializer = self.simplified_action_serializer_class(
            current_level_actions, many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="activate")
    def activate_scrutiny_workflow_config(self, request, pk=None):
        config = self.get_queryset().model.all_objects.filter(pk=pk).first()
        if not config:
            return Response(
                {"detail": "Scrutiny Config not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        config.is_active = True
        config.save(update_fields=["is_active"])
        return Response(
            {"detail": "Scrutiny Config activated."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["patch"], url_path="deactivate")
    def deactivate_scrutiny_workflow_config(self, request, pk=None):
        config = self.get_queryset().model.all_objects.filter(pk=pk).first()
        if not config:
            return Response(
                {"detail": "Scrutiny Config not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        config.is_active = False
        config.save(update_fields=["is_active"])
        return Response(
            {"detail": "Scrutiny Config deactivated."}, status=status.HTTP_200_OK
        )


class BaseWorkflowActionViewSet(BaseViewSet):
    """
    Override in project:
        queryset, serializer_class, filterset_class,
        list_serializer_class
    """
    list_serializer_class = None

    def get_serializer_class(self):
        if self.action == "list" and self.list_serializer_class:
            return self.list_serializer_class
        return self.serializer_class

    @action(detail=False, methods=["get"], url_path="all")
    def all_actions(self, request):
        queryset = self.get_queryset().model.all_objects.all()

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="activate")
    def activate(self, request, pk=None):
        obj = self.get_queryset().model.all_objects.filter(pk=pk).first()
        if not obj:
            return Response(
                {"detail": "Action not found."}, status=status.HTTP_404_NOT_FOUND
            )
        obj.is_active = True
        obj.save(update_fields=["is_active"])
        return Response({"detail": "Action activated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        obj = self.get_queryset().model.all_objects.filter(pk=pk).first()
        if not obj:
            return Response(
                {"detail": "Action not found."}, status=status.HTTP_404_NOT_FOUND
            )
        obj.is_active = False
        obj.save(update_fields=["is_active"])
        return Response({"detail": "Action deactivated."}, status=status.HTTP_200_OK)


class BaseWorkFlowViewSet(BaseViewSet):
    """
    Override in project:
        queryset, serializer_class, filterset_class,
        list_serializer_class
    
    workflow_choices and available_workflows are project-specific
    because WORKFLOW_NAME_CHOICES lives in the project — add those
    actions directly on the subclass.
    """
    list_serializer_class = None

    def get_serializer_class(self):
        if self.action == "list" and self.list_serializer_class:
            return self.list_serializer_class
        return self.serializer_class
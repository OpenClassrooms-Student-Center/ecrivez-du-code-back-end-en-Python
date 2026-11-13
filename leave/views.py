from typing import assert_never

from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .composition import build_leave_service
from .exceptions import AlreadyProcessed
from .serializers import (
    BalanceSerializer,
    CreateLeaveRequestSerializer,
    LeaveRequestFilterSerializer,
    LeaveRequestSerializer,
)
from .services import ApprovalResult, RefusalResult


@extend_schema(responses=BalanceSerializer)
@api_view(["GET"])
def employee_balance(request, employee_id: int):
    result = build_leave_service().get_balance(employee_id)
    if result is None:
        raise NotFound("Ce salarié n’existe pas.")
    data = {"employee_id": employee_id, "balance": result}
    return Response(BalanceSerializer(data).data)


class LeaveRequestViewSet(viewsets.ViewSet):
    lookup_value_regex = r"\d+"

    @extend_schema(
        parameters=[LeaveRequestFilterSerializer],
        responses=LeaveRequestSerializer(many=True),
    )
    def list(self, request):
        query = LeaveRequestFilterSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        leave_requests = build_leave_service().get_requests(
            query.validated_data.get("status")
        )
        return Response(LeaveRequestSerializer(leave_requests, many=True).data)

    @extend_schema(responses=LeaveRequestSerializer)
    def retrieve(self, request, pk):
        leave_request = build_leave_service().get_request(int(pk))
        if leave_request is None:
            raise NotFound()
        return Response(LeaveRequestSerializer(leave_request).data)

    @extend_schema(
        request=CreateLeaveRequestSerializer,
        responses={201: LeaveRequestSerializer},
    )
    def create(self, request):
        payload = CreateLeaveRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        leave_request = build_leave_service().create(**payload.validated_data)
        if leave_request is None:
            raise ValidationError({"employeeId": ["Ce salarié n’existe pas."]})
        return Response(
            LeaveRequestSerializer(leave_request).data,
            status=status.HTTP_201_CREATED,
            headers={
                "Location": reverse("leave-request-detail", args=[leave_request.pk])
            },
        )

    @extend_schema(request=None, responses=LeaveRequestSerializer)
    @action(detail=True, methods=["post"])
    def approval(self, request, pk):
        service = build_leave_service()
        match service.approve(int(pk)):
            case ApprovalResult.NOT_FOUND:
                raise NotFound()
            case ApprovalResult.NOT_PENDING:
                raise AlreadyProcessed()
            case ApprovalResult.APPROVED | ApprovalResult.INSUFFICIENT_BALANCE:
                leave_request = service.get_request(int(pk))
                return Response(LeaveRequestSerializer(leave_request).data)
            case unreachable:
                assert_never(unreachable)

    @extend_schema(request=None, responses=LeaveRequestSerializer)
    @action(detail=True, methods=["post"])
    def refusal(self, request, pk):
        service = build_leave_service()
        match service.refuse(int(pk)):
            case RefusalResult.NOT_FOUND:
                raise NotFound()
            case RefusalResult.NOT_PENDING:
                raise AlreadyProcessed()
            case RefusalResult.REFUSED:
                leave_request = service.get_request(int(pk))
                return Response(LeaveRequestSerializer(leave_request).data)
            case unreachable:
                assert_never(unreachable)

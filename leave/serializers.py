from rest_framework import serializers

from .models import LeaveStatus


class BalanceSerializer(serializers.Serializer):
    employeeId = serializers.IntegerField(source="employee_id")
    balance = serializers.FloatField()


class LeaveRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    employeeId = serializers.IntegerField(source="employee_id")
    startDate = serializers.DateField(source="start_date")
    endDate = serializers.DateField(source="end_date")
    workingDays = serializers.IntegerField(source="working_days")
    status = serializers.CharField()


class LeaveRequestFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=LeaveStatus.choices, required=False)


class CreateLeaveRequestSerializer(serializers.Serializer):
    employeeId = serializers.IntegerField(source="employee_id", min_value=1)
    startDate = serializers.DateField(source="start_date")
    endDate = serializers.DateField(source="end_date")

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                {
                    "endDate": (
                        "La date de fin doit être postérieure ou égale "
                        "à la date de début."
                    )
                }
            )
        return attrs

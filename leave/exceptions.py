from rest_framework import status
from rest_framework.exceptions import APIException


class AlreadyProcessed(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Cette demande a déjà été traitée."
    default_code = "already_processed"

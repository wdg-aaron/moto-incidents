"""Exceptions raised by the ssmincidents service."""
from moto.core.exceptions import JsonRESTError

class ValidationException(JsonRESTError):
    code = 400

    def __init__(self, message):
        super().__init__("ValidationException", message)
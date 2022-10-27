"""Exceptions raised by the ssmcontacts service."""
from moto.core.exceptions import JsonRESTError

class ValidationException(JsonRESTError):
    code = 400

    def __init__(self, message):
        super().__init__("ValidationException", message)

class ConflictException(JsonRESTError):
    code = 400

    def __init__(self, message):
        super().__init__("ConflictException", message)

class ResourceNotFoundException(JsonRESTError):
    code = 400

    def __init__(self, message):
        super().__init__("ResourceNotFoundException", message)
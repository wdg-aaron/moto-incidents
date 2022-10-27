"""ssmcontacts module initialization; sets value for base decorator."""
from .models import ssmcontacts_backends
from ..core.models import base_decorator

mock_ssmcontacts = base_decorator(ssmcontacts_backends)

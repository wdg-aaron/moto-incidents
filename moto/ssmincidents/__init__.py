"""ssmincidents module initialization; sets value for base decorator."""
from .models import ssmincidents_backends
from ..core.models import base_decorator

mock_ssmincidents = base_decorator(ssmincidents_backends)
"""SSMIncidentsBackend class with methods for supported APIs."""

from moto.core import BaseBackend, BaseModel
from moto.core.utils import BackendDict
from .exceptions import ValidationException

class SSMIncidentsBackend(BaseBackend):
    """Implementation of SSMIncidents APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)

    # add methods from here

    def get_response_plan(self, arn):
        # implement here
        #return actions, arn, chat_channel, display_name, engagements, incident_template, name
        pass

    def update_response_plan(self, actions, arn, chat_channel, client_token, display_name, engagements, incident_template_dedupe_string, incident_template_impact, incident_template_notification_targets, incident_template_summary, incident_template_tags, incident_template_title):
        # implement here
        return 
    

ssmincidents_backends = BackendDict(SSMIncidentsBackend, "ssm-incidents")

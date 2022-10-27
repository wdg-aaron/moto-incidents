"""Handles incoming ssmincidents requests, invokes methods, returns responses."""
import json

from moto.core.responses import BaseResponse
from .models import ssmincidents_backends


class SSMIncidentsResponse(BaseResponse):
    """Handler for SSMIncidents requests and responses."""

    def __init__(self):
        super().__init__(service_name="ssmincidents")

    @property
    def ssmincidents_backend(self):
        """Return backend instance specific for this region."""
        return ssmincidents_backends[self.current_account][self.region]

    # add methods from here

    
    def get_response_plan(self):
        params = self._get_params()
        arn = params.get("arn")
        actions, arn, chat_channel, display_name, engagements, incident_template, name = self.ssmincidents_backend.get_response_plan(
            arn=arn,
        )
        # TODO: adjust response
        return json.dumps(dict(actions=actions, arn=arn, chatChannel=chat_channel, displayName=display_name, engagements=engagements, incidentTemplate=incident_template, name=name))

    
    def update_response_plan(self):
        params = self._get_params()
        actions = params.get("actions")
        arn = params.get("arn")
        chat_channel = params.get("chatChannel")
        client_token = params.get("clientToken")
        display_name = params.get("displayName")
        engagements = params.get("engagements")
        incident_template_dedupe_string = params.get("incidentTemplateDedupeString")
        incident_template_impact = params.get("incidentTemplateImpact")
        incident_template_notification_targets = params.get("incidentTemplateNotificationTargets")
        incident_template_summary = params.get("incidentTemplateSummary")
        incident_template_tags = params.get("incidentTemplateTags")
        incident_template_title = params.get("incidentTemplateTitle")
        self.ssmincidents_backend.update_response_plan(
            actions=actions,
            arn=arn,
            chat_channel=chat_channel,
            client_token=client_token,
            display_name=display_name,
            engagements=engagements,
            incident_template_dedupe_string=incident_template_dedupe_string,
            incident_template_impact=incident_template_impact,
            incident_template_notification_targets=incident_template_notification_targets,
            incident_template_summary=incident_template_summary,
            incident_template_tags=incident_template_tags,
            incident_template_title=incident_template_title,
        )
        # TODO: adjust response
        return json.dumps(dict())
# add templates from here

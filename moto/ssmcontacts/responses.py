"""Handles incoming ssmcontacts requests, invokes methods, returns responses."""
import json

from moto.core.responses import BaseResponse
from .models import ssmcontacts_backends


class SSMContactsResponse(BaseResponse):
    """Handler for SSMContacts requests and responses."""

    def __init__(self):
        super().__init__(service_name="ssm-contacts")

    @property
    def ssmcontacts_backend(self):
        """Return backend instance specific for this region."""
        return ssmcontacts_backends[self.current_account][self.region]

    def create_contact(self):
        print(self._get_param("Type"))
        contact_arn = self.ssmcontacts_backend.create_contact(
            alias=self._get_param("Alias"),
            display_name=self._get_param("DisplayName"),
            type_str=self._get_param("Type"),
            plan=self._get_param("Plan"),
            tags=self._get_param("Tags"),
            idempotency_token=self._get_param("IdempotencyToken"),
        )
        return json.dumps(dict(contactArn=contact_arn))

    
    def create_contact_channel(self):
        params = self._get_params()
        contact_id = params.get("ContactId")
        name = params.get("Name")
        type = params.get("Type")
        delivery_address = params.get("DeliveryAddress")
        defer_activation = params.get("DeferActivation")
        idempotency_token = params.get("IdempotencyToken")
        contact_channel_arn = self.ssmcontacts_backend.create_contact_channel(
            contact_id=contact_id,
            name=name,
            type=type,
            delivery_address=delivery_address,
            defer_activation=defer_activation,
            idempotency_token=idempotency_token,
        )
        return json.dumps(dict(contactChannelArn=contact_channel_arn))

    def get_contact(self):
        params = self._get_params()
        contact_id = params.get("ContactArn")
        return json.dumps(self.ssmcontacts_backend.get_contact(contact_id = contact_id))

    def list_contacts(self):
        params = self._get_params()
        next_token = params.get("NextToken")
        max_results = params.get("MaxResults")
        alias_prefix = params.get("AliasPrefix")
        type = params.get("Type")
        next_token, contacts = self.ssmcontacts_backend.list_contacts(
            next_token=next_token,
            max_results=max_results,
            alias_prefix=alias_prefix,
            type=type,
        )
        return json.dumps(dict(nextToken=next_token, contacts=contacts))

    # def list_tags_for_resource(self):
    #     params = self._get_params()
    #     resource_arn = params.get("ResourceARN")
    #     tags = self.ssmcontacts_backend.list_tags_for_resource(
    #         resource_arn=resource_arn,
    #     )
    #     # TODO: adjust response
    #     return json.dumps(dict(tags=tags))

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
        contact_arn = self.ssmcontacts_backend.create_contact(
            alias=self._get_param("Alias"),
            display_name=self._get_param("DisplayName"),
            type_str=self._get_param("Type"),
            plan=self._get_param("Plan"),
            tags=self._get_param("Tags"),
        )
        return json.dumps({"ContactArn": contact_arn})

    def create_contact_channel(self):

        contact_channel_arn = self.ssmcontacts_backend.create_contact_channel(
            contact_id=self._get_param("ContactId"),
            name=self._get_param("Name"),
            type_str=self._get_param("Type"),
            delivery_address=self._get_param("DeliveryAddress"),
            defer_activation=self._get_param("DeferActivation") or False,
        )
        response = dict(ContactChannelArn=contact_channel_arn)
        return json.dumps(response)

    def get_contact(self):
        return json.dumps(
            self.ssmcontacts_backend.get_contact(
                contact_id=self._get_param("ContactId")
            )
        )

    def list_contacts(self):
        contacts, next_token = self.ssmcontacts_backend.list_contacts(
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults"),
            alias_prefix=self._get_param("AliasPrefix"),
            type_str=self._get_param("Type"),
        )
        if next_token:
            response = dict(NextToken=next_token, Contacts=contacts)
        else:
            response = dict(Contacts=contacts)
        return json.dumps(response)

    # def list_tags_for_resource(self):
    #     params = self._get_params()
    #     resource_arn = params.get("ResourceARN")
    #     tags = self.ssmcontacts_backend.list_tags_for_resource(
    #         resource_arn=resource_arn,
    #     )
    #     # TODO: adjust response
    #     return json.dumps(dict(tags=tags))

    def update_contact(self):
        self.ssmcontacts_backend.update_contact(
            contact_id=self._get_param("ContactId"),
            display_name=self._get_param("DisplayName"),
            plan=self._get_param("Plan"),
        )
        return "{}"

    def update_contact_channel(self):
        params = self._get_params()
        contact_channel_id = params.get("ContactChannelId")
        name = params.get("Name")
        delivery_address = params.get("DeliveryAddress")
        self.ssmcontacts_backend.update_contact_channel(
            contact_channel_id=contact_channel_id,
            name=name,
            delivery_address=delivery_address,
        )
        return "{}"

    def delete_contact(self):
        params = self._get_params()
        contact_id = params.get("ContactId")
        self.ssmcontacts_backend.delete_contact(
            contact_id=contact_id,
        )
        return "{}"

    def delete_contact_channel(self):
        params = self._get_params()
        contact_channel_id = params.get("ContactChannelId")
        self.ssmcontacts_backend.delete_contact_channel(
            contact_channel_id=contact_channel_id,
        )
        return "{}"

    def get_contact_channel(self):
        params = self._get_params()
        contact_channel_id = params.get("ContactChannelId")
        return json.dumps(
            self.ssmcontacts_backend.get_contact_channel(
                contact_channel_id=contact_channel_id,
            )
        )

    def list_contact_channels(self):
        contact_channels, next_token  = self.ssmcontacts_backend.list_contact_channels(
            contact_id=self._get_param("ContactId"),
            next_token=self._get_param("NextToken"),
            max_results=self._get_param("MaxResults")
        )
        if next_token:
            response = dict(NextToken=next_token, ContactChannels=contact_channels)
        else:
            response = dict(ContactChannels=contact_channels)
        return json.dumps(response)

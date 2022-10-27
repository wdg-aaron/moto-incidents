"""SSMContactsBackend class with methods for supported APIs."""

from moto.core import BaseBackend, BaseModel
from moto.core.utils import BackendDict
from moto.utilities.paginator import paginate
from .utils import PAGINATION_MODEL
from typing import Dict
from moto.moto_api._internal import mock_random as random
import re
from .exceptions import ValidationException, ConflictException


class ContactChannel(BaseModel):
    def __init__(
        self,
        contact_id,
        name,
        type,
        delivery_address,
        idempotency_token,
        region,
        account_id,
        defer_activation=True,
    ):
        self.contact_id = contact_id
        self.name = name
        self.type = type
        self.delivery_address = delivery_address
        self.defer_activation = defer_activation
        self.activation_status = "ACTIVATED " if defer_activation else "NOT_ACTIVATED"
        if self.type not in ("EMAIL", "SMS", "VOICE"):
            raise ValidationException
        contact = contact_id.split(":")
        self.arn = (
            f"arn:aws:iam:{region}:{account_id}:contact-channel/{contact[5]}/{self.id}"
        )
        self.id = random.uuid4()
        if type(self.delivery_address) is not dict:
            raise ValidationException
        if self.delivery_address.get("SimpleAddress") is None:
            raise ValidationException

    def describe(self):
        return {
            "Name": self.name,
            "ContactArn": self.contact_id,
            "ActivationStatus": self.activation_status,
            "ContactChannelArn": self.arn,
            "DeliveryAddress": self.delivery_address,
        }

    @property
    def arn(self):
        return


class EngagementPlanTarget(BaseModel):
    """
    Target can be a contact or a contact channel
    """

    def __init__(
        self,
        contact_channel_id=None,
        retry_interval_in_minutes=1,
        contact_id=None,
        is_essential=False,
    ):
        if contact_channel_id is not None:
            # target is channel
            self.contact_channel_id = contact_channel_id
            self.retry_interval_in_minutes = retry_interval_in_minutes
        elif contact_id is not None:
            # target is contact
            self.contact_id = contact_id
            self.is_essential = is_essential

        if contact_channel_id is None and contact_id is None:
            raise ValidationException
        if contact_channel_id and contact_id:
            raise ValidationException


class EngagementPlanStage(BaseModel):
    def __init__(self, target, duration_in_minutes=1):
        self.target = EngagementPlanTarget(**target)
        self.duration_in_minutes = duration_in_minutes
        if 1 > self.duration_in_minutes > 30:
            raise ValidationException


class Contact(BaseModel):
    def __init__(
        self,
        alias,
        display_name,
        type_str,
        tags,
        idempotency_token,
        region,
        account_id,
        plan=None,
    ):
        self.alias = alias
        self.display_name = display_name
        self.type = type_str
        self.plan = list[EngagementPlanStage]
        self.tags = tags
        self.idempotency_token = idempotency_token  # ignored
        self.arn = f"arn:aws:iam:{region}:{account_id}:contact/{self.alias}"
        print(self.type)
        if self.type not in ("PERSONAL", "ESCALATION"):
            raise ValidationException("Type must be one of PERSONAL or ESCALATION")
        print(plan["Stages"])
        if plan["Stages"]:
            for stage in plan:
                print(stage)
                self.plan.append(EngagementPlanStage(stage))
        self.tags = tags

    def describe(self):
        return {
            "Alias": self.alias,
            "DisplayName": self.display_name,
            "Type": self.type,
            "Plan": {"Stages": self.plan},
            "Tags": self.tags,
            "ContactArn": self.arn,
        }

    def list_describe(self):
        return {
            "Alias": self.alias,
            "ContactArn": self.arn,
            "DisplayName": self.display_name,
            "Type": self.type,
        }


class SSMContactsBackend(BaseBackend):
    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.contacts: Dict[str, Contact] = {}
        self.contact_channels: Dict[str, ContactChannel] = {}

    # add methods from here

    def create_contact(
        self, alias, display_name, type_str, plan, tags, idempotency_token
    ):
        # implement here
        contact = Contact(
            alias=alias,
            display_name=display_name,
            type_str=type_str,
            plan=plan,
            tags=tags,
            idempotency_token=idempotency_token,
            region=self.region_name,
            account_id=self.account_id,
        )
        if contact.arn in self.contacts:
            raise ConflictException("Contact alias already exists")
        self.contacts[contact.arn] = contact
        return contact.arn

    def create_contact_channel(
        self,
        contact_id,
        name,
        type_str,
        delivery_address,
        defer_activation,
        idempotency_token,
    ):
        # implement here
        contact_channel = ContactChannel(
            contact_id=contact_id,
            name=name,
            type=type_str,
            delivery_address=delivery_address,
            defer_activation=defer_activation,
            idempotency_token=idempotency_token,
        )
        self.contact_channels[contact_channel.arn] = contact_channel
        return contact_channel.arn

    def get_contact(self, contact_id):
        contact = self._contacts.get(contact_id)
        if contact is None:
            raise ValidationException
        return contact.describe()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_contacts(self, next_token, alias_prefix, type, max_results=10):
        result = list()
        for id, contact in self.contacts.items():
            result.append(contact.list_describe())
        return result

    # def list_engagements(self, next_token, max_results, incident_id, time_range_value):
    #     # implement here
    #     pass
    #     #return next_token, engagements

    # def list_tags_for_resource(self, resource_arn):
    #     # implement here
    #     #return tags
    #     pass


ssmcontacts_backends = BackendDict(
    SSMContactsBackend,
    "ssm-contacts",
    use_boto3_regions=False,
    additional_regions=["global", "us-east-1", "us-west-2"],
)

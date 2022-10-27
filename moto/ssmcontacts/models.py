"""SSMContactsBackend class with methods for supported APIs."""
import dataclasses

from moto.core import BaseBackend, BaseModel
from moto.core.utils import BackendDict
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from .utils import PAGINATION_MODEL
from typing import Dict
from moto.moto_api._internal import mock_random as random
import re
from .exceptions import (
    ValidationException,
    ConflictException,
    ResourceNotFoundException,
)


class ContactChannel(BaseModel):
    def __init__(
        self,
        contact_id,
        name,
        type_str,
        delivery_address,
        region,
        account_id,
        defer_activation=True,
    ):
        self.contact_id = contact_id
        self.name = name

        self.defer_activation = defer_activation
        self.activation_status = "ACTIVATED " if defer_activation else "NOT_ACTIVATED"
        if type_str not in ("SMS", "EMAIL", "VOICE"):
            raise ValidationException(
                f"1 validation error detected: Value '{type_str}' at 'type' failed to satisfy "
                f"constraint: Member must satisfy enum value set: [SMS, EMAIL, VOICE]"
            )
        self.type = type_str
        self.id = random.uuid4()
        contact = contact_id.split(":")
        self.arn = (
            f"arn:aws:iam:{region}:{account_id}:contact-channel/{contact[5]}/{self.id}"
        )
        if delivery_address.get("SimpleAddress") is None:
            raise ValidationException(
                "Invalid value provided - ContactChannelAddress(simpleAddress=null) Contact "
                "channel address is invalid"
            )

        if self.type in ("SMS", "VOICE") and not re.match(
            r"\+\d{10}", delivery_address["SimpleAddress"]
        ):
            raise ValidationException(
                f"Invalid value provided - ContactChannelAddress({delivery_address}) Contact channel address is invalid"
            )
        if self.type == "EMAIL" and not re.match(
            r"\w+@\w+", delivery_address["SimpleAddress"]
        ):
            raise ValidationException(
                f"Invalid value provided - ContactChannelAddress({delivery_address}) Contact channel address is invalid"
            )
        self.delivery_address = delivery_address

    def describe(self):
        return {
            "Name": self.name,
            "ContactArn": self.contact_id,
            "ActivationStatus": self.activation_status,
            "ContactChannelArn": self.arn,
            "DeliveryAddress": self.delivery_address,
        }


class EngagementPlanTarget(BaseModel):
    """
    Target can be a contact or a contact channel
    """

    def __init__(self, target):
        self.contact_channel_id = None
        self.contact_id = None
        self.is_essential = None
        self.retry_interval_in_minutes = None
        if target.get("ChannelTargetInfo"):
            # target is channel
            self.contact_channel_id = target.get("ChannelTargetInfo").get("ContactChannelId")
            self.retry_interval_in_minutes = target.get("ChannelTargetInfo").get("RetryIntervalInMinutes")
        elif target.get("ContactTargetInfo"):
            # target is contact
            self.contact_id = target.get("ContactTargetInfo").get("ContactId")
            self.is_essential = target.get("ContactTargetInfo").get("IsEssential")

    def describe(self):
        if self.contact_channel_id is not None:
            return dict(ChannelTargetInfo=dict(
                ContactChannelId=self.contact_channel_id,
                RetryIntervalInMinutes=self.retry_interval_in_minutes,
            ))
        else:
            return dict(ContactTargetInfo=dict(ContactId=self.contact_id, IsEssential=self.is_essential))


class EngagementPlanStage(BaseModel):
    def __init__(self, stage):
        self.targets: list[EngagementPlanTarget] = []
        for target in stage.get("Targets"):
            self.targets.append(EngagementPlanTarget(target))
        self.duration_in_minutes = stage.get("DurationInMinutes")
        if 1 > self.duration_in_minutes > 30:
            raise ValidationException

    def describe(self):
        return dict(
            DurationInMinutes=self.duration_in_minutes,
            Targets=[t.describe() for t in self.targets],
        )


class Contact(BaseModel):
    def __init__(
        self,
        alias,
        display_name,
        type_str,
        tags,
        region,
        account_id,
        plan=None,
    ):
        self.alias = alias
        self.display_name = display_name
        self.plan: list[EngagementPlanStage] = []
        self.tags = tags
        self.arn = f"arn:aws:iam:{region}:{account_id}:contact/{self.alias}"
        if type_str not in ("PERSONAL", "ESCALATION"):
            raise ValidationException(
                f"1 validation error detected: Value '{type_str}' at 'type' failed to satisfy "
                f"constraint: Member must satisfy enum value set: [PERSONAL, ESCALATION]"
            )
        self.type = type_str
        self.set_plan(plan)
        self.tags = tags

    def set_plan(self, plan):
        self.plan: list[EngagementPlanStage] = []
        if plan["Stages"]:
            for stage in plan["Stages"]:
                self.plan.append(EngagementPlanStage(stage))

    def describe(self):
        return dict(
            Alias=self.alias,
            DisplayName=self.display_name,
            Type=self.type,
            Plan={"Stages": [s.describe() for s in self.plan]},
            Tags=self.tags,
            ContactArn=self.arn,
        )

    def list_describe(self):
        return dict(
            Alias=self.alias,
            ContactArn=self.arn,
            DisplayName=self.display_name,
            Type=self.type,
        )


class SSMContactsBackend(BaseBackend):
    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.contacts: Dict[str, Contact] = {}
        self.contact_channels: Dict[str, ContactChannel] = {}

    def create_contact(self, alias, display_name, type_str, plan, tags):
        contact = Contact(
            alias=alias,
            display_name=display_name,
            type_str=type_str,
            plan=plan,
            tags=tags,
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
    ):
        contact_channel = ContactChannel(
            contact_id=contact_id,
            name=name,
            type_str=type_str,
            delivery_address=delivery_address,
            defer_activation=defer_activation,
            region=self.region_name,
            account_id=self.account_id,
        )
        self.contact_channels[contact_channel.arn] = contact_channel
        return contact_channel.arn

    def get_contact(self, contact_id):
        contact = self.contacts.get(contact_id)
        if contact is None:
            raise ResourceNotFoundException("Contact not found")
        return contact.describe()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_contacts(self, next_token, alias_prefix, type_str, max_results=10):
        result = list()
        if type_str is not None and type_str not in ("PERSONAL", "ESCALATION"):
            raise ValidationException(
                f"1 validation error detected: Value '{type_str}' at 'type' failed to satisfy "
                f"constraint: Member must satisfy enum value set: [PERSONAL, ESCALATION]"
            )
        for id, contact in self.contacts.items():
            if type_str:
                if contact.type == type_str:
                    result.append(contact.list_describe())
            else:
                if type_str is None:
                    result.append(contact.list_describe())
        return result

    # def list_tags_for_resource(self, resource_arn):
    #     # implement here
    #     #return tags
    #     pass

    def update_contact(self, contact_id, display_name, plan):
        try:
            self.contacts.get(contact_id)
        except KeyError:
            raise ResourceNotFoundException
        if plan:
            self.contacts[contact_id].set_plan(plan)
        if display_name:
            self.contacts[contact_id].display_name = display_name

    def update_contact_channel(self, contact_channel_id, name, delivery_address):
        # implement here
        return

    def delete_contact(self, contact_id):
        if contact_id in self.contacts:
            self.contacts.pop(contact_id)
        return

    def delete_contact_channel(self, contact_channel_id):
        if contact_channel_id in self.contact_channels:
            self.contact_channels.pop(contact_channel_id)
        return

    def get_contact_channel(self, contact_channel_id):
        result = self.contact_channels.get(contact_channel_id)
        if result is None:
            raise ResourceNotFoundException
        return result.describe()

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_contact_channels(self, contact_id, next_token, max_results):
        result = list()
        for channel_id, channel in self.contact_channels.items():
            if contact_id == channel.contact_id:
                result.append(channel.describe())
        return result


# boto3 returns an empty array for regions for ssm-contacts, so moto breaks horribly.
# force moto to create at least a couple backends, no idea why boto3 doesnt find the regions, this IS a region
# specific service, not a global one.
ssmcontacts_backends = BackendDict(
    SSMContactsBackend,
    "ssm-contacts",
    use_boto3_regions=False,
    additional_regions=["global", "us-east-1", "us-west-2"],
)

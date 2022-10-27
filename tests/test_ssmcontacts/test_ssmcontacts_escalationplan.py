import boto3
import pytest
import sure  # noqa # pylint: disable=unused-import

from botocore.exceptions import ClientError
from moto import mock_ssmcontacts
from pprint import pprint


@mock_ssmcontacts
def test_create_escalation_plan():
    client = boto3.client("ssm-contacts")
    contacts = list()
    for i in range(0, 3):
        contacts.append(
            client.create_contact(
                DisplayName=f"Test User{i}",
                Alias=f"tuser{i}",
                Type="PERSONAL",
                Plan={"Stages": []},
                Tags=[{"Key": "Environment", "Value": "Testing"}],
            )
        )
    for c in contacts:
        channel1 = client.create_contact_channel(
            ContactId=c["ContactArn"],
            Name="voice",
            Type="VOICE",
            DeliveryAddress={"SimpleAddress": "+12005551212"},
            DeferActivation=True,
        )
        channel2 = client.create_contact_channel(
            ContactId=c["ContactArn"],
            Name="text",
            Type="SMS",
            DeliveryAddress={"SimpleAddress": "+12005551212"},
            DeferActivation=True,
        )
        channel3 = client.create_contact_channel(
            ContactId=c["ContactArn"],
            Name="email",
            Type="EMAIL",
            DeliveryAddress={"SimpleAddress": "invalid@emailaddress.com"},
            DeferActivation=True,
        )
        client.update_contact(
            ContactId=c["ContactArn"],
            Plan={
                "Stages": [
                    {
                        "DurationInMinutes": 5,
                        "Targets": [
                            {
                                "ChannelTargetInfo": {
                                    "ContactChannelId": channel1["ContactChannelArn"],
                                    "RetryIntervalInMinutes": 1,
                                }
                            }
                        ],
                    },
                    {
                        "DurationInMinutes": 5,
                        "Targets": [
                            {
                                "ChannelTargetInfo": {
                                    "ContactChannelId": channel2["ContactChannelArn"],
                                    "RetryIntervalInMinutes": 1,
                                }
                            }
                        ],
                    },
                    {
                        "DurationInMinutes": 5,
                        "Targets": [
                            {
                                "ChannelTargetInfo": {
                                    "ContactChannelId": channel3["ContactChannelArn"],
                                    "RetryIntervalInMinutes": 1,
                                }
                            }
                        ],
                    },
                ]
            },
        )
    escalation = client.create_contact(
        DisplayName=f"Test Escalation Plan",
        Alias=f"test_escalation_plan",
        Type="ESCALATION",
        Plan={
            "Stages": [
                {
                    "DurationInMinutes": 15,
                    "Targets": [{"ContactTargetInfo": {"ContactId": contacts[0]["ContactArn"], "IsEssential": True}}],
                },{
                    "DurationInMinutes": 15,
                    "Targets": [{"ContactTargetInfo": {"ContactId": contacts[1]["ContactArn"], "IsEssential": True}}],
                },{
                    "DurationInMinutes": 15,
                    "Targets": [{"ContactTargetInfo": {"ContactId": contacts[2]["ContactArn"], "IsEssential": True}}],
                }
            ]
        },
        Tags=[{"Key": "Environment", "Value": "Testing"}],
    )
    contacts = client.list_contacts(Type="ESCALATION")
    assert len(contacts["Contacts"]).should.equal(1)    # Should only return the one contact
    ep = client.get_contact(ContactId=escalation["ContactArn"])
    len(ep["Plan"]["Stages"]).should.equal(3)
    ep["Type"].should.equal("ESCALATION")

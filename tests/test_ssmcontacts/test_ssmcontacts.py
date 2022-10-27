import boto3
import pytest
import sure  # noqa # pylint: disable=unused-import

from botocore.exceptions import ClientError
from moto import mock_ssmcontacts
from pprint import pprint


@mock_ssmcontacts
def test_create_contact_success():
    client = boto3.client("ssm-contacts")
    contact = client.create_contact(
        DisplayName="Test User",
        Alias="tuser",
        Type="PERSONAL",
        Plan={"Stages": []},
        Tags=[{"Key": "Environment", "Value": "Testing"}],
    )
    assert "ContactArn" in contact
    channel = client.create_contact_channel(
        ContactId=contact["ContactArn"],
        Name="voice",
        Type="VOICE",
        DeliveryAddress={"SimpleAddress": "+12005551212"},
        DeferActivation=True,
    )
    assert "ContactChannelArn" in channel
    channel = client.create_contact_channel(
        ContactId=contact["ContactArn"],
        Name="text",
        Type="SMS",
        DeliveryAddress={"SimpleAddress": "+12005551212"},
        DeferActivation=True,
    )
    assert "ContactChannelArn" in channel
    channel = client.create_contact_channel(
        ContactId=contact["ContactArn"],
        Name="email",
        Type="EMAIL",
        DeliveryAddress={"SimpleAddress": "invalid@emailaddress.com"},
        DeferActivation=True,
    )
    assert "ContactChannelArn" in channel
    channels = client.list_contact_channels(ContactId=contact["ContactArn"])
    len(channels["ContactChannels"]).should.equal(3)


@mock_ssmcontacts
def test_create_contactchannel_validationfails():
    client = boto3.client("ssm-contacts")
    contact = client.create_contact(
        DisplayName="Test User",
        Alias="tuser",
        Type="PERSONAL",
        Plan={"Stages": []},
        Tags=[{"Key": "Environment", "Value": "Testing"}],
    )
    with pytest.raises(ClientError) as ex:
        channel = client.create_contact_channel(
            ContactId=contact["ContactArn"],
            Name="voice",
            Type="VOICE",
            DeliveryAddress={"SimpleAddress": "12005551212"},
            DeferActivation=True,
        )
    ex.value.response["Error"]["Code"].should.equal("ValidationException")
    ex.value.response["Error"]["Message"].should.contain("Invalid value provided")
    with pytest.raises(ClientError) as ex:
        channel = client.create_contact_channel(
            ContactId=contact["ContactArn"],
            Name="email",
            Type="EMAIL",
            DeliveryAddress={"SimpleAddress": "12005551212"},
            DeferActivation=True,
        )
    ex.value.response["Error"]["Code"].should.equal("ValidationException")
    ex.value.response["Error"]["Message"].should.contain("Invalid value provided")


@mock_ssmcontacts
def test_add_contact_plan_personal():
    client = boto3.client("ssm-contacts")
    contact = client.create_contact(
        DisplayName="Test User",
        Alias="tuser",
        Type="PERSONAL",
        Plan={"Stages": []},
        Tags=[{"Key": "Environment", "Value": "Testing"}],
    )
    channel1 = client.create_contact_channel(
        ContactId=contact["ContactArn"],
        Name="voice",
        Type="VOICE",
        DeliveryAddress={"SimpleAddress": "+12005551212"},
        DeferActivation=True,
    )
    channel2 = client.create_contact_channel(
        ContactId=contact["ContactArn"],
        Name="text",
        Type="SMS",
        DeliveryAddress={"SimpleAddress": "+12005551212"},
        DeferActivation=True,
    )
    channel3 = client.create_contact_channel(
        ContactId=contact["ContactArn"],
        Name="email",
        Type="EMAIL",
        DeliveryAddress={"SimpleAddress": "invalid@emailaddress.com"},
        DeferActivation=True,
    )
    client.update_contact(
        ContactId=contact["ContactArn"],
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
    contact = client.get_contact(ContactId=contact["ContactArn"])
    len(contact["Plan"]["Stages"]).should.equal(3)


@mock_ssmcontacts
def test_paginated_contacts():
    client = boto3.client("ssm-contacts")
    for i in range(0, 20):
        client.create_contact(
            DisplayName=f"Test User{i}",
            Alias=f"tuser{i}",
            Type="PERSONAL",
            Plan={"Stages": []},
            Tags=[{"Key": "Environment", "Value": "Testing"}],
        )
    pg = client.get_paginator("list_contacts")
    pager = pg.paginate()
    result = list()
    for page in pager:
        result = result + page["Contacts"]
    len(result).should.equal(20)


@mock_ssmcontacts
def test_paginated_contact_channels():
    client = boto3.client("ssm-contacts")
    contact = client.create_contact(
        DisplayName="Test User",
        Alias="tuser",
        Type="PERSONAL",
        Plan={"Stages": []},
        Tags=[{"Key": "Environment", "Value": "Testing"}],
    )
    for i in range(0, 20):
        client.create_contact_channel(
            ContactId=contact["ContactArn"],
            Name="email",
            Type="EMAIL",
            DeliveryAddress={"SimpleAddress": f"{i}invalid@emailaddress.com"},
            DeferActivation=True,
        )
    pg = client.get_paginator("list_contact_channels")
    pager = pg.paginate(**{"ContactId": contact["ContactArn"]})
    result = list()
    for page in pager:
        result = result + page["ContactChannels"]
    len(result).should.equal(20)



# @mock_ssmcontacts
# def test_update_contact():
#     client = boto3.client("ssm-contacts", region_name="ap-southeast-1")
#     resp = client.update_contact()
#
#     raise Exception("NotYetImplemented")
#
#
# @mock_ssmcontacts
# def test_update_contact_channel():
#     client = boto3.client("ssm-contacts", region_name="eu-west-1")
#     resp = client.update_contact_channel()
#
#     raise Exception("NotYetImplemented")
#
#
# @mock_ssmcontacts
# def test_delete_contact():
#     client = boto3.client("ssm-contacts", region_name="eu-west-1")
#     resp = client.delete_contact()
#
#     raise Exception("NotYetImplemented")
#
#
# @mock_ssmcontacts
# def test_delete_contact_channel():
#     client = boto3.client("ssm-contacts", region_name="eu-west-1")
#     resp = client.delete_contact_channel()
#
#     raise Exception("NotYetImplemented")
#
#
# @mock_ssmcontacts
# def test_get_contact_channel():
#     client = boto3.client("ssm-contacts", region_name="ap-southeast-1")
#     resp = client.get_contact_channel()
#
#     raise Exception("NotYetImplemented")
#
#
# @mock_ssmcontacts
# def test_list_contact_channels():
#     client = boto3.client("ssm-contacts", region_name="eu-west-1")
#     resp = client.list_contact_channels()
#
#     raise Exception("NotYetImplemented")

import boto3
import pytest
import sure  # noqa # pylint: disable=unused-import

from botocore.exceptions import ClientError
from moto import mock_ssmcontacts



def test_create_contact():
    with mock_ssmcontacts():
        client = boto3.client("ssm-contacts")
        client.create_contact(
            DisplayName="Test User",
            Alias="tuser",
            Type="PERSONAL",
            Plan={"Stages": []},
            Tags=[{"Key": "Environment", "Value": "Testing"}],
        )
        client.list_contacts()

"""Test different server responses."""
import sure  # noqa # pylint: disable=unused-import

import moto.server as server
import json

def test_ssmcontacts_list():
    backend = server.create_backend_app("ssm-contacts")
    test_client = backend.test_client()

    headers = {"X-Amz-Target": "X-Amz-Target=SSMContacts.ListContacts"}
    resp = test_client.post("/", headers=headers)
    data = json.loads(resp.data.decode("utf-8"))
    resp.status_code.should.equal(200)
    assert "Contacts" in data
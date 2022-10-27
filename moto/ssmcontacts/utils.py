PAGINATION_MODEL = {
    "list_contacts": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 10,
        "unique_attribute": "ContactArn"
    },
    "list_contact_channels": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 10,
        "unique_attribute": "ContactChannelArn"
    }
}
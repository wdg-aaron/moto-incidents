"""ssmcontacts base URL and path."""
from .responses import SSMContactsResponse

url_bases = [
    r"https?://ssm-contacts\.(.+)\.amazonaws\.com",
]



url_paths = {
    "{0}/$": SSMContactsResponse.dispatch,
}

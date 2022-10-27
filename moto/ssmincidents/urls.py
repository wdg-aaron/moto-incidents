"""ssmincidents base URL and path."""
from .responses import SSMIncidentsResponse

url_bases = [
    r"https?://ssm-incidents\.(.+)\.amazonaws\.com",
]


response = SSMIncidentsResponse()


url_paths = {
    "{0}/.*$": response.dispatch,
}

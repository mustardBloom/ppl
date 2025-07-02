from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import re

def ensure_url(string: str) -> str:
    """Ensures the given string is a URL by adding 'http://' if it doesn't start with 'http://' or 'https://'.

    Raises an error if the string is not a valid URL.

    Parameters:
        string (str): The string to be checked and possibly modified.

    Returns:
        str: The modified string that is ensured to be a URL.

    Raises:
        ValueError: If the string is not a valid URL.
    """
    if not string.startswith(("http://", "https://")):
        string = "http://" + string

        # Basic URL validation regex
    url_regex = re.compile(
        r"^(https?:\/\/)?"  # optional protocol
        r"(www\.)?"  # optional www
        r"([a-zA-Z0-9.-]+)"  # domain
        r"(\.[a-zA-Z]{2,})?"  # top-level domain
        r"(:\d+)?"  # optional port
        r"(\/[^\s]*)?$",  # optional path
        re.IGNORECASE,
    )

    if not url_regex.match(string):
        msg = f"Invalid URL: {string}"
        raise ValueError(msg)

    return string

def add_params(url: str, query_params: dict) -> str:
    """
    Adds query parameters to a given URL.

    Parameters:
        url (str): The URL containing placeholders for path parameters in the format {param}.
        query_params (dict): A dictionary of query parameters to be appended to the URL.

    Returns:
        str: The URL with the path parameters replaced and query parameters appended.

    Example:
        url = "http://example.com/api/123/details"
        query_params = {"key1": "value1", "key2": "value2"}

        result = add_params(url, query_params, path_params) # "http://example.com/api/123/details?key1=value1&key2=value2"
    """
    parsed_url = urlparse(url)
    
    query = dict(parse_qsl(parsed_url.query))
    if query_params != None:
        query.update(query_params)  # Add/Update query parameters
        
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        urlencode(query),  # Updated query string
        parsed_url.fragment
    ))
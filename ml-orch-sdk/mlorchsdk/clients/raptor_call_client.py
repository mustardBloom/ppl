from typing import Optional
import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from mlorchsdk.keymaker import get_application_context
from mlorchsdk.utils.url_utils import add_params, ensure_url
from mlorchsdk.utils.cosmosai_utils import is_production

raptor_service_headers = [
    "Correlation-Id",
    "X-PayPal-Security-Context",
    "PayPal-Client-Metadata-Id",
    "PayPal-Client-Ipaddress",
    "PayPal-Visitor-Id",
    "PayPal-Remote-Address",
    "PayPal-Entry-Point",
    "X-PayPal-FPTI",
    "PayPal-Routing-Metadata"
    ]


class RaptorCallClient:
    """
    A client for making HTTP requests to the Raptor service with support for 
    application context headers, query parameters, and SSL configuration.

    Attributes:
        url (str): The target URL for the request.
        method (str): The HTTP method to use (e.g., 'get', 'post', 'put').
        timeout (int): The timeout for the request in seconds.
        query_params (Optional[dict]): Query parameters to append to the URL.
        headers (Optional[dict]): HTTP headers to include in the request.
        body (Optional[dict]): JSON body for POST/PUT requests.
        target_service (Optional[str]): The target service name for context.
        source_service (Optional[str]): The source service name for context.
        km_application_context (Optional[str]): Application context used to request keymaker.
    """

    def __init__(
        self,
        url: str,
        method: str,
        timeout: int = 30,
        query_params: Optional[dict] = None,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        target_service: Optional[str] = None,
        source_service: Optional[str] = None,
        km_application_context: Optional[str] = None
    ):
        """
        Initializes the RaptorCallClient with the given parameters.

        Args:
            url (str): The target URL for the request.
            method (str): The HTTP method to use (e.g., 'get', 'post', 'put').
            timeout (int, optional): The timeout for the request in seconds. Defaults to 30.
            query_params (Optional[dict], optional): Query parameters to append to the URL. Defaults to None.
            headers (Optional[dict], optional): HTTP headers to include in the request. Defaults to None.
            body (Optional[dict], optional): JSON body for POST/PUT requests. Defaults to None.
            target_service (Optional[str], optional): The target service name for context. Defaults to None.
            source_service (Optional[str], optional): The source service name for context. Defaults to None.
        """
        self.url = url
        self.method = method
        self.timeout = timeout
        self.query_params = query_params or {}
        self.headers = headers or {}
        self.body = body or {}
        self.target_service = target_service
        self.source_service = source_service
        self.km_application_context = km_application_context

    def send_request(self) -> dict:
        self.url = add_params(ensure_url(self.url), self.query_params)
        self._append_application_context()
        response = self._send_request()
        response.raise_for_status()
        result = response.json()
        return result
    
    def append_passdown_headers(self, req_headers):
        for h in raptor_service_headers:
            if h in req_headers:
                self.headers[h] = req_headers.get(h)
        return self

    def _append_application_context(self) -> dict:
        ca = get_application_context(self.source_service, self.target_service, self.km_application_context)
        if ca is not None:
            self.headers["PayPal-Application-Context"] = ca
        return self.headers

    def _send_request(self):
        certs = ('client.crt', 'client.key') if is_production() else None
        session = _get_send_client()
        if self.method == 'post':
            return session.post(self.url, cert=certs, verify=False, headers=self.headers, json=self.body, timeout=self.timeout)
        if self.method == 'put':
            return session.put(self.url, cert=certs, verify=False, headers=self.headers, json=self.body, timeout=self.timeout)
        if self.method == 'get':
            return session.get(self.url, cert=certs, verify=False, headers=self.headers, timeout=self.timeout)

        raise ValueError("Raptor call with unknown request method: {}.".format(self.method))

@staticmethod
def _get_send_client():    
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    session = requests.Session()
    session.mount("https://", SSLAdapter(ssl_context))
    return session
    
class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None):
        self.ssl_context = ssl_context or ssl.create_default_context()
        super().__init__()

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )
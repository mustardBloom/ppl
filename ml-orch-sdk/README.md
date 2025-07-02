# ML-Orch-SDK

ML-Orch-SDK is a powerful software development kit designed to streamline the orchestration of machine learning workflows. It provides tools and utilities to simplify the development, deployment, and management of ML pipelines, enabling data scientists and engineers to focus on building impactful solutions.

## Installation

To install the SDK, use pip:

```bash
pip install ml_orch_sdk -i https://artifactory.paypalcorp.com/artifactory/api/pypi/paypal-python-all/simple
```

### RaptorCallClient Usage
Used to send raptor call request, will download the client certificate, fetch PayPal-Application-Context automatically from keymaker if related parameters are set correctly.

**This Clinet will not auto pass down headers like `Correlation-Id` automatically.**

If `km_application_context` is not set, will read default application context from environment variable `DEFAULT_KM_APPLICATION_CONTEXT` to download the client certs in production, client certs is a **MUST** in production, can be skipped in QA.

For production deployment, if no specific km_application_context needed to configure, please use secref ref to `mldefaultsec`, which will configure `DEFAULT_KM_APPLICATION_CONTEXT` to download client certs automatically.

```python
from mlorchsdk import RaptorCallClient

# Usually the PayPal-Application-Context value is stored with key {source_app_name}_{target_service_name}_app_context". 
# Only when PayPal-Application-Context is required to fetch, need to set the source_service and target_service
RaptorCallClient(
            url="xxx",
            method='post', # can be post/get/put
            query_params={}, # query params in the URL
            headers={}, 
            timeout=5, # in seconds, default value is 30
            body={
                "inputs": {
                    "chat_input": "my account status"
                }
            }, # one payload query example
            source_service="xxx", # The source application name of your use case in keymaker. 
            target_service="xxx", # The target service name.
            km_application_context="eyj4xxx" # Key used to fetch contents in keymaker
        ).send_request()
```

Raptor need to auto pass down headers like correlation id etc to the downstream service, we also included this part in this library. And these auto pass headers can be found [here](https://github.paypal.com/edp-aiml/ml-orch-sdk/blob/main/mlorchsdk/clients/raptor_call_client.py#L10), bellow is an example to append auto passdown headers
```python
RaptorCallClient(...).append_passdown_headers(req_headers).send_request() # req_headers is the header received, it should be a dict and contains the headers need to auto passdown to the headers 
```
### Notes:
- The lib use environment variable `CURRENT_PROFILE` to get current environment, if its value is `prod`, we regard it as `production`, otherwise is `QA`.

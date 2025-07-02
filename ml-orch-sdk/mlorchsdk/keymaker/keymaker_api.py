import requests
from mlorchsdk.utils.cosmosai_utils import keymaker_endpoint
import base64


class KeyMakerApi(object):
    
    def __init__(self, token):
        if token is None or token.strip() == '':
            raise ValueError("Application Context is required to load keyMaker Contexts")
        
        self._objects = self._load_ctx(token)

    def _load_ctx(self, token):
        try:
            response = requests.get(
                "{}/kmsapi/v1/keyobject/all".format(keymaker_endpoint()), 
                headers={"Content-Type": "application/json", "X-KM-APP-CONTEXT": token.strip()}, 
                verify=False)
            
            if response.ok:
                return response.json()
            else:
                response.raise_for_status()
        except Exception as e:  # catch ValueError to suppress token from being written to the log file
            if e.message and token in e.message:
                e.message.replace(token, "<token>")
            raise e

    @staticmethod
    def get_decoded_value(value):
        if KeyMakerApi.is_base64(value):
            return KeyMakerApi.get_decoded_value(base64.b64decode(value).decode())
        return value
    
    @staticmethod
    def is_base64(s: str) -> bool:
        try:
            return base64.b64encode(base64.b64decode(s)) == s.encode()
        except Exception:
            return False

    def get_context(self):
        return self._objects

    def get_specific_nonkeys_value(self, key_name: str, raise_exception: bool = False):
        nonkeys = self._objects["nonkeys"]
        if nonkeys:
            for nonkey in nonkeys:
                key = nonkey['nonkey']['name']
                state = nonkey['nonkey']['state']
                if key_name.strip() == key and state == 'enabled':
                    return self.get_decoded_value(nonkey['nonkey']['encoded_key_data'])
        if raise_exception:
            raise ValueError(key_name, "Key doesn't exist in keymaker.")
        else:
            return None

    @staticmethod    
    def build_paypal_application_context_key(source_service, target_service):
        return "{}_{}_app_context".format(source_service, target_service)


        
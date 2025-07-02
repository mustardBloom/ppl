from mlorchsdk.utils.cosmosai_utils import keymaker_cache_timeout_in_days, is_production, default_km_app_context
from mlorchsdk.cache import InMemoryCache
from .keymaker_api import KeyMakerApi
import io, textwrap

__cached = InMemoryCache(keymaker_cache_timeout_in_days() * 24 * 3600)

def download_certs(ctx):
    if not is_production() or __cached.get("client_cert") is not None:
        return
        
    if 'keystores' not in ctx:
        raise ValueError("The application context can't load keystores!")
        
    for keystore in ctx['keystores']:
        if keystore['keystore']['name'] == 'custom_to_altus_mutual_hrz_keystore':
            keystore = keystore['keystore']
            with io.StringIO() as cert_out, io.StringIO() as key_out:
                for entry in keystore['entries']:
                    if entry['entry_type'] == 'KeyEntry':
                        data = entry['entry']['keypair']
                        if data['state'] != 'enabled':
                            continue

                        for cert in data['certificates']:
                            raw = cert['encoded_cert']
                            print(f'-----BEGIN CERTIFICATE-----', file=cert_out)

                            for line in textwrap.wrap(raw, width=65):
                                print(line, file=cert_out)

                            print(f'-----END CERTIFICATE-----', file=cert_out)

                        key = data['private_key']['encoded_private_key']
                        print(f'-----BEGIN PRIVATE KEY-----', file=key_out)
                        for line in textwrap.wrap(key, width=65):
                            print(line, file=key_out)
                        print(f'-----END PRIVATE KEY-----', file=key_out)
                with open('client.crt', 'w') as f1:
                    f1.write(cert_out.getvalue())
                with open('client.key', 'w') as f2:
                    f2.write(key_out.getvalue())

        __cached.set("client_cert", True)

def get_application_context(sorce_service, target_service, app_context):
    cached_key = "{}_{}_ca".format(sorce_service, target_service)
    if __cached.get(cached_key) is not None:
        return __cached.get(cached_key)
        
    if app_context is None or app_context.strip() == '':
        if target_service is not None and target_service.strip() != '':
            raise ValueError(""""
            "Keymaker Application Context is required to get the PayPal-Application-Context, "
            "please set the global environment varible KM_APPLICATION_CONTEXT or remove the target service configuration."
            """)
        if not is_production():
            return None
        
        keymakerapi = KeyMakerApi(default_km_app_context())
    else:
        keymakerapi = KeyMakerApi(app_context)

    download_certs(keymakerapi.get_context())        
    value = keymakerapi.get_specific_nonkeys_value(KeyMakerApi.build_paypal_application_context_key(sorce_service, target_service), raise_exception=False)
    __cached.set(cached_key, value)
    return value
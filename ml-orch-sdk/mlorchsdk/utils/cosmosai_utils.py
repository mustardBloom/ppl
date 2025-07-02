import os

def is_production():
    return os.environ.get("CURRENT_PROFILE", "DEV").lower() in ["prod"]

def keymaker_endpoint():
     return "https://keymakerapi.g.paypalinc.com:21358" if is_production() else "https://keymakerapi-vip.qa.paypal.com"

def default_km_app_context():
    return os.getenv("DEFAULT_KM_APPLICATION_CONTEXT", None)

def keymaker_cache_timeout_in_days():
    return int(os.getenv("KEYMAKER_CACHE_TIMEOUT_IN_DAYS", 7))
import os
class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ['SECRET_KEY']
    REGISTRY_BASE_URL = os.environ['REGISTRY_BASE_URL']
    REGISTRY_CONSUMER_KEY = os.environ['REGISTRY_CONSUMER_KEY']
    REGISTRY_CONSUMER_SECRET = os.environ['REGISTRY_CONSUMER_SECRET']
    BASE_URL = os.environ['BASE_URL']
    WWW_BASE_URL = os.environ['WWW_BASE_URL']
    TWILIO_ACCOUNT_ID = os.environ['TWILIO_ACCOUNT_ID']
    TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
    TWILLIO_PHONE_NUMBER = os.environ['TWILLIO_PHONE_NUMBER']

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False



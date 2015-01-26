import os
from flask import Flask
from flask_oauthlib.client import OAuth
from flask.ext.cors import CORS

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
oauth = OAuth(app)

from redis import Redis
import urllib
url = urllib.parse.urlparse(app.config.get('REDISCLOUD_URL', 'redis://user:@localhost:6379'))
redis_client = Redis(host=url.hostname, port=url.port, password=url.password)

if 'SENTRY_DSN' in os.environ:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, dsn=os.environ['SENTRY_DSN'])

from start_organisation import views

from start_organisation import app
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
os.environ['DEBUG'] = 'true'
app.run(host="0.0.0.0", port=int(os.environ['PORT']), debug=True)

import os
import hashlib
import json

import dateutil.parser
from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for,
    session,
    flash,
    abort,
    current_app
)

import requests
import jinja2
from flask_oauthlib.client import OAuth, OAuthException
from twilio.rest import TwilioRestClient
import start_organisation.forms as forms
from start_organisation.order import Order
from start_organisation import app, oauth
from decorators import registry_oauth_required

from start_organisation import redis_client, locator

service = {
  "name": "Start organisation",
  "minister": "Minister for business",
  "registers": ["Licences", "Organisations"],
  "slug": "start-organisation",
  "service_base_url_config": "ORGANISATIONS_BASE_URL",
  "policies": [],
  "legislation": [],
  "guides": [
    {"title": "Guide for Directors", "slug": "directors"},
    {"title": "Guide for Trustees", "slug": "trustees"},
    {"title": "Types of organisation", "slug": "types"}
  ]
}


registry = oauth.remote_app(
    'registry',
    consumer_key=app.config['REGISTRY_CONSUMER_KEY'],
    consumer_secret=app.config['REGISTRY_CONSUMER_SECRET'],
    request_token_params={'scope': 'organisation:add person:view notice:add'},
    base_url=app.config['REGISTRY_BASE_URL'],
    request_token_url=None,
    access_token_method='POST',
    access_token_url='%s/oauth/token' % app.config['REGISTRY_BASE_URL'],
    authorize_url='%s/oauth/authorize' % app.config['REGISTRY_BASE_URL']
)


def log_traceback(logger, ex, ex_traceback=None):
    import traceback
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    logger.info(tb_lines)


def make_random_token():
    random =  hashlib.sha1(os.urandom(128)).hexdigest()
    random = random.upper()
    return "%s-%s-%s-%s" % (random[0:4], random[5:9], random[10:14], random[15:19])

#auth helper
@registry.tokengetter
def get_registry_oauth_token():
    return session.get('registry_token')

#views
@app.route("/")
def index():
    return redirect("%s/organisations" % app.config['WWW_BASE_URL'])

@app.route("/start")
@registry_oauth_required
def start():
    return redirect(url_for('choose_type'))

@app.route("/choose-type", methods=['GET', 'POST'])
@registry_oauth_required
def choose_type():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        order = Order()

    locator.send_message({ "active": "organisations" })

    # create form and add options
    form = forms.StartOrganisationTypeForm(request.form)
    form.organisation_type.value = order.organisation_type

    if request.method == 'POST':
        order.organisation_type = form.organisation_type.data
        session['order'] = order.to_dict()
        return redirect(url_for('start_details'))

    return render_template('start-type.html', form=form)

@app.route("/start/details", methods=['GET', 'POST'])
@registry_oauth_required
def start_details():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        return redirect(url_for('choose_type'))

    form = forms.StartOrganisationDetailsForm(request.form)

    if request.method == 'POST':
        order.name = form.name.data
        order.activities = form.activities.data
        session['order'] = order.to_dict()
        return redirect(url_for('find_address'))

    return render_template('start-details.html', form=form)


@app.route("/start/postcode-lookup", methods=['GET', 'POST'])
@registry_oauth_required
def find_address():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        return redirect(url_for('choose_type'))
    form = forms.StartOrganisationPostcodeForm(request.form)
    if request.method == 'POST':
        postcode = form.postcode.data
        address_form = forms.StartOrganisationChooseAddress()
        if postcode:
            uri = "%s/addresses" % app.config['REGISTRY_BASE_URL']
            response = requests.get(uri, params={'postcode': postcode})
            if response.status_code == 200:
                #TODO - store uri of address?
                addresses = [(item['address'], item['address']) for item in response.json()]
                addresses.sort(key=lambda address: address[1])
                address_form.address_choices.choices = addresses
        else:
            address_form.address_choices.choices = [('Transworld House, 100 Borchester City Road, Borchester, BO1Y 2BP','Transworld House, 100 Borchester City Road, Borchester, BO1Y 2BP')]

        return render_template('choose-address.html', form=address_form)

    return render_template('postcode-lookup.html', form=form)


@app.route("/start/choose-address", methods=['POST'])
@registry_oauth_required
def choose_address():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        return redirect(url_for('choose_type'))

    current_app.logger.info('selected address %s' % request.form['address_choices'])
    order.address = request.form['address_choices']
    session['order'] = order.to_dict()

    return redirect(url_for('start_invite'))


@app.route("/start/invite", methods=['GET', 'POST'])
@registry_oauth_required
def start_invite():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        return redirect(url_for('choose_type'))

    form = forms.StartOrganisationInviteForm(request.form)

    if request.method == 'POST':
        if form.validate():

            #this can be used to highlight another service/platform being used
            if form.people.data:
                locator.send_message({ "active": "sms" })

            #send sms
            client = TwilioRestClient(app.config['TWILIO_ACCOUNT_ID'], app.config['TWILIO_AUTH_TOKEN'])
            for person in form.people:
                order.directors.append(person.fullname.data)
                if person.phone.data:
                    message = "Please visit GOV.UK and enter the following code to verify you wish to become a director of '%s': %s" % (order.name, make_random_token())
                    client.sms.messages.create(to=person.phone.data, from_=app.config['TWILLIO_PHONE_NUMBER'], body=message)

            #next
            return redirect(url_for('start_register'))
        else:
            current_app.logger.info('invalid form %s' % form.errors)

    return render_template('start-invite.html', form=form)

@app.route("/start/register", methods=['GET', 'POST'])
@registry_oauth_required
def start_register():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        return redirect(url_for('choose_type'))

    form = forms.StartOrganisationRegistrationForm(request.form)

    if request.method == "POST":
        if form.validate():
            order.register_data = form.register_data.data
            order.register_employer = form.register_employer.data
            order.register_construction = form.register_construction.data
            session['order'] = order.to_dict()
            return redirect(url_for('start_taxes'))

    return render_template('start-register.html', form=form)

@app.route("/start/taxes", methods=['GET', 'POST'])
@registry_oauth_required
def start_taxes():
    if request.method == "POST":
        return redirect(url_for('start_review'))
    return render_template('start-taxes.html')


@app.route("/start/review", methods=['GET', 'POST'])
@registry_oauth_required
def start_review():
    order_data = session.get('order', None)
    if order_data:
        order = Order(**order_data)
    else:
        return redirect(url_for('choose_type'))

    form = forms.StartOrganisationReviewForm(request.form)

    if request.method == 'POST':
        if form.validate():
            data = {
                'organisation_type' : order.organisation_type,
                'name' : order.name,
                'activities' : order.activities,
                'register_data' : order.register_data,
                'register_employer' : order.register_employer,
                'register_construction' : order.register_construction,
                'directors' : order.directors,
                'full_address': order.address
            }

            response = registry.post('/organisations', data=data, format='json')
            if response.status == 201:
                session.pop('order', None)
                return redirect(url_for('start_done'))
            else:
                flash('Something went wrong', 'error')

    return render_template('start-review.html', form=form, order=order)

@app.route("/start/done")
def start_done():
    session.clear()
    return render_template('start-done.html')

@app.route("/manage")
@registry_oauth_required
def manage():
    #for now, just redirect to the last one that was created
    uri = "%s/organisations" % app.config['REGISTRY_BASE_URL']
    response = requests.get(uri)
    if response.status_code == 200:
        organisations = response.json()
        organisation_uri = organisations[len(organisations) -1]['uri']
        organisation_id = organisation_uri.split("/")[len(organisation_uri.split("/")) - 1]
        return redirect(url_for('manage_organisation', organisation_id=organisation_id))
    else:
        abort(404)

@app.route("/signout")
def signout():
    session.clear()
    return redirect("%s/start" % app.config['WWW_BASE_URL'])

@app.route("/manage/<organisation_id>")
@registry_oauth_required
def manage_organisation(organisation_id):

    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    todos = _get_todos(organisation_id)
    unread_todos = [todo for todo in todos if not todo['read']]

    return render_template("manage.html", organisation=organisation, service=service, organisation_id=organisation_id, selected_tab='overview', todos=todos, unread_todos=unread_todos)

@app.route("/manage/<organisation_id>/licences")
@registry_oauth_required
def manage_organisation_licences(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    todos = _get_todos(organisation_id)

    return render_template("licences.html", organisation=organisation, service=service, organisation_id=organisation_id, selected_tab='licences', todos=todos)


@app.route("/manage/<organisation_id>/tax")
@registry_oauth_required
def manage_organisation_tax(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    todos = _get_todos(organisation_id)

    return render_template("tax.html", organisation=organisation, service=service, organisation_id=organisation_id, selected_tab='tax', todos=todos)

@app.route("/manage/<organisation_id>/employees")
@registry_oauth_required
def manage_organisation_employees(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    todos = _get_todos(organisation_id)

    return render_template("employees.html", organisation=organisation, service=service, organisation_id=organisation_id, selected_tab='employees', todos=todos)

#apply for a licence
@app.route("/manage/<organisation_id>/licences/apply", methods=['GET', 'POST'])
@registry_oauth_required
def licence_apply_type(organisation_id):

    session['resume_url'] = '/manage/'+organisation_id+'/licences/apply'

    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    form = forms.LicenceApplicationForm(request.form)
    if form.validate_on_submit():
        licences = []
        for field in form:
            if field.type == "BooleanField" and field.data:
                licences.append({"licence_type": field.description})

        #TODO if no licences noop
        session['licences'] = licences

        return redirect(url_for('licence_apply_address', organisation_id=organisation_id))

    return render_template("licence-apply-type.html", organisation=organisation, form=form)

#apply for a licence
@app.route("/manage/<organisation_id>/licences/apply/address", methods=['GET', 'POST'])
@registry_oauth_required
def licence_apply_address(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    form = forms.LicenceAddressForm(request.form)
    form.licence_address.choices = [('registered-address', organisation['full_address']), ("another-address", "Another address")]

    if form.validate_on_submit():
        licences = session.get('licences', [])
        if licences:
            if form.licence_address.data == 'registered-address':
                licence_address = organisation['full_address']
            # else actually implement other address part of form
            # and get those details but for now hard code some default
            else:
                licence_address = "Transworld House, 100 City Road, London, EC1Y 2BP"

            data = {"subject_uri": organisation['uri'],
                    "subject_name": organisation['name'],
                    "licence_address": licence_address,
                    "licences": licences }

            response = registry.post('/notices', data=data, format='json')

            _set_todos(organisation_id, licences)

            session.pop('licences', None)

            return redirect(url_for('licence_apply_done', organisation_id=organisation_id))


        else:
            current_app.logger.info('we should not be here')
            return redirect(url_for('licence_apply_address', organisation_id=organisation_id))

    return render_template("licence-apply-address.html", organisation=organisation, form=form)

@app.route("/manage/<organisation_id>/licences/apply/done")
@registry_oauth_required
def licence_apply_done(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    return render_template("licence-apply-done.html", organisation=organisation)

@app.route("/")
@registry_oauth_required
def todo_list(organisation_id):
    uri = "%s/organisations/%s" % (app.config['REGISTRY_BASE_URL'], organisation_id)
    response = requests.get(uri)
    if response.status_code == 200:
        organisation = response.json()
    else:
        abort(404)

    todos = _get_todos(organisation_id, mark_read=True)

    return render_template("todos.html", organisation=organisation, service=service, organisation_id=organisation_id, todos=todos)

@app.route('/verify')
def verify():
    _scheme = 'https'
    if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', False) == 'true':
        _scheme = 'http'
    return registry.authorize(callback=url_for('verified', _scheme=_scheme, _external=True))

@app.route('/verified')
def verified():
    resp = registry.authorized_response()

    if resp is None or isinstance(resp, OAuthException):
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registry_token'] = (resp['access_token'], '')
    session['refresh_token'] = resp['refresh_token']
    if session.get('resume_url'):
        resume_url = session.get('resume_url')
        session.pop('resume_url', None)
        return redirect(resume_url)
    else:
        return redirect(url_for('index'))


@app.route('/check')
def check_name():
    name = request.args.get('name')
    uri = "%s/organisations" % app.config['REGISTRY_BASE_URL']
    response = requests.get(uri, params={'exact_match': name})
    organisations = response.json()
    if len(organisations) > 0:
        return 'OK', 200
    return 'NOT FOUND', 404


# These are just to hook up some notifications and
# don't let then break stuff. swallow exceptions and carry on
def _get_todos(organisation_id, mark_read=False):
    import sys
    all_todos = []
    try:
        todos = redis_client.get(organisation_id)
        if todos:
            import pickle
            all_todos = pickle.loads(todos)
            #mark all as read
            if mark_read:
                for todo in all_todos:
                    todo['read'] = True
            _set_todos(organisation_id, all_todos, replace=True)
    except Exception as e:
        log_traceback(current_app.logger, e)

    return all_todos


def _set_todos(organisation_id, todos, replace=False):
    import pickle
    import sys
    import uuid

    for todo in todos:
        if not todo.get('uuid'):
            todo['uuid'] = uuid.uuid4()
        # fake up a hearing date
        if not todo.get('hearing_date'):
            from datetime import timedelta, datetime
            from random import randint
            start_date = datetime.now()
            end_date = timedelta(days=randint(1,90))
            hearing_date = start_date + end_date
            todo['hearing_date'] = hearing_date
        if not todo.get('read'):
            todo['read'] = False
    try:
        if todos:
            if replace:
                redis_client.set(organisation_id, pickle.dumps(todos))
            else:
                all_todos = []
                existing_todos = redis_client.get(organisation_id)
                if existing_todos:
                    all_todos = pickle.loads(existing_todos)
                all_todos.extend(todos)
                redis_client.set(organisation_id, pickle.dumps(all_todos))
        else:
            redis_client.delete(organisation_id)
    except Exception as e:
        log_traceback(current_app.logger, e)

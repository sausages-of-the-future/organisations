import os
import jinja2
import forms
import json
import hashlib
from order import Order
import dateutil.parser
from flask import Flask, request, redirect, render_template, url_for, session, flash, abort
from flask.json import JSONEncoder
from flask_oauthlib.client import OAuth
from fishing import app, oauth

registers = oauth.remote_app(
    'registers',
    consumer_key='c1aedf2d9fa74884930392850712c0a6',
    consumer_secret='00952aff578e476b93c7a10e9a1cbb05',
    request_token_params={'scope': 'person:view personal_licence:view personal_licence:add'},
    base_url='http://localhost:5000',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='http://localhost:5000/oauth/token',
    authorize_url='http://localhost:5000/oauth/authorize'
)

#filters
@app.template_filter('reference_number')
def reference_number_filter(s):
    split = s.split('/')
    return split[len(split) - 1].upper()

@app.template_filter('format_money')
def format_money_filter(value):
    return "{:,.2f}".format(value)

@app.template_filter('pad_reference')
def pad_reference(s):
    n = 4
    result = [s[i:i+n] for i in range(0, len(s), n)]
    return " ".join(result)

#auth helper
@registers.tokengetter
def get_registers_oauth_token():
    return session.get('registers_token')

#views
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/buy", methods=['GET', 'POST'])
def buy():

    if not session.get('registers_token', False):
        return redirect(url_for('verify'))

    order = None
    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)
    else:
        #get the person associated with this token
        about = registers.get('/about').data
        person = registers.get(about['person'].replace(registers.base_url, '')).data
        existing_licences = registers.get('/personal-licences').data
        disabled = False
        order = Order(dateutil.parser.parse(person['born_at']), existing_licences, disabled, app.config['BASE_URL'])
        session['order'] = order.to_dict()

    form = forms.LicenceTypeForm(request.form)

    if request.method == 'POST':
        if form.validate():
            order.licence_type = form.licence_type.data
            order.duration = form.duration.data
            order.starts_at = None
            session['order'] = order.to_dict()
            return redirect(url_for('pay'))

    return render_template('buy.html', order=order, form=form)

@app.route("/pay", methods=["GET", "POST"])
def pay():

    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)
    else:
        return redirect(url_for('index'))

    #form
    form = forms.PaymentForm(request.form)

    if request.method == 'POST':
        if form.validate():
            data = {
                'licence_type_uri': order.licence_type_uri(),
                'starts_at': '2013-01-01',
                'ends_at': '2014-01-01'
                }
            response = registers.post('/personal-licences', data=data, format='json')
            if response.status == 201:
                flash('Licence granted', 'success')
                session.pop('order', None)
                return redirect(url_for('your_licences'))
            else:
                flash('Something went wrong', 'error')
    return render_template('pay.html', order=order, form=form)

@app.route("/your-licences")
def your_licences():
    if not session.get('registers_token', False):
        return redirect(url_for('verify'))
    licences = registers.get('/personal-licences').data
    return render_template('your-licences.html', licences=licences)

@app.route("/licences")
def licences():
    return render_template('licences.html')

@app.route("/licences/salmon-trout")
def licence_salmon_trout():
    return render_template('salmon-trout.html')

@app.route("/licences/coarse")
def coarse():
    return render_template('coarse.html')

@app.route("/licences/thames")
def thames():
    return render_template('thames.html')

@app.route("/check")
def check():
    return render_template('check.html')

@app.route("/check/result")
def check_result():
    if not session.get('registers_token', False):
        return redirect(url_for('verify'))

    search = request.args.get('q', False)
    if not search:
        abort(404)

    result = registers.get('/personal-licences/%s' % search.replace(' ', ''))
    licence = None
    if not result.status == 200 and result.status != 404:
        abort(result.status)
    if result.status == 200:
        licence = result.data

    return render_template('check-result.html', licence=licence)

@app.route('/verify')
def verify():
    return registers.authorize(callback=url_for('verified', _external=True))

@app.route('/verified')
def verified():

    resp = registers.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registers_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


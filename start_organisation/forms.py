import json
from flask_wtf import Form
from wtforms import TextField, TextAreaField, RadioField, BooleanField, FormField, IntegerField, FieldList, DateField, SelectField, validators
from wtforms.fields import html5

class StartOrganisationTypeForm(Form):
    organisaiton_types = [
        ("public-limited-company", "Public Limited Company"),
        ("private-limited-company", "Private company limited by guarantee"),
        ("ordinary-business-partnership", "Ordinary Business Partnership"),
        ("limited-partnership", "Limited Partnership"),
        ("limited-liability-partnership", "Limited Liability Partnership"),
        ("unincorperated-association", "Unincorporated Association"),
        ("charity", "Charity"),
        ("charitable-incorperated-organisation", "Charitable Incorporated Organisation"),
        ("cooperative", "Co-operative"),
        ("industrial-and-provident-society", "Industrial and Provident Society"),
        ("community-interest-company", "Community Interest Company")
    ]
    organisation_type = RadioField('Organisation type', choices=organisaiton_types, validators=[validators.required()])

class StartOrganisationDetailsForm(Form):
    name = TextField('Organisation name', validators=[validators.required()])
    activities = TextAreaField('Main business activities', validators=[validators.required()])

class StartOrganisationRegistrationForm(Form):
    register_data = BooleanField("Will the organisation be collecting and holding data about individuals? (Data Protection Register)")
    register_employer = BooleanField("Will the organisation be employing people? (Employer register and PAYE Tax)")
    register_construction = BooleanField("Will the organisation pay subcontractors to do construction work?")

class PersonForm(Form):
    name = TextField('Name', validators=[validators.required()])
    position = TextField('Position', validators=[validators.required()])
    phone = html5.TelField('Phone number', validators=[validators.required()])

class StartOrganisationInviteForm(Form):
    user_is_director = SelectField('Are you one of the directors?', choices=[("True", "Yes"), ("False", "No")])
    director_count = SelectField("Other than yourself - how many other directors are there?", choices=[("0", "0"), ("1", "1"),("2", "2"), ("3", "3"),("4", "4"),("5", "5")], default=0)
    method = RadioField("", default="sms", choices=[("sms", "Send codes as a text message"), ("print", "Print one-use codes")])
    people = FieldList(FormField(PersonForm), min_entries=0)

class StartOrganisationReviewForm(Form):
    confirm = BooleanField("I confirm that the details above are correct (it is an offence to provide information which you know to be incorrect.)", validators=[validators.DataRequired("You must confirm that the details are correct (it is an offence to provide information which you know to be incorrect.)")])

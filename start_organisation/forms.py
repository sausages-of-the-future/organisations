import json
import wtforms
from flask_wtf import Form
from wtforms import TextField, TextAreaField, RadioField, BooleanField, FormField, IntegerField, FieldList, DateField, SelectField, validators
from wtforms.fields import html5

class StartOrganisationTypeForm(Form):
    organisation_types = [
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
    organisation_type = RadioField('Organisation type', choices=organisation_types, validators=[validators.required()])

class StartOrganisationDetailsForm(Form):
    name = TextField('Organisation name', validators=[validators.required()])
    activities = TextAreaField('Main business activities', validators=[validators.required()])

class StartOrganisationRegistrationForm(Form):
    register_data = BooleanField("Will the organisation be collecting and holding data about individuals? (Data Protection Register)")
    register_employer = BooleanField("Will the organisation be employing people? (Employer register and PAYE Tax)")
    register_construction = BooleanField("Will the organisation pay subcontractors to do construction work?")

class PersonForm(wtforms.form.Form):

    # this form inherits from wtforms.form.Form rather than
    # flask_wtf.Form. The latter is actually a secure form
    # which would mean each Person form in the Fieldist
    # of StartOrganisationInviteForm would need a csrf_token of their own
    # and the forms are constructed client side.
    # http://stackoverflow.com/questions/15649027/wtforms-csrf-flask-fieldlist

    fullname = TextField('Name', validators=[validators.required()])
    position = TextField('Position', validators=[validators.required()])
    phone = html5.TelField('Phone number', validators=[validators.required()])

class StartOrganisationInviteForm(Form):
    user_is_director = SelectField('Are you one of the directors?', choices=[("True", "Yes"), ("False", "No")])
    director_count = SelectField("Other than yourself - how many other directors are there?", choices=[("0", "0"), ("1", "1"),("2", "2"), ("3", "3"),("4", "4"),("5", "5")], default=0)
    method = RadioField("", default="sms", choices=[("sms", "Send codes as a text message"), ("print", "Print one-use codes")])
    people = FieldList(FormField(PersonForm), min_entries=0)

class StartOrganisationReviewForm(Form):
    confirm = BooleanField("I confirm that the details above are correct (it is an offence to provide information which you know to be incorrect.)", validators=[validators.DataRequired("You must confirm that the details are correct (it is an offence to provide information which you know to be incorrect.)")])

class StartOrganisationPostcodeForm(Form):
    postcode = TextField('Enter postcode', validators=[validators.required()])


class StartOrganisationChooseAddress(Form):
    address_choices = RadioField('Address choice', choices=[], validators=[validators.required()])

class LicenceApplicationForm(Form):
    use_cctv = BooleanField("Use CCTV systems", description="Licence to use CCTV systems.")
    discharge_effluent = BooleanField("Discharge trade effluent", description="Licence to discharge trade effluent.")
    tables_chairs_on_pavement = BooleanField("Put tables or chairs on the pavement", description="Licence to put tables or chairs on the pavement.")
    sell_alcohol = BooleanField("Sell alcoholic drinks", description="Licence to sell alcoholic drinks.")

class LicenceAddressForm(Form):

    licence_address = RadioField('What address do you require the licences for?', validators=[validators.required()])


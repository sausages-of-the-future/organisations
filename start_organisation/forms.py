import json
from wtforms import Form, TextField, TextAreaField, RadioField, BooleanField, FormField, IntegerField, FieldList, DateField, SelectField,  validators

class StartOrganisationTypeForm(Form):
    organisaiton_types = [
        ("public-limited-company", "Public Limited Company"),
        ("private-limited-company", "Private company limited by guarantee"),
        ("ordinary-business-partnership", "Ordinary Business Partnership"),
        ("limited-partnership", "Limited Partnership"),
        ("limited-liability-partnership", "Limited Liability Partnership"),
        ("unincorperated-association", "Unincorperated Association"),
        ("charity", "Charity"),
        ("charitable-incorperated-organisation", "Charitable Incorperated Organisation"),
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
    phone = IntegerField('Phone number', validators=[validators.required()])

class StartOrganisationInviteForm(Form):
    user_is_director = SelectField('Are you one of the directors?', choices=[("True", "Yes"), ("False", "No")])    
    director_count = IntegerField("Other than yourself - how many other directors are there?", default=0, validators=[validators.NumberRange(min=0, max=20, message=None)])
    method = RadioField("", default="sms", choices=[("sms", "Send codes as a text message"), ("print", "Print one-use codes")])
    people = FieldList(FormField(PersonForm), min_entries=1)

class StartOrganisationReviewForm(Form):
    confirm = BooleanField("I confirm that the details above are correct", validators=[validators.DataRequired("You must confirm that the details are correct")])
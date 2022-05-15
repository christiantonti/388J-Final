from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils_nodb import FormField
import base64
import uuid


@login_manager.user_loader
def load_user(user_id):
    return User.objects(uid=user_id).first()


class User(db.Document, UserMixin):
    uid = db.StringField(required=True, primary_key=True, regex="^\d{9}$", min_length=9, max_length=9)
    email = db.EmailField(required=True, unique=True)
    phone = db.StringField(required=True, regex="^\d{10}$", min_length=10, max_length=10)
    password = db.StringField(required=True)
    fname = db.StringField(required=True, regex="\w+", max_length=15)
    lname = db.StringField(required=True, regex="\w+", max_length=25)
    isAdmin = db.BooleanField(required=True, default=False)
    profile_pic = db.ImageField()

    # Returns unique string identifying our object
    def get_id(self):
        return self.uid

    # checks if user has admin permissions
    def is_admin(self):
        return self.isAdmin

class PointLog(db.Document):
    uuid = db.UUIDField(binary=False, required=True, default=uuid.uuid4, primary_key=True)
    user = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    points = db.IntField(required=True, min_value=-100, max_value=100)
    reason = db.StringField(required=True)
    date = db.StringField(required=True, default=datetime.now().strftime("%m/%d/%y @ %H:%M:%S"))

# ***** CUSTOM FORM STUFF *****
class FormObject(db.Document):
    uuid = db.UUIDField(binary=False, required=True, default=uuid.uuid4, primary_key=True)
    name = db.StringField(required=True)
    # list of field types (to be constructed when form is requested)
    fields = db.ListField(db.EnumField(FormField, default=FormField.STRING_FIELD, required=True))
    # list of field labels (to be displayed)
    labels = db.ListField(db.StringField(required=True, default="Label", max_length=100))
    # due date for form, not required
    due_by = db.DateTimeField()
    # ID for a linked event, not required
    event_id = db.StringField()

class FormSubmission(db.Document):
    uuid = db.UUIDField(binary=False, required=True, default=uuid.uuid4, primary_key=True)
    user = db.ReferenceField(User, required=True, reverse_delete_rule=db.CASCADE)
    # for some godforsaken reason ONLY THIS one needs dbref=True
    form = db.ReferenceField(FormObject, dbref=True, required=True, reverse_delete_rule=db.CASCADE)
    # idk how to make a heterogenous submission, so all responses will be string casted
    data = db.ListField(db.StringField(required=True, default="N/A"))
    completed_dt = db.DateTimeField(default=datetime.now())


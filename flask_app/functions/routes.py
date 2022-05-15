from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required
from mongoengine.queryset.visitor import Q
from datetime import datetime
import json
from flask_app.utils_nodb import FormField

from ..forms import MemberSearchForm, LoadFormObject
from ..models import User, FormObject, FormSubmission
from ..utils import get_b64_img
from ..utils_nodb import date_str, now
# get calendar api route methods
from ..calendar.routes import getEvents

functions = Blueprint("functions", __name__)

""" ************ View functions ************ """


@functions.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@functions.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@functions.route("/members", methods=["GET", "POST"])
@login_required
def members():
    form = MemberSearchForm()

    if form.validate_on_submit():
        query = form.query.data
        return redirect(url_for("functions.members", query=query))
    
    # check for GET arg
    query = request.args.get('query')
    if(query):
        users = User.objects(Q(fname__icontains=query) | Q(lname__icontains=query))
    else:
        users = User.objects()
    for user in users:
        user.img = get_b64_img(user.uid)
    return render_template("members.html", users=users, form=form, query=query)

@functions.route("/forms", methods=["GET"])
@login_required
def forms():
    c_forms = FormSubmission.objects(user=current_user).only('uuid', 'form', 'completed_dt').order_by('-completed_dt')
    completed_ids = [form.form.uuid for form in c_forms]
    u_forms = FormObject.objects(uuid__nin=completed_ids).order_by('+due_by')
    # add is_late to each form
    for form in u_forms:
        form.is_late = (now() > form.due_by)
        form.due_by = date_str(form.due_by)
    for sub in c_forms:
        sub.is_late = (sub.completed_dt > sub.form.due_by)
        sub.completed_dt = date_str(sub.completed_dt)
    return render_template("forms.html", u_forms=u_forms, c_forms=c_forms)

@functions.route("/viewForm", methods=["GET", "POST"])
@login_required
def viewForm():
    # check ID was passed
    if request.args.get('id') == None:
        flash("No form ID provided!")
        return redirect(url_for('functions.forms'))
    uuid = request.args.get('id')
    form_obj = FormObject.objects(uuid=uuid).first()
    if form_obj:
        # first check if they already completed it
        if FormSubmission.objects(user=current_user, form=form_obj).first():
            flash('Form already completed!')
            return redirect(url_for('functions.forms'))
        # now, construct custom form
        form = LoadFormObject(form_obj)

        # since form only exists here we check for POST here
        if form.validate_on_submit():
            # convert submission into strings, cut off submit/csrf
            data = [str(i) for i in list(form.data.values())[:-2]]
            submission = FormSubmission(user=current_user, form=FormObject.objects(uuid=uuid).first(), data=data, completed_dt=now())
            submission.save()
            flash("Successfully submitted form!")
            return redirect(url_for('functions.forms'))
        elif form.errors:
            flash(form.errors)

        return render_template("form_complete.html", name=form_obj.name, form=form)
    else:
        flash("Form not found")
        return redirect(url_for('functions.forms'))

# ***** EVENTS ROUTES *****
@functions.route("/events", methods=["GET"])
@login_required
def events():
    events = json.loads(getEvents().data)
    new_events = []
    for event in events:
        new_event = {}
        new_event['title'] = event.get('summary')
        new_event['description'] = event.get('description', 'No Description')
        new_event['start'] = date_str(datetime.strptime(event.get('start',{}).get('dateTime')[:-6], "%Y-%m-%dT%H:%M:%S"))
        form_id = FormObject.objects(event_id=event.get('id')).first()
        if form_id:
            new_event['form_link'] = f"/viewForm?id={form_id['uuid']}"
        new_events.append(new_event)
    return render_template("events.html", events=new_events)
import re
from flask import Blueprint, render_template, url_for, redirect, request, flash, jsonify
from flask_login import current_user
from datetime import datetime
from ..forms import PointsForm, ViewLogsForm, createCustomCreationForm, EventCreationForm
from ..models import FormObject, FormSubmission, User, PointLog
from ..utils import get_points, current_time
from ..utils_nodb import FormField, date_str
from ..calendar.routes import createEvent

admin = Blueprint("admin", __name__)

""" ************ View functions ************ """

# CHECK FOR ADMIN STATUS FOR EVERY REQUEST
# yes, I know that I could use Flask-Login roles but its a lot of work to just create 2 roles
# this should have effectively the same functionality
@admin.before_request
def check_role():
    if current_user.isAdmin != True:
        flash('Insufficient Permissions!')
        return redirect(url_for('functions.index'))

# ***** POINT TRACKING ROUTES *****
@admin.route("/points", methods=["GET", "POST"])
def points():
    mform = PointsForm()
    vform = ViewLogsForm()
    users = User.objects()
    # populate dropdown choices
    choices = [(user.uid, f'{user.fname} {user.lname}') for user in users]
    mform.uid.choices = choices
    vform.uid.choices = choices

    # can pass in uid GET param to pre-fill stuff
    sel_uid = request.args.get('uid')

    if mform.validate_on_submit():
        user = User.objects(uid=mform.uid.data).first()
        if user:
            log = PointLog(user=user, points=mform.points.data, reason=mform.reason.data, date=current_time())
            log.save()
            points = get_points(user)
            flash(f"{user.fname} now has {points} points")
            url = url_for("admin.points", uid=user.uid)
            return redirect(url)
        else: print("USER NOT FOUND!")

    if vform.validate_on_submit():
        user = User.objects(uid=vform.uid.data).first()
        if user:
            logs = PointLog.objects(user=user).order_by('-date')
            points = get_points(user)
            return render_template("points.html", mform=mform, vform=vform, user=user, logs=logs, points=points)
        else: print("USER NOT FOUND!")
    
    # allow for dropdown pre-select through GET
    if(sel_uid):
        mform.uid.data = sel_uid
        vform.uid.data = sel_uid

    # for user in users:
    #     user.img = get_b64_img(user.uid)
    return render_template("points.html", mform=mform, vform=vform)

@admin.route("/pointsRemove", methods=["GET"])
def pointsRemove():
    uuid = request.args.get('id')
    if uuid:
        log = PointLog.objects(uuid=uuid).first()
        if log:
            log.delete()
            flash(f"Successfully deleted log from {log.date}")
            return redirect(url_for("admin.points", uid=log.user.uid))
    flash("Invalid Log ID")
    return redirect(url_for("admin.points"))

@admin.route("/pointsLog", methods=["GET"])
def pointsLog():
    uid = request.args.get('uid')
    if uid:
        user = User.objects(uid=uid).first()
        if user:
            logs = PointLog.objects(user=user).order_by('-date')
            points = get_points(user)
            return jsonify({"name":f"{user.fname} {user.lname}", "points":points, "logs":logs})
        else: return "USER NOT FOUND!"
    flash("Invalid User ID")
    return redirect(url_for("admin.points"))

# ***** FORM CREATION ROUTES *****
@admin.route("/formCreate", methods=["GET", "POST"])
def formCreate():
    # get existing forms for table
    all_forms = FormObject.objects().order_by('+due_by')

    # need to do some voodoo magic to create a custom form for creating a custom form....
    # check if GET params are passed, otherwise give the starter form (None)
    form = None
    if request.args.get('num_fields'): # number of fields
        num = int(request.args.get('num_fields'))
        form = createCustomCreationForm(num)

        if form.validate_on_submit():
            name = form.name.data
            due = form.due_date.data
            # loop thru custom fields; exclude name/date/submit/csrf
            # alternate between types and labels; true=type, false=label
            is_type = True
            types = []
            labels = []
            for field in list(form)[2:-2]:
                # separate into lists; ensure Enum value
                if is_type: types.append(FormField(int(field.data)))
                else: labels.append(field.data)
                is_type = not is_type
            form_obj = FormObject(name=name, fields=types, labels=labels, due_by=due)
            form_obj.save()
            flash("Form Successfully Created!")
            return redirect(url_for("admin.formCreate"))
        else: print(form.errors)
            
    return render_template("form_creation.html", form=form, all_forms=all_forms)

@admin.route("/formRemove", methods=["GET"])
def formRemove():
    uuid = request.args.get('id')
    if uuid:
        form = FormObject.objects(uuid=uuid).first()
        if form:
            form.delete()
            flash(f"Successfully deleted form named '{form.name}'")
            return redirect(url_for("admin.formCreate"))
    flash("Invalid Form ID")
    return redirect(url_for("admin.formCreate"))

@admin.route("/viewSubmissions", methods=["GET"])
def viewSubmissions():
    uuid = request.args.get('id')
    if uuid:
        form_obj = FormObject.objects(uuid=uuid).first()
        form_subs = FormSubmission.objects(form=form_obj).order_by('+completed')
        for sub in form_subs:
            sub.is_late = (sub.completed_dt > form_obj.due_by)
            sub.completed_dt = date_str(sub.completed_dt)
        return render_template("form_submissions.html", form_obj=form_obj, form_subs=form_subs)
    flash("Invalid Form ID")
    return redirect(url_for("admin.formCreate"))

# ***** EVENT CREATION ROUTE *****
@admin.route("/eventCreate", methods=["GET", "POST"])
def eventCreate():
    form = EventCreationForm()

    if form.validate_on_submit():
        id = createEvent(form.name.data, form.description.data, form.start.data, form.end.data)
        if id:
            if form.create_form.data:
                # create and register an attendance form
                name = f"Attendance for event: {form.name.data}"
                due = form.start.data
                types = [FormField.STRING_FIELD, FormField.EMAIL_FIELD, FormField.STRING_FIELD]
                labels = ['Name:', 'Email:', 'Event Passphrase:']
                form_obj = FormObject(name=name, fields=types, labels=labels, due_by=due, event_id=id)
                form_obj.save()
            flash("Event successfully created!")
        else:
            flash("Error occurred during event creation")
        return redirect(url_for('admin.eventCreate'))
    
    return render_template("event_creation.html", form=form)
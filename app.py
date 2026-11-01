"""
Hospital Management System
Main Flask Application
Author: College Mini Project
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

# ── Load environment variables from .env ───────────────────────────────────
load_dotenv()

# ── Flask App Setup ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-secret-key')

# ── MongoDB Atlas Connection ───────────────────────────────────────────────
MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME   = os.environ.get('DB_NAME', 'hospital_db')

if not MONGO_URI:
    raise ValueError("ERROR: MONGO_URI not set. Please create a .env file (see .env.example).")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')   # Test connection
    print("✅  Connected to MongoDB Atlas successfully!")
except ConnectionFailure as e:
    print(f"❌  MongoDB connection failed: {e}")
    raise

db           = client[DB_NAME]
patients_col = db['patients']
appts_col    = db['appointments']
bills_col    = db['bills']

# ══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════

def get_patient_or_404(patient_id):
    """Fetch a patient by id string; return None if invalid or not found."""
    try:
        return patients_col.find_one({'_id': ObjectId(patient_id)})
    except (InvalidId, Exception):
        return None


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════

@app.route('/')
def dashboard():
    # ── Aggregate stats ──
    total_patients      = patients_col.count_documents({})
    total_appointments  = appts_col.count_documents({})
    today_str           = datetime.now().strftime('%Y-%m-%d')
    today_appointments  = appts_col.count_documents({'date': today_str})

    paid_bills = list(bills_col.find({'payment_status': 'Paid'}))
    total_revenue = sum(b.get('amount', 0) for b in paid_bills)

    pending_bills = bills_col.count_documents({'payment_status': 'Pending'})

    # ── Recent records ──
    recent_patients = list(
        patients_col.find().sort('registered_on', -1).limit(5)
    )
    upcoming_appointments = list(
        appts_col.find({'status': 'Scheduled', 'date': {'$gte': today_str}})
        .sort('date', 1).limit(5)
    )

    # ── Monthly revenue for chart (last 6 months) ──
    from collections import defaultdict
    monthly_data = defaultdict(float)
    for bill in bills_col.find({'payment_status': 'Paid'}):
        created = bill.get('created_on')
        if isinstance(created, datetime):
            key = created.strftime('%b %Y')
            monthly_data[key] += bill.get('amount', 0)

    # Build ordered list for the last 6 months
    import calendar
    chart_labels = []
    chart_values = []
    now = datetime.now()
    for i in range(5, -1, -1):
        m = (now.month - i - 1) % 12 + 1
        y = now.year if now.month - i > 0 else now.year - 1
        label = f"{calendar.month_abbr[m]} {y}"
        chart_labels.append(label)
        chart_values.append(round(monthly_data.get(label, 0), 2))

    return render_template(
        'dashboard.html',
        total_patients=total_patients,
        total_appointments=total_appointments,
        today_appointments=today_appointments,
        total_revenue=total_revenue,
        pending_bills=pending_bills,
        recent_patients=recent_patients,
        upcoming_appointments=upcoming_appointments,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


# ══════════════════════════════════════════════════════════════════════════
#  PATIENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════

@app.route('/patients')
def patients_list():
    search = request.args.get('search', '').strip()
    if search:
        query = {
            '$or': [
                {'name':  {'$regex': search, '$options': 'i'}},
                {'phone': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
            ]
        }
        patient_list = list(patients_col.find(query))
    else:
        patient_list = list(patients_col.find().sort('registered_on', -1))

    return render_template('patients/list.html',
                           patients=patient_list, search=search)


@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name         = request.form.get('name', '').strip()
        age          = request.form.get('age', '').strip()
        gender       = request.form.get('gender', '').strip()
        blood_group  = request.form.get('blood_group', '').strip()
        phone        = request.form.get('phone', '').strip()
        email        = request.form.get('email', '').strip()
        address      = request.form.get('address', '').strip()
        med_history  = request.form.get('medical_history', '').strip()

        # ── Server-side validation ──
        errors = []
        if not name:
            errors.append('Patient name is required.')
        if not age or not age.isdigit() or int(age) <= 0 or int(age) > 150:
            errors.append('Valid age (1–150) is required.')
        if not gender:
            errors.append('Gender is required.')
        if not phone or len(phone) < 10:
            errors.append('Valid phone number (min 10 digits) is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('patients/add.html',
                                   form_data=request.form)

        patient = {
            'name':            name,
            'age':             int(age),
            'gender':          gender,
            'blood_group':     blood_group,
            'phone':           phone,
            'email':           email,
            'address':         address,
            'medical_history': med_history,
            'registered_on':   datetime.now(),
        }
        patients_col.insert_one(patient)
        flash(f'Patient "{name}" registered successfully!', 'success')
        return redirect(url_for('patients_list'))

    return render_template('patients/add.html', form_data={})


@app.route('/patients/<patient_id>')
def patient_detail(patient_id):
    patient = get_patient_or_404(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients_list'))

    # Fetch linked appointments and bills
    patient_appts = list(appts_col.find({'patient_id': str(patient_id)}).sort('date', -1))
    patient_bills = list(bills_col.find({'patient_id': str(patient_id)}).sort('created_on', -1))
    total_billed  = sum(b.get('amount', 0) for b in patient_bills)

    return render_template('patients/detail.html',
                           patient=patient,
                           appointments=patient_appts,
                           bills=patient_bills,
                           total_billed=total_billed)


@app.route('/patients/edit/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = get_patient_or_404(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients_list'))

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        age         = request.form.get('age', '').strip()
        gender      = request.form.get('gender', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        phone       = request.form.get('phone', '').strip()
        email       = request.form.get('email', '').strip()
        address     = request.form.get('address', '').strip()
        med_history = request.form.get('medical_history', '').strip()

        errors = []
        if not name:
            errors.append('Patient name is required.')
        if not age or not age.isdigit() or int(age) <= 0:
            errors.append('Valid age is required.')
        if not phone or len(phone) < 10:
            errors.append('Valid phone number is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('patients/edit.html', patient=patient)

        patients_col.update_one(
            {'_id': ObjectId(patient_id)},
            {'$set': {
                'name':            name,
                'age':             int(age),
                'gender':          gender,
                'blood_group':     blood_group,
                'phone':           phone,
                'email':           email,
                'address':         address,
                'medical_history': med_history,
            }}
        )
        flash(f'Patient "{name}" updated successfully!', 'success')
        return redirect(url_for('patient_detail', patient_id=patient_id))

    return render_template('patients/edit.html', patient=patient)


@app.route('/patients/delete/<patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = get_patient_or_404(patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients_list'))

    patients_col.delete_one({'_id': ObjectId(patient_id)})
    flash(f'Patient "{patient["name"]}" deleted successfully.', 'warning')
    return redirect(url_for('patients_list'))


# ══════════════════════════════════════════════════════════════════════════
#  APPOINTMENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════

@app.route('/appointments')
def appointments_list():
    status_filter = request.args.get('status', '')
    date_filter   = request.args.get('date', '')

    query = {}
    if status_filter:
        query['status'] = status_filter
    if date_filter:
        query['date'] = date_filter

    appt_list = list(appts_col.find(query).sort('date', -1))
    return render_template('appointments/list.html',
                           appointments=appt_list,
                           status_filter=status_filter,
                           date_filter=date_filter)


@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    all_patients = list(patients_col.find().sort('name', 1))

    if request.method == 'POST':
        patient_id   = request.form.get('patient_id', '').strip()
        doctor       = request.form.get('doctor', '').strip()
        department   = request.form.get('department', '').strip()
        date_str     = request.form.get('date', '').strip()
        time_str     = request.form.get('time', '').strip()
        notes        = request.form.get('notes', '').strip()

        errors = []
        patient = get_patient_or_404(patient_id)
        if not patient:
            errors.append('Please select a valid patient.')
        if not doctor:
            errors.append('Doctor name is required.')
        if not department:
            errors.append('Department is required.')
        if not date_str:
            errors.append('Appointment date is required.')
        if not time_str:
            errors.append('Appointment time is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('appointments/add.html',
                                   patients=all_patients,
                                   form_data=request.form)

        appt = {
            'patient_id':   str(patient_id),
            'patient_name': patient['name'],
            'doctor':       doctor,
            'department':   department,
            'date':         date_str,
            'time':         time_str,
            'status':       'Scheduled',
            'notes':        notes,
            'created_on':   datetime.now(),
        }
        appts_col.insert_one(appt)
        flash(f'Appointment booked for {patient["name"]} on {date_str}!', 'success')
        return redirect(url_for('appointments_list'))

    return render_template('appointments/add.html',
                           patients=all_patients, form_data={})


@app.route('/appointments/edit/<appt_id>', methods=['GET', 'POST'])
def edit_appointment(appt_id):
    try:
        appt = appts_col.find_one({'_id': ObjectId(appt_id)})
    except Exception:
        appt = None

    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments_list'))

    all_patients = list(patients_col.find().sort('name', 1))

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        doctor     = request.form.get('doctor', '').strip()
        department = request.form.get('department', '').strip()
        date_str   = request.form.get('date', '').strip()
        time_str   = request.form.get('time', '').strip()
        status     = request.form.get('status', '').strip()
        notes      = request.form.get('notes', '').strip()

        patient = get_patient_or_404(patient_id)
        if not patient:
            flash('Invalid patient selected.', 'danger')
            return render_template('appointments/edit.html',
                                   appt=appt, patients=all_patients)

        appts_col.update_one(
            {'_id': ObjectId(appt_id)},
            {'$set': {
                'patient_id':   str(patient_id),
                'patient_name': patient['name'],
                'doctor':       doctor,
                'department':   department,
                'date':         date_str,
                'time':         time_str,
                'status':       status,
                'notes':        notes,
            }}
        )
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments_list'))

    return render_template('appointments/edit.html',
                           appt=appt, patients=all_patients)


@app.route('/appointments/delete/<appt_id>', methods=['POST'])
def delete_appointment(appt_id):
    try:
        result = appts_col.delete_one({'_id': ObjectId(appt_id)})
        if result.deleted_count:
            flash('Appointment cancelled successfully.', 'warning')
        else:
            flash('Appointment not found.', 'danger')
    except Exception:
        flash('Invalid appointment ID.', 'danger')
    return redirect(url_for('appointments_list'))


# ══════════════════════════════════════════════════════════════════════════
#  BILLING MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════

SERVICES_LIST = [
    'Consultation', 'Lab Test', 'X-Ray', 'MRI Scan', 'CT Scan',
    'Blood Test', 'Urine Test', 'ECG', 'Ultrasound', 'Physiotherapy',
    'Surgery', 'ICU Charges', 'Room Charges', 'Medication', 'Nursing',
]


@app.route('/billing')
def billing_list():
    status_filter = request.args.get('status', '')
    if status_filter:
        bill_list = list(bills_col.find({'payment_status': status_filter}).sort('created_on', -1))
    else:
        bill_list = list(bills_col.find().sort('created_on', -1))

    return render_template('billing/list.html',
                           bills=bill_list,
                           status_filter=status_filter)


@app.route('/billing/add', methods=['GET', 'POST'])
def add_bill():
    all_patients = list(patients_col.find().sort('name', 1))

    if request.method == 'POST':
        patient_id     = request.form.get('patient_id', '').strip()
        services       = request.form.getlist('services')
        amount         = request.form.get('amount', '0').strip()
        payment_status = request.form.get('payment_status', 'Pending').strip()
        date_str       = request.form.get('date', '').strip()
        notes          = request.form.get('notes', '').strip()

        errors = []
        patient = get_patient_or_404(patient_id)
        if not patient:
            errors.append('Please select a valid patient.')
        if not services:
            errors.append('Select at least one service.')
        if safe_float(amount) <= 0:
            errors.append('Amount must be greater than 0.')
        if not date_str:
            errors.append('Billing date is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('billing/add.html',
                                   patients=all_patients,
                                   services_list=SERVICES_LIST,
                                   form_data=request.form)

        bill = {
            'patient_id':     str(patient_id),
            'patient_name':   patient['name'],
            'services':       services,
            'amount':         safe_float(amount),
            'date':           date_str,
            'payment_status': payment_status,
            'notes':          notes,
            'created_on':     datetime.now(),
        }
        bills_col.insert_one(bill)
        flash(f'Bill created for {patient["name"]} — ₹{amount}!', 'success')
        return redirect(url_for('billing_list'))

    return render_template('billing/add.html',
                           patients=all_patients,
                           services_list=SERVICES_LIST,
                           form_data={})


@app.route('/billing/<bill_id>')
def bill_detail(bill_id):
    try:
        bill = bills_col.find_one({'_id': ObjectId(bill_id)})
    except Exception:
        bill = None

    if not bill:
        flash('Bill not found.', 'danger')
        return redirect(url_for('billing_list'))

    patient = get_patient_or_404(bill.get('patient_id', ''))
    return render_template('billing/detail.html', bill=bill, patient=patient)


@app.route('/billing/update_status/<bill_id>', methods=['POST'])
def update_bill_status(bill_id):
    new_status = request.form.get('payment_status', 'Paid')
    try:
        bills_col.update_one(
            {'_id': ObjectId(bill_id)},
            {'$set': {'payment_status': new_status}}
        )
        flash(f'Payment status updated to "{new_status}".', 'success')
    except Exception:
        flash('Failed to update payment status.', 'danger')
    return redirect(url_for('bill_detail', bill_id=bill_id))


@app.route('/billing/delete/<bill_id>', methods=['POST'])
def delete_bill(bill_id):
    try:
        bills_col.delete_one({'_id': ObjectId(bill_id)})
        flash('Bill deleted successfully.', 'warning')
    except Exception:
        flash('Failed to delete bill.', 'danger')
    return redirect(url_for('billing_list'))


# ══════════════════════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


# ══════════════════════════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True)

"""
seed_data.py — Load sample data into MongoDB Atlas for demonstration.
Run once: python seed_data.py
"""

import os
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME   = os.environ.get('DB_NAME', 'hospital_db')

if not MONGO_URI:
    raise ValueError("MONGO_URI not set! Please create a .env file.")

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# ── Clear existing data ──────────────────────────────────────────────────
db.patients.drop()
db.appointments.drop()
db.bills.drop()
print("🗑️  Cleared existing collections.")

# ── Sample Patients ──────────────────────────────────────────────────────
patients_data = [
    {
        'name': 'Arjun Sharma',       'age': 34, 'gender': 'Male',
        'blood_group': 'B+',          'phone': '9876543210',
        'email': 'arjun.sharma@email.com',
        'address': '12, MG Road, Bengaluru, Karnataka',
        'medical_history': 'Hypertension, Type 2 Diabetes',
        'registered_on': datetime.now() - timedelta(days=30),
    },
    {
        'name': 'Priya Nair',         'age': 28, 'gender': 'Female',
        'blood_group': 'O+',          'phone': '9812345678',
        'email': 'priya.nair@email.com',
        'address': '45, Jubilee Hills, Hyderabad, Telangana',
        'medical_history': 'Asthma',
        'registered_on': datetime.now() - timedelta(days=25),
    },
    {
        'name': 'Vikram Patel',       'age': 52, 'gender': 'Male',
        'blood_group': 'A+',          'phone': '9845678901',
        'email': 'vikram.patel@email.com',
        'address': '7, Satellite Road, Ahmedabad, Gujarat',
        'medical_history': 'Arthritis, High Cholesterol',
        'registered_on': datetime.now() - timedelta(days=22),
    },
    {
        'name': 'Sunita Devi',        'age': 45, 'gender': 'Female',
        'blood_group': 'AB+',         'phone': '9765432109',
        'email': 'sunita.devi@email.com',
        'address': '22, Civil Lines, Lucknow, UP',
        'medical_history': 'Migraine, Thyroid disorder',
        'registered_on': datetime.now() - timedelta(days=20),
    },
    {
        'name': 'Rahul Mehta',        'age': 19, 'gender': 'Male',
        'blood_group': 'O-',          'phone': '9654321098',
        'email': 'rahul.mehta@email.com',
        'address': '88, Bandra West, Mumbai, Maharashtra',
        'medical_history': 'None',
        'registered_on': datetime.now() - timedelta(days=18),
    },
    {
        'name': 'Ananya Krishnan',    'age': 31, 'gender': 'Female',
        'blood_group': 'B-',          'phone': '9543210987',
        'email': 'ananya.k@email.com',
        'address': '5, T Nagar, Chennai, Tamil Nadu',
        'medical_history': 'PCOD, Anaemia',
        'registered_on': datetime.now() - timedelta(days=15),
    },
    {
        'name': 'Deepak Rajput',      'age': 60, 'gender': 'Male',
        'blood_group': 'A-',          'phone': '9432109876',
        'email': 'deepak.r@email.com',
        'address': '34, Model Town, Delhi',
        'medical_history': 'Coronary artery disease, Diabetes',
        'registered_on': datetime.now() - timedelta(days=12),
    },
    {
        'name': 'Kavya Reddy',        'age': 24, 'gender': 'Female',
        'blood_group': 'O+',          'phone': '9321098765',
        'email': 'kavya.reddy@email.com',
        'address': '11, Hitech City, Hyderabad, Telangana',
        'medical_history': 'None',
        'registered_on': datetime.now() - timedelta(days=9),
    },
    {
        'name': 'Manoj Tiwari',       'age': 41, 'gender': 'Male',
        'blood_group': 'AB-',         'phone': '9210987654',
        'email': 'manoj.t@email.com',
        'address': '67, Arera Colony, Bhopal, MP',
        'medical_history': 'Kidney Stone',
        'registered_on': datetime.now() - timedelta(days=5),
    },
    {
        'name': 'Lakshmi Iyer',       'age': 55, 'gender': 'Female',
        'blood_group': 'B+',          'phone': '9109876543',
        'email': 'lakshmi.iyer@email.com',
        'address': '2, Indiranagar, Bengaluru, Karnataka',
        'medical_history': 'Osteoporosis, Hypertension',
        'registered_on': datetime.now() - timedelta(days=2),
    },
]

inserted_patients = db.patients.insert_many(patients_data)
patient_ids = [str(pid) for pid in inserted_patients.inserted_ids]
patient_names = [p['name'] for p in patients_data]
print(f"✅  Inserted {len(patient_ids)} patients.")

# ── Sample Appointments ──────────────────────────────────────────────────
doctors = [
    ('Dr. Anil Kumar',    'Cardiology'),
    ('Dr. Preethi Sinha', 'Neurology'),
    ('Dr. Ramesh Gupta',  'Orthopaedics'),
    ('Dr. Meena Joshi',   'Gynaecology'),
    ('Dr. Suresh Pillai', 'General Medicine'),
    ('Dr. Nisha Thomas',  'Dermatology'),
]
statuses = ['Scheduled', 'Scheduled', 'Completed', 'Completed', 'Cancelled']
times    = ['09:00', '10:00', '10:30', '11:00', '12:00',
            '14:00', '15:00', '15:30', '16:00', '17:00']

appointments_data = []
for i in range(15):
    pid_index = i % len(patient_ids)
    doc, dept = random.choice(doctors)
    appt_date = datetime.now() + timedelta(days=random.randint(-10, 15))
    status    = random.choice(statuses)
    appointments_data.append({
        'patient_id':   patient_ids[pid_index],
        'patient_name': patient_names[pid_index],
        'doctor':       doc,
        'department':   dept,
        'date':         appt_date.strftime('%Y-%m-%d'),
        'time':         random.choice(times),
        'status':       status,
        'notes':        'Routine check-up' if i % 3 == 0 else 'Follow-up visit',
        'created_on':   datetime.now() - timedelta(days=random.randint(0, 20)),
    })

db.appointments.insert_many(appointments_data)
print(f"✅  Inserted {len(appointments_data)} appointments.")

# ── Sample Bills ─────────────────────────────────────────────────────────
services_pool = [
    'Consultation', 'Lab Test', 'X-Ray', 'Blood Test',
    'ECG', 'Ultrasound', 'Medication', 'Room Charges', 'Nursing',
]

bills_data = []
for i in range(10):
    pid_index   = i % len(patient_ids)
    services    = random.sample(services_pool, random.randint(1, 4))
    amount      = round(random.uniform(500, 15000), 2)
    pay_status  = 'Paid' if i % 3 != 0 else 'Pending'
    bill_date   = datetime.now() - timedelta(days=random.randint(0, 30))
    bills_data.append({
        'patient_id':     patient_ids[pid_index],
        'patient_name':   patient_names[pid_index],
        'services':       services,
        'amount':         amount,
        'date':           bill_date.strftime('%Y-%m-%d'),
        'payment_status': pay_status,
        'notes':          '',
        'created_on':     bill_date,
    })

db.bills.insert_many(bills_data)
print(f"✅  Inserted {len(bills_data)} bills.")

print("\n🎉  Sample data loaded successfully!")
print(f"    Database : {DB_NAME}")
print(f"    Patients : {len(patient_ids)}")
print(f"    Appts    : {len(appointments_data)}")
print(f"    Bills    : {len(bills_data)}")
print("\n▶  Run the app now:  python app.py")

# 🏥 Hospital Management System

A full-stack web application for managing hospital operations — built with **Python Flask**, **MongoDB Atlas**, **Bootstrap 5**, and custom CSS.

---

## 📋 Features

| Feature | Description |
|---------|-------------|
| 🏠 Dashboard | Live stats: patients, appointments, revenue + chart |
| 👤 Patients | Register, view, edit, delete patient records |
| 📅 Appointments | Book, manage, and track appointments |
| 💰 Billing | Create bills, track payment status, view invoices |
| 🔍 Search | Search patients by name or phone number |

---

## ⚙️ Setup Instructions

### Step 1 — Clone / Download the Project
```
cd "HOSPITAL MANAGEMENT SYSTEM"
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure MongoDB Atlas
1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and sign up for free.
2. Create a **free M0 cluster**.
3. Under **Database Access**, create a user with read/write privileges.
4. Under **Network Access**, add `0.0.0.0/0` to allow all IPs.
5. Click **Connect → Drivers** and copy your connection string.

### Step 5 — Create Your `.env` File
```bash
copy .env.example .env
```
Open `.env` and paste your MongoDB Atlas connection string:
```
MONGO_URI=mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=hospital_db
SECRET_KEY=any-random-long-string
```

### Step 6 — Load Sample Data
```bash
python seed_data.py
```
This adds 10 patients, 15 appointments, and 10 bills for demonstration.

### Step 7 — Run the Application
```bash
python app.py
```
Open your browser at: **http://127.0.0.1:5000**

---

## 📁 Project Structure
```
HOSPITAL MANAGEMENT SYSTEM/
├── app.py                  # Flask app & routes
├── seed_data.py            # Demo data loader
├── requirements.txt
├── .env.example            # Environment variable template
├── .env                    # Your actual credentials (not in git)
├── README.md
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/logo.png
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── patients/
    ├── appointments/
    └── billing/
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.x + Flask 2.3
- **Database**: MongoDB Atlas (PyMongo)
- **Frontend**: HTML5 + Bootstrap 5 + Custom CSS
- **Icons**: Font Awesome 6
- **Charts**: Chart.js

---

## 👨‍💻 Built for College Mini Project

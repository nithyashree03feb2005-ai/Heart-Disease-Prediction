import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    
    # Users table for both patients and doctors
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patient predictions history
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            age REAL,
            sex INTEGER,
            cp REAL,
            trestbps REAL,
            chol REAL,
            fbs INTEGER,
            restecg REAL,
            thalach REAL,
            exang REAL,
            oldpeak REAL,
            slope REAL,
            ca REAL,
            thal REAL,
            chol_bp_ratio REAL,
            age_group INTEGER,
            risk_score REAL,
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Add fbs column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE predictions ADD COLUMN fbs INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Doctor's patient management
    c.execute('''
        CREATE TABLE IF NOT EXISTS doctor_patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            patient_id INTEGER,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (doctor_id) REFERENCES users(id),
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, password, user_type, full_name='', email='', phone=''):
    """Register a new user (patient or doctor)"""
    try:
        conn = sqlite3.connect('database/patients.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (username, password, user_type, full_name, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password, user_type, full_name, email, phone))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username, password):
    """Authenticate user and return user info"""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    c.execute("SELECT id, username, user_type, full_name, email FROM users WHERE username=? AND password=?", 
              (username, password))
    user = c.fetchone()
    conn.close()
    return user

def insert_prediction(user_id, data):
    """Insert prediction data for a patient"""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO predictions (user_id, age, sex, cp, trestbps, chol, fbs, restecg, 
        thalach, exang, oldpeak, slope, ca, thal, chol_bp_ratio, age_group, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, data['age'], data['sex'], data['cp'], data['trestbps'], 
          data['chol'], data['fbs'], data['restecg'], data['thalach'], data['exang'], 
          data['oldpeak'], data['slope'], data['ca'], data['thal'], 
          data['chol_bp_ratio'], data['age_group'], data['risk_score']))
    conn.commit()
    conn.close()

def get_user_predictions(user_id):
    """Get all predictions for a specific user"""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    c.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY prediction_date DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_all_predictions():
    """Fetch all predictions (for doctor dashboard)"""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    c.execute("""
        SELECT p.*, u.full_name, u.username 
        FROM predictions p 
        LEFT JOIN users u ON p.user_id = u.id 
        ORDER BY p.prediction_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_users_by_type(user_type):
    """Get all users of a specific type"""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    c.execute("SELECT id, username, full_name, email, created_at FROM users WHERE user_type=?", (user_type,))
    rows = c.fetchall()
    conn.close()
    return rows

def assign_patient_to_doctor(doctor_id, patient_id, notes=''):
    """Assign a patient to a doctor"""
    try:
        conn = sqlite3.connect('database/patients.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO doctor_patients (doctor_id, patient_id, notes)
            VALUES (?, ?, ?)
        """, (doctor_id, patient_id, notes))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_doctor_patients(doctor_id):
    """Get all patients assigned to a doctor"""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.username, u.full_name, u.email, dp.notes, dp.assigned_date
        FROM users u
        INNER JOIN doctor_patients dp ON u.id = dp.patient_id
        WHERE dp.doctor_id = ? AND u.user_type = 'patient'
    """, (doctor_id,))
    rows = c.fetchall()
    conn.close()
    return rows
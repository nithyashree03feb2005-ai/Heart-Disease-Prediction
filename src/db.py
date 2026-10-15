import sqlite3
import os
from datetime import datetime

def init_db():
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
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

    user_columns = {row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()}
    for column in ('normalized_username', 'normalized_email', 'normalized_phone'):
        if column not in user_columns:
            c.execute(f'ALTER TABLE users ADD COLUMN {column} TEXT')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS users_normalized_username_idx ON users(normalized_username) WHERE normalized_username IS NOT NULL')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS users_normalized_email_idx ON users(normalized_email) WHERE normalized_email IS NOT NULL')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS users_normalized_phone_idx ON users(normalized_phone) WHERE normalized_phone IS NOT NULL')

    c.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier_hash TEXT NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS login_attempts_identifier_time_idx ON login_attempts(identifier_hash, attempted_at)')
    
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

def register_user(username, password_hash, user_type, full_name='', email='', phone=''):
    """Create an account with final duplicate checks inside a write transaction."""
    conn = sqlite3.connect('database/patients.db', timeout=10)
    try:
        conn.execute('BEGIN IMMEDIATE')
        c = conn.cursor()

        c.execute('SELECT 1 FROM users WHERE lower(trim(username)) = ? LIMIT 1', (username.casefold(),))
        if c.fetchone():
            return False, 'username'
        c.execute('SELECT 1 FROM users WHERE lower(trim(email)) = ? LIMIT 1', (email.casefold(),))
        if c.fetchone():
            return False, 'email'

        candidate_phone = ''.join(character for character in phone if character.isdigit())
        if candidate_phone.startswith('91') and len(candidate_phone) == 12:
            candidate_phone = candidate_phone[2:]
        for (existing_phone,) in c.execute('SELECT phone FROM users WHERE phone IS NOT NULL AND trim(phone) != ""').fetchall():
            existing_digits = ''.join(character for character in existing_phone if character.isdigit())
            if existing_digits.startswith('91') and len(existing_digits) == 12:
                existing_digits = existing_digits[2:]
            if existing_digits == candidate_phone:
                return False, 'phone'

        c.execute("""
            INSERT INTO users (
                username, password, user_type, full_name, email, phone,
                normalized_username, normalized_email, normalized_phone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, password_hash, user_type, full_name, email, phone,
            username.casefold(), email.casefold(), candidate_phone
        ))
        conn.commit()
        return True, ''
    except sqlite3.IntegrityError:
        conn.rollback()
        for field, value in (
            ('username', username.casefold()),
            ('email', email.casefold()),
        ):
            column = f'normalized_{field}'
            if conn.execute(f'SELECT 1 FROM users WHERE {column} = ?', (value,)).fetchone():
                return False, field
        return False, 'phone'
    finally:
        conn.close()

def get_user_for_auth(identifier):
    """Fetch the credential record for a username or email identifier."""
    conn = sqlite3.connect('database/patients.db')
    c = conn.cursor()
    normalized_identifier = identifier.strip().casefold()
    c.execute("""
        SELECT id, username, user_type, full_name, email, password
        FROM users
        WHERE lower(username) = ? OR lower(trim(email)) = ?
        LIMIT 1
    """, (normalized_identifier, normalized_identifier))
    user = c.fetchone()
    conn.close()
    return user

def update_user_password(user_id, password_hash):
    conn = sqlite3.connect('database/patients.db')
    try:
        conn.execute('UPDATE users SET password = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()
    finally:
        conn.close()

def get_legacy_password_users():
    conn = sqlite3.connect('database/patients.db')
    try:
        return conn.execute(
            "SELECT id, password FROM users WHERE substr(password, 1, 14) != 'pbkdf2_sha256$'"
        ).fetchall()
    finally:
        conn.close()

def registration_field_available(field, value):
    """Check availability for UI feedback; register_user repeats this atomically."""
    conn = sqlite3.connect('database/patients.db')
    try:
        c = conn.cursor()
        normalized_value = value.casefold()
        if field in ('username', 'email'):
            c.execute(
                f'SELECT 1 FROM users WHERE lower(trim({field})) = ? LIMIT 1',
                (normalized_value,),
            )
            return c.fetchone() is None
        if field == 'phone':
            digits = ''.join(character for character in value if character.isdigit())
            if digits.startswith('91') and len(digits) == 12:
                digits = digits[2:]
            rows = c.execute('SELECT phone FROM users WHERE phone IS NOT NULL').fetchall()
            for (existing_phone,) in rows:
                existing_digits = ''.join(character for character in existing_phone if character.isdigit())
                if existing_digits.startswith('91') and len(existing_digits) == 12:
                    existing_digits = existing_digits[2:]
                if existing_digits == digits:
                    return False
            return True
        raise ValueError('Unsupported registration field')
    finally:
        conn.close()

def count_recent_login_failures(identifier_hash):
    conn = sqlite3.connect('database/patients.db')
    try:
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) FROM login_attempts
            WHERE identifier_hash = ? AND attempted_at >= datetime('now', '-15 minutes')
        """, (identifier_hash,))
        return c.fetchone()[0]
    finally:
        conn.close()

def record_login_failure(identifier_hash):
    conn = sqlite3.connect('database/patients.db')
    try:
        conn.execute(
            "INSERT INTO login_attempts (identifier_hash) VALUES (?)",
            (identifier_hash,),
        )
        conn.execute("DELETE FROM login_attempts WHERE attempted_at < datetime('now', '-1 day')")
        conn.commit()
    finally:
        conn.close()

def clear_login_failures(identifier_hash):
    conn = sqlite3.connect('database/patients.db')
    try:
        conn.execute('DELETE FROM login_attempts WHERE identifier_hash = ?', (identifier_hash,))
        conn.commit()
    finally:
        conn.close()

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
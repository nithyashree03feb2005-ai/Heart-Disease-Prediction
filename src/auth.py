import hashlib
import hmac
import re
import secrets

from db import (
    clear_login_failures,
    count_recent_login_failures,
    get_user_for_auth,
    get_legacy_password_users,
    record_login_failure,
    register_user,
    registration_field_available,
    update_user_password,
)

PASSWORD_ITERATIONS = 600_000
MAX_LOGIN_FAILURES = 5
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.]{3,20}$")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$")
PHONE_PATTERN = re.compile(r"^(?:\+91)?[6-9][0-9]{9}$")


def normalize_phone(phone):
    """Normalize accepted Indian mobile formats to +91 followed by ten digits."""
    stripped = phone.strip()
    if not re.fullmatch(r"[0-9+\-\s]+", stripped):
        return None
    compact = re.sub(r"[\s-]", "", stripped)
    if not PHONE_PATTERN.fullmatch(compact):
        return None
    digits = compact[3:] if compact.startswith('+91') else compact
    return f'+91{digits}'


def validate_username(username):
    username = username.strip()
    if not username:
        return 'Username is required.'
    if not USERNAME_PATTERN.fullmatch(username):
        return 'Use 3-20 characters: letters, numbers, underscores, or periods only.'
    return None


def validate_email(email):
    email = email.strip()
    if not email:
        return 'Email address is required.'
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        return 'Enter a valid email address, such as name@example.com.'
    local_part, domain = email.rsplit('@', 1)
    if local_part.startswith('.') or local_part.endswith('.') or '..' in local_part or '..' in domain:
        return 'Enter a valid email address, such as name@example.com.'
    return None


def validate_phone(phone):
    if not phone.strip():
        return 'Phone number is required.'
    if normalize_phone(phone) is None:
        return 'Enter a valid 10-digit Indian mobile number, optionally prefixed with +91.'
    return None


def password_strength(password):
    has_required_characters = all((
        re.search(r'[A-Z]', password),
        re.search(r'[a-z]', password),
        re.search(r'[0-9]', password),
        re.search(r'[^A-Za-z0-9\s]', password),
    ))
    if len(password) < 8 or not password.strip() or not has_required_characters:
        return 'Weak'
    if len(password) >= 12:
        return 'Strong'
    return 'Medium'


def validate_password(password):
    if not password or not password.strip():
        return 'Password is required and cannot contain only spaces.'
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    if len(password) > 128:
        return 'Password must be 128 characters or fewer.'
    missing = []
    if not re.search(r'[A-Z]', password):
        missing.append('an uppercase letter')
    if not re.search(r'[a-z]', password):
        missing.append('a lowercase letter')
    if not re.search(r'[0-9]', password):
        missing.append('a number')
    if not re.search(r'[^A-Za-z0-9\s]', password):
        missing.append('a special character')
    if missing:
        return 'Password must include ' + ', '.join(missing) + '.'
    return None


def validate_registration(username, password, user_type, full_name='', email='', phone=''):
    normalized = {
        'username': username.strip(),
        'password': password,
        'user_type': user_type,
        'full_name': full_name.strip(),
        'email': email.strip().casefold(),
        'phone': normalize_phone(phone) or phone.strip(),
    }
    errors = {
        'username': validate_username(username),
        'email': validate_email(email),
        'phone': validate_phone(phone),
        'password': validate_password(password),
    }
    if user_type not in ('patient', 'doctor'):
        errors['user_type'] = 'Choose a valid account type.'
    if user_type == 'doctor' and not normalized['full_name']:
        errors['full_name'] = 'Full name is required for doctor accounts.'
    return normalized, {field: message for field, message in errors.items() if message}


def validate_user_data(user_type, **kwargs):
    """Compatibility wrapper for callers that need a simple validity result."""
    _, errors = validate_registration(
        kwargs.get('username', ''),
        kwargs.get('password', ''),
        user_type,
        kwargs.get('full_name', ''),
        kwargs.get('email', ''),
        kwargs.get('phone', ''),
    )
    return (False, next(iter(errors.values()))) if errors else (True, 'Valid')


def _hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PASSWORD_ITERATIONS)
    return f'pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}'


def _verify_password(password, stored_password):
    if not stored_password.startswith('pbkdf2_sha256$'):
        return False
    try:
        _, iterations, salt_hex, digest_hex = stored_password.split('$', 3)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def migrate_legacy_passwords():
    """Hash passwords created by older releases before allowing login attempts."""
    for user_id, legacy_password in get_legacy_password_users():
        update_user_password(user_id, _hash_password(legacy_password))


def _login_identifier_hash(identifier):
    return hashlib.sha256(identifier.strip().casefold().encode('utf-8')).hexdigest()


def is_login_rate_limited(identifier):
    if not identifier.strip():
        return False
    return count_recent_login_failures(_login_identifier_hash(identifier)) >= MAX_LOGIN_FAILURES


def authenticate(identifier, password):
    """Authenticate by username or email; return public user data on success."""
    identifier = identifier.strip()
    if not identifier or not password:
        return None

    identifier_hash = _login_identifier_hash(identifier)
    if count_recent_login_failures(identifier_hash) >= MAX_LOGIN_FAILURES:
        return None

    user = get_user_for_auth(identifier)
    if user is None:
        # Keep unknown-account failures close in cost to a real password verification.
        hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'heartcare-dummy-salt', PASSWORD_ITERATIONS)
        record_login_failure(identifier_hash)
        return None

    user_id, username, user_type, full_name, email, stored_password = user
    valid = _verify_password(password, stored_password)
    if not valid:
        record_login_failure(identifier_hash)
        return None

    clear_login_failures(identifier_hash)
    return user_id, username, user_type, full_name, email


def register(username, password, user_type, full_name='', email='', phone=''):
    normalized, errors = validate_registration(
        username, password, user_type, full_name, email, phone
    )
    if errors:
        return False, next(iter(errors.values()))

    for field in ('username', 'email', 'phone'):
        if not registration_field_available(field, normalized[field]):
            return False, f'That {field} is already registered. Please use a different {field}.'

    success, conflict = register_user(
        normalized['username'],
        _hash_password(normalized['password']),
        normalized['user_type'],
        normalized['full_name'],
        normalized['email'],
        normalized['phone'],
    )
    if success:
        return True, 'Registration successful'
    return False, f'That {conflict} is already registered. Please use a different {conflict}.'
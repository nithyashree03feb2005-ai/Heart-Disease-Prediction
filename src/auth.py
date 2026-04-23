from db import register_user, get_user

def authenticate(username, password):
    """Authenticate user and return user data if successful"""
    return get_user(username, password)

def register(username, password, user_type, full_name='', email='', phone=''):
    """Register a new user"""
    # Validate inputs
    if not username or not password:
        return False, "Username and password are required"
    
    if len(password) < 4:
        return False, "Password must be at least 4 characters long"
    
    if user_type not in ['patient', 'doctor']:
        return False, "Invalid user type"
    
    # Register user
    success = register_user(username, password, user_type, full_name, email, phone)
    
    if success:
        return True, "Registration successful"
    else:
        return False, "Username already exists"

def validate_user_data(user_type, **kwargs):
    """Validate user registration data"""
    if user_type == 'doctor':
        if not kwargs.get('full_name'):
            return False, "Full name is required for doctors"
        if not kwargs.get('email'):
            return False, "Email is required for doctors"
        if not kwargs.get('phone'):
            return False, "Phone number is required for doctors"
    
    return True, "Valid"
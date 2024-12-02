from functools import wraps
from flask import jsonify
from flask_login import LoginManager, UserMixin, current_user, login_required
from db import get_user_by_email, get_user_by_id, check_password

class User(UserMixin):
    def __init__(self, id, name, email, address, role, created_date, created_by):
        self.id = id
        self.name = name
        self.email = email
        self.address = address
        self.role = role
        self.created_date = created_date
        self.created_by = created_by

    @classmethod
    def get_user_by_email(cls, email):
        user_data = get_user_by_email(email)
        if user_data:
            return cls(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                address=user_data['address'],
                role=user_data['role'],
                created_date=user_data['created_date'],
                created_by=user_data['created_by']
            )
        return None

    @classmethod
    def get_user_by_id(cls, user_id):
        user_data = get_user_by_id(user_id)
        if user_data:
            return cls(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                address=user_data['address'],
                role=user_data['role'],
                created_date=user_data['created_date'],
                created_by=user_data['created_by']
            )
        return None

    def check_password(self, password):
        # Assuming password is stored in the database and passed through get_user_by_email
        user_data = get_user_by_email(self.email)
        if user_data and 'password' in user_data:
            return check_password(user_data['password'], password)
        return False


from functools import wraps
from flask import jsonify
from flask_login import current_user

# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             # Check if the user is authenticated
#             if not current_user.is_authenticated:
#                 return jsonify({'error': 'You must be logged in to access this resource'}), 401
            
#             # Check if the user has the required role
#             if current_user.role != role:
#                 return jsonify({'error': 'Unauthorized access'}), 403
            
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# def role_required(*roles):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             # Check if the user is authenticated
#             if not current_user.is_authenticated:
#                 return jsonify({'error': 'You must be logged in to access this resource'}), 401
            
#             # Check if the user's role is in the allowed roles
#             if current_user.role not in roles:
#                 return jsonify({'error': 'Unauthorized access'}), 403
            
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps

def role_required(*roles):
    def decorator(f): 
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            
            # Kiểm tra role của user
            if current_user['role'] not in roles:
                return jsonify({'error': 'Unauthorized access'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
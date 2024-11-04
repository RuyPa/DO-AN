from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db import add_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/add-user', methods=['POST'])
@login_required
def add_user_route():
    # Check if current user is an admin
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    # Get user data from request
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    address = data.get('address')
    role = data.get('role', 'user')  # Default role to 'user' if not provided
    created_by = current_user.name   # Set the admin who created the user
    password = data.get('password')

    # Validate required fields
    if not all([name, email, address, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Add the new user to the database
    try:
        add_user(name, email, address, role, created_by, password)
        return jsonify({'message': 'User added successfully!'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while adding the user'}), 500

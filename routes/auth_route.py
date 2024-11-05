from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Fetch user by email
        user = User.get_user_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({
                'message': 'Login successful!',
                'role': user.role,  # Return the user's role
                'name': user.name
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    
    # Render a login form for GET request
    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'}), 200


# Protected route example
@auth_bp.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({'message': f'Hello, {current_user.name}! You have access to this route.'})


# Role-based protected route example
@auth_bp.route('/admin-only', methods=['GET'])
@login_required
def admin_only():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    return jsonify({'message': 'Welcome, admin!'})



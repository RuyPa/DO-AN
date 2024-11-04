import bcrypt
import mysql.connector
from flask import current_app
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask_bcrypt import Bcrypt
from datetime import datetime



bcrypt = Bcrypt()



def get_db_connection():
    return mysql.connector.connect(
        host=current_app.config['DB_HOST'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_DATABASE']
    )

# Create tbl_user table function (if it doesn't exist)
def create_user_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            address VARCHAR(100),
            role VARCHAR(100),
            created_date DATETIME,
            created_by VARCHAR(100)
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

# Add a new user function with password hashing (optional if you add a password field)
def add_user(name, email, address, role, created_by, password=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    created_date = datetime.now()  # Set the created date to the current timestamp
    if password:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    else:
        password_hash = None  # Use None if password column doesn't exist in tbl_user

    cursor.execute('''
        INSERT INTO tbl_user (name, email, address, role, created_date, created_by, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (name, email, address, role, created_date, created_by, password_hash))

    connection.commit()
    cursor.close()
    connection.close()

# Fetch a user by email
def get_user_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_user WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    return user_data

# Fetch a user by ID
def get_user_by_id(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_user WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    return user_data

def check_password(stored_password, provided_password):
    # Pass stored_password as a string, not as bytes
    return bcrypt.check_password_hash(stored_password, provided_password)

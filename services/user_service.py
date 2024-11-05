import app
from db import get_db_connection
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


def add_user(username, password, role='user'):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)', (username, password_hash, role))
    connection.commit()
    cursor.close()
    connection.close()

from db import get_db_connection
from models.traffic_sign import TrafficSign

def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_traffic_sign (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50) NOT NULL,
            description TEXT,
            path VARCHAR(255)
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

def get_all_signs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_traffic_sign')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [TrafficSign.from_row(row) for row in rows]

def get_sign_by_id(sign_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_traffic_sign WHERE id = %s', (sign_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    return TrafficSign.from_row(row) if row else None

def add_sign(sign: TrafficSign):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO tbl_traffic_sign (name, code, description, path) VALUES (%s, %s, %s, %s)',
                   (sign.name, sign.code, sign.description, sign.path))
    connection.commit()
    cursor.close()
    connection.close()

def update_sign(sign_id, name, code, description, path):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE tbl_traffic_sign SET name = %s, code = %s, description = %s, path = %s WHERE id = %s',
                   (name, code, description, path, sign_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_sign(sign_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM tbl_traffic_sign WHERE id = %s', (sign_id,))
    connection.commit()
    cursor.close()
    connection.close()

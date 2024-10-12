from db import get_db_connection
from models.label import Label
from services.traffic_sign_service import get_sign_by_id

def create_label(label: Label):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO tbl_label (centerX, centerY, height, width, sample_id, traffic_sign_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (label.centerX, label.centerY, label.height, label.width, label.sample_id, label.traffic_sign.id))
    connection.commit()
    cursor.close()
    connection.close()

def get_all_labels():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_label')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [Label.from_row(row) for row in rows]

# def get_label_by_id(label_id):
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute('SELECT * FROM tbl_label WHERE id = %s', (label_id,))
#     row = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return Label.from_row(row) if row else None
def get_label_by_id(label_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Lấy thông tin của Label từ bảng tbl_label
    cursor.execute('SELECT * FROM tbl_label WHERE id = %s', (label_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        connection.close()
        return None
    
    # Lấy thông tin của TrafficSign từ bảng traffic_sign dựa trên traffic_sign_id
    traffic_sign = get_sign_by_id(row['traffic_sign_id'])
    
    cursor.close()
    connection.close()

    # Trả về đối tượng Label, kèm theo TrafficSign
    return Label.from_row(row, traffic_sign=traffic_sign)

def update_label(label_id, centerX=None, centerY=None, height=None, width=None, sample_id=None, traffic_sign_id=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Chỉ cập nhật những trường có giá trị không None
    updates = []
    params = []

    if centerX is not None:
        updates.append('centerX = %s')
        params.append(centerX)
    if centerY is not None:
        updates.append('centerY = %s')
        params.append(centerY)
    if height is not None:
        updates.append('height = %s')
        params.append(height)
    if width is not None:
        updates.append('width = %s')
        params.append(width)
    if sample_id is not None:
        updates.append('tbl_sample_id = %s')
        params.append(sample_id)
    if traffic_sign_id is not None:
        updates.append('traffic_sign_id = %s')
        params.append(traffic_sign_id)

    params.append(label_id)
    cursor.execute(f'UPDATE tbl_label SET {", ".join(updates)} WHERE id = %s', tuple(params))
    
    connection.commit()
    cursor.close()
    connection.close()

def delete_label(label_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM tbl_label WHERE id = %s', (label_id,))
    connection.commit()
    cursor.close()
    connection.close()

# def get_labels_by_sample_id(sample_id):
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute('SELECT * FROM tbl_label WHERE sample_id = %s', (sample_id,))
#     rows = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return [Label.from_row(row) for row in rows]  # Trả về danh sách các đối tượng Label

def get_labels_by_sample_id(sample_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Lấy tất cả các label từ bảng tbl_label theo sample_id
    cursor.execute('SELECT * FROM tbl_label WHERE sample_id = %s', (sample_id,))
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()

    labels = []
    # Duyệt qua các label và lấy thông tin của TrafficSign tương ứng
    for row in rows:
        traffic_sign = get_sign_by_id(row['traffic_sign_id'])
        label = Label.from_row(row, traffic_sign=traffic_sign)
        labels.append(label)
    
    return labels
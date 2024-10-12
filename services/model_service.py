import random
from models.model import Model
from services.model_sample_service import get_model_samples_by_model_id
from db import get_db_connection

# Lấy thông tin model theo id
def get_model_by_id(model_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Thực hiện query lấy thông tin model theo id
    cursor.execute('''
        SELECT * FROM tbl_model WHERE id = %s
    ''', (model_id,))
    row = cursor.fetchone()
    
    # Nếu không tìm thấy thì trả về None
    if not row:
        cursor.close()
        connection.close()
        return None
    
    # Tạo object Model từ dữ liệu vừa lấy
    model = Model.from_row(row)
    
    # Gọi service lấy danh sách ModelSample liên quan đến model
    model.model_samples = get_model_samples_by_model_id(model.id)
    
    cursor.close()
    connection.close()
    
    return model

# Lấy tất cả các model
def get_all_models():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Thực hiện query lấy tất cả các model
    cursor.execute('SELECT * FROM tbl_model')
    rows = cursor.fetchall()
    
    models = []
    
    # Tạo list các object Model từ dữ liệu
    for row in rows:
        model = Model.from_row(row)
        # Lấy danh sách ModelSample cho mỗi model
        model.model_samples = get_model_samples_by_model_id(model.id)
        models.append(model)
    
    cursor.close()
    connection.close()
    
    return models


def add_model(sample_ids):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Giả lập thông số của model
        f1 = round(random.uniform(0.5, 1.0), 5)
        accuracy = round(random.uniform(0.5, 1.0), 5)
        precision = round(random.uniform(0.5, 1.0), 5)
        recall = round(random.uniform(0.5, 1.0), 5)

        # Tạo một model mới
        cursor.execute(
            '''INSERT INTO tbl_model (name, path, date, acc, pre, f1, recall, status) 
               VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)''',
            ('Model_' + str(random.randint(1000, 9999)), 'some/fake/path', accuracy, precision, f1, recall, 1)
        )

        model_id = cursor.lastrowid  # Lấy ID của model vừa tạo
        
        # Tạo các model_sample liên kết với các sample
        for sample_id in sample_ids:
            cursor.execute(
                '''INSERT INTO tbl_model_sample (model_id, sample_id, created_date)
                   VALUES (%s, %s, NOW())''',
                (model_id, sample_id)
            )
        
        # Commit các thay đổi vào cơ sở dữ liệu
        connection.commit()
        
        cursor.close()
        connection.close()

        return model_id
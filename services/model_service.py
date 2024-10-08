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

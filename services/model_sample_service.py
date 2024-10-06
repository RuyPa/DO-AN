from db import get_db_connection
from models.model_sample import ModelSample
from services.sample_service import get_sample_by_id

from models.model_sample import ModelSample
from models.sample import Sample
from models.label import Label
from models.traffic_sign import TrafficSign

def get_model_sample_by_id(model_sample_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Truy vấn một lần để lấy dữ liệu cả từ tbl_model_sample, tbl_sample và tbl_traffic_sign
    cursor.execute('''
        SELECT 
            ms.id as model_sample_id, ms.model_id, ms.created_date, ms.created_by,
            s.id as sample_id, s.code as sample_code, s.path as sample_path, s.name as sample_name,
            l.id as label_id, l.centerX, l.centerY, l.height, l.width,
            ts.id as traffic_sign_id, ts.name as traffic_sign_name, ts.description as traffic_sign_description, ts.path as traffic_sign_path
        FROM tbl_model_sample ms
        JOIN tbl_sample s ON ms.sample_id = s.id
        LEFT JOIN tbl_label l ON s.id = l.sample_id
        LEFT JOIN tbl_traffic_sign ts ON l.traffic_sign_id = ts.id
        WHERE ms.id = %s
    ''', (model_sample_id,))
    
    rows = cursor.fetchall()

    if not rows:
        return None
    
    # Xử lý dữ liệu để ánh xạ vào các model
    sample = None
    labels = []
    for row in rows:
        if sample is None:
            sample = Sample.from_prj(row)
        
        if row['label_id']:
            traffic_sign = TrafficSign.from_prj(row)
            label = Label.from_prj(row, traffic_sign)
            labels.append(label)
    
    sample.labels = labels

    model_sample = ModelSample.from_prj(row, sample)
    
    cursor.close()
    connection.close()
    
    return model_sample

def get_model_samples_by_model_id(model_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Truy vấn để lấy dữ liệu của model_sample, sample, label, và traffic_sign theo model_id
    cursor.execute('''
        SELECT 
            ms.id as model_sample_id, ms.model_id, ms.created_date, ms.created_by,
            s.id as sample_id, s.code as sample_code, s.path as sample_path, s.name as sample_name,
            l.id as label_id, l.centerX, l.centerY, l.height, l.width,
            ts.id as traffic_sign_id, ts.name as traffic_sign_name, ts.description as traffic_sign_description, ts.path as traffic_sign_path
        FROM tbl_model_sample ms
        JOIN tbl_sample s ON ms.sample_id = s.id
        LEFT JOIN tbl_label l ON s.id = l.sample_id
        LEFT JOIN tbl_traffic_sign ts ON l.traffic_sign_id = ts.id
        WHERE ms.model_id = %s
    ''', (model_id,))
    
    rows = cursor.fetchall()

    model_samples_dict = {}
    
    # Ánh xạ dữ liệu trả về
    for row in rows:
        if row['model_sample_id'] not in model_samples_dict:
            sample = Sample.from_prj(row)
            model_sample = ModelSample.from_prj(row, sample)
            model_samples_dict[row['model_sample_id']] = model_sample
        
        if row['label_id']:
            traffic_sign = TrafficSign.from_prj(row)
            label = Label.from_prj(row, traffic_sign)
            model_samples_dict[row['model_sample_id']].sample.labels.append(label)
    
    cursor.close()
    connection.close()
    
    return list(model_samples_dict.values())

def add_model_sample(model_sample):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        'INSERT INTO tbl_model_sample (model_id, sample_id, created_date, created_by) VALUES (%s, %s, %s, %s)',
        (model_sample.model_id, model_sample.sample.id, model_sample.created_date, model_sample.created_by)
    )
    
    connection.commit()
    cursor.close()
    connection.close()

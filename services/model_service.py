import csv
import os
import random
import shutil
import time
import uuid

from flask import jsonify, send_file
from sklearn.model_selection import train_test_split
import yaml
from models.model import Model
from services.model_sample_service import get_model_samples_by_model_id
from db import get_db_connection
from ultralytics import YOLO
import torch


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

def copy_image(image_path, save_path):
    try:
        shutil.copy(image_path, save_path)
    except Exception as e:
        print(f"Error copying image: {e}")

def write_label_file(label_save_path, label_content=""):
    try:
        with open(label_save_path, 'w', encoding='utf-8') as f:
            f.write(label_content)
    except Exception as e:
        print(f"Error writing label file: {e}")

def add_model(sample_ids, log_callback):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

        # Truy vấn để lấy thông tin sample và nhãn từ database
     # Truy vấn để lấy thông tin sample và nhãn từ database
    format_strings = ','.join(['%s'] * len(sample_ids))
    query = f'''
        SELECT 
            s.path as sample_path, 
            s.name as sample_name, 
            s.code as sample_code,
            l.centerX, l.centerY, l.height, l.width, 
            ts.id as traffic_sign_id
        FROM tbl_sample s
        LEFT JOIN tbl_label l ON s.id = l.sample_id
        LEFT JOIN tbl_traffic_sign ts ON l.traffic_sign_id = ts.id
        WHERE s.id IN ({format_strings})
    '''
    cursor.execute(query, tuple(sample_ids))
    samples_with_labels = cursor.fetchall()

    log_callback("Creating directories and preparing data...\n")
    yield

    # Tạo thư mục chính với UUID
    base_dir = os.path.join('static', str(uuid.uuid4()))
    os.makedirs(os.path.join(base_dir, 'train', 'images'))
    os.makedirs(os.path.join(base_dir, 'train', 'labels'))
    os.makedirs(os.path.join(base_dir, 'valid', 'images'))
    os.makedirs(os.path.join(base_dir, 'valid', 'labels'))

    # Tạo danh sách các ảnh và nội dung nhãn
    image_paths = {}
    labels = {}

    log_callback("Processing samples and labels...\n")
    yield

    for sample in samples_with_labels:
        sample_path = sample['sample_path']
        sample_name = sample['sample_name']

        # Nếu có nhãn, ghi thông tin nhãn, nếu không, tạo nội dung rỗng
        label_content = f"{sample['centerX']} {sample['centerY']} {sample['height']} {sample['width']} {sample['traffic_sign_id']}\n" if sample['centerX'] and sample['centerY'] else ""
        
        if sample_name not in labels:
            labels[sample_name] = label_content
        else:
            labels[sample_name] += label_content

        # Đảm bảo không trùng lặp
        image_paths[sample_name] = sample_path

    # Chia dữ liệu thành train và valid theo tỷ lệ 7:3
    log_callback("Splitting data into training and validation sets...\n")
    yield

    sample_names = list(image_paths.keys())
    train_samples, valid_samples = train_test_split(sample_names, test_size=0.3, random_state=42)

    # Xử lý sao chép ảnh và ghi file nhãn cho train
    for sample_name in train_samples:
        image_path = image_paths[sample_name]
        label_content = labels[sample_name]

        image_save_path = os.path.join(base_dir, 'train', 'images', sample_name)
        label_save_path = os.path.join(base_dir, 'train', 'labels', sample_name.replace('.png', '.txt'))

        # Sao chép ảnh và ghi file nhãn
        copy_image(image_path, image_save_path)
        write_label_file(label_save_path, label_content)

    # Xử lý sao chép ảnh và ghi file nhãn cho valid
    for sample_name in valid_samples:
        image_path = image_paths[sample_name]
        label_content = labels[sample_name]

        image_save_path = os.path.join(base_dir, 'valid', 'images', sample_name)
        label_save_path = os.path.join(base_dir, 'valid', 'labels', sample_name.replace('.png', '.txt'))

        # Sao chép ảnh và ghi file nhãn
        copy_image(image_path, image_save_path)
        write_label_file(label_save_path, label_content)

    # Ghi file config.yaml  
    log_callback("Generating config.yaml...\n")
    yield

    config_path = os.path.join(base_dir, 'config.yaml')
    config_content = {
        'path': base_dir,
        'train': 'train/images',
        'val': 'valid/images',
        'test': 'test/images',  # Thư mục test có thể không dùng
        'names': {
            0: 'cam_di_nguoc_chieu',
            1: 'cam_dung_va_do_xe',
            2: 'cam_re_trai',
            3: 'gioi_han_toc_do',
            4: 'bien_bao_cam',
            5: 'bien_nguy_hiem',
            6: 'bien_hieu_lenh'
        }
    }

    # Ghi file config.yaml
    with open(config_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(config_content, yaml_file)
        

    relative_config_path = os.path.join(base_dir, 'config.yaml').replace('\\', '/')

    log_callback(f"Config path: {relative_config_path}\n")
    yield

    # Train the YOLO model
    log_callback("Starting model training...\n")
    yield

    print(f"Config path: {relative_config_path}")

    # Set up the YOLO model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    model = YOLO('static/yolov8n.pt')

    # Train the model using the relative config path
    results = model.train(data=relative_config_path, epochs=10, imgsz=640, device=0)

    log_callback("Model training completed!\n")
    yield


    cursor.execute("SELECT id, path FROM tbl_model ORDER BY id DESC LIMIT 1")
    last_model = cursor.fetchone()

    last_path = last_model['path']

    base, train_num = os.path.split(last_path)
    
    num = int(train_num.replace('train', ''))
    next_num = num + 1
    new_train_path = f"train{next_num}"
    new_path = os.path.join(base, new_train_path)

    results_csv_path = os.path.join(new_path, 'results.csv')


    precision = 0
    recall = 0
    f1 = 0
    count = 0
    acc = 0

    with open(results_csv_path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row

        for row in reader:
            count += 1
            precision += float(row[4])
            recall += float(row[5])
            acc += float(row[7])
            # Compute F1 based on precision and recall at each iteration
            f1 += (2 * precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

    # Average calculations
    avg_precision = precision / count
    avg_recall = recall / count
    avg_f1 = f1 / count
    avg_acc = acc / count

    # Tạo một model mới
    cursor.execute(
        '''INSERT INTO tbl_model (name, path, date, acc, pre, f1, recall, status) 
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)''',
        ('best.pt', new_path, avg_acc, avg_precision, avg_f1, avg_recall, 0)
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

def add_model_with_logging(sample_ids):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to get sample and label data
    format_strings = ','.join(['%s'] * len(sample_ids))
    query = f'''
        SELECT 
            s.path as sample_path, 
            s.name as sample_name, 
            s.code as sample_code,
            l.centerX, l.centerY, l.height, l.width, 
            ts.id as traffic_sign_id
        FROM tbl_sample s
        LEFT JOIN tbl_label l ON s.id = l.sample_id
        LEFT JOIN tbl_traffic_sign ts ON l.traffic_sign_id = ts.id
        WHERE s.id IN ({format_strings})
    '''
    cursor.execute(query, tuple(sample_ids))
    samples_with_labels = cursor.fetchall()


    # Create directories for train and validation
    base_dir = os.path.join('static', str(uuid.uuid4()))
    os.makedirs(os.path.join(base_dir, 'train', 'images'))
    os.makedirs(os.path.join(base_dir, 'train', 'labels'))
    os.makedirs(os.path.join(base_dir, 'valid', 'images'))
    os.makedirs(os.path.join(base_dir, 'valid', 'labels'))

    image_paths = {}
    labels = {}



    for sample in samples_with_labels:
        sample_path = sample['sample_path']
        sample_name = sample['sample_name']

        # If there's a label, write the content, otherwise create an empty file
        label_content = f"{sample['centerX']} {sample['centerY']} {sample['height']} {sample['width']} {sample['traffic_sign_id']}\n" if sample['centerX'] and sample['centerY'] else ""

        if sample_name not in labels:
            labels[sample_name] = label_content
        else:
            labels[sample_name] += label_content

        image_paths[sample_name] = sample_path


    # Split into train and valid datasets
    sample_names = list(image_paths.keys())
    train_samples, valid_samples = train_test_split(sample_names, test_size=0.3, random_state=42)

    # Copy train samples
    for sample_name in train_samples:
        image_path = image_paths[sample_name]
        label_content = labels[sample_name]
        image_save_path = os.path.join(base_dir, 'train', 'images', sample_name)
        label_save_path = os.path.join(base_dir, 'train', 'labels', sample_name.replace('.png', '.txt'))
        copy_image(image_path, image_save_path)
        write_label_file(label_save_path, label_content)

    # Copy valid samples
    for sample_name in valid_samples:
        image_path = image_paths[sample_name]
        label_content = labels[sample_name]
        image_save_path = os.path.join(base_dir, 'valid', 'images', sample_name)
        label_save_path = os.path.join(base_dir, 'valid', 'labels', sample_name.replace('.png', '.txt'))
        copy_image(image_path, image_save_path)
        write_label_file(label_save_path, label_content)
    # Write config.yaml file
    config_path = os.path.join(base_dir, 'config.yaml')
    config_content = {
        'path': base_dir,
        'train': 'train/images',
        'val': 'valid/images',
        'names': {
            0: 'cam_di_nguoc_chieu',
            1: 'cam_dung_va_do_xe',
            2: 'cam_re_trai',
            3: 'gioi_han_toc_do',
            4: 'bien_bao_cam',
            5: 'bien_nguy_hiem',
            6: 'bien_hieu_lenh'
        }
    }

    with open(config_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(config_content, yaml_file)
        
    relative_config_path = os.path.join(base_dir, 'config.yaml').replace('\\', '/')


    # Train YOLO model
    model = YOLO('static/yolov8n.pt')
    results = model.train(data=relative_config_path, epochs=10, imgsz=640, device=0)

    cursor.close()
    connection.close()

def delete_model(id):
    # Kết nối đến cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()

    # Xóa các bản ghi model_sample liên quan đến model
    delete_model_samples_query = "DELETE FROM tbl_model_sample WHERE model_id = %s"
    cursor.execute(delete_model_samples_query, (id,))

    # Xóa model
    delete_model_query = "DELETE FROM tbl_model WHERE id = %s"
    cursor.execute(delete_model_query, (id,))

    # Lưu các thay đổi
    connection.commit()

    return {'status': 'success', 'message': 'Model and associated samples deleted successfully'}

def set_active_model(model_id):
    # Kết nối đến cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()

    # Đặt tất cả các model khác về trạng thái 0
    reset_status_query = "UPDATE tbl_model SET status = 0 WHERE status = 1"
    cursor.execute(reset_status_query)

    # Đặt model được chỉ định về trạng thái 1
    set_active_query = "UPDATE tbl_model SET status = 1 WHERE id = %s"
    cursor.execute(set_active_query, (model_id,))

    # Lưu các thay đổi
    connection.commit()

    return {'status': 'success', 'message': f'Model {model_id} set to active successfully'}

def get_model_path_by_id(model_id):
    # Lấy đường dẫn của model từ cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT path FROM tbl_model WHERE id = %s", (model_id,))
    model = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return model['path']


def download_model_file(model_path):
    # Gửi file về phía người dùng
    if not os.path.exists(model_path):
        return jsonify({"error": "File not found"}), 404
    try:
        return send_file(model_path, as_attachment=True)
    except Exception as e:
        print(f"Error sending file: {e}")
        return jsonify({"error": "Could not send file"}), 500

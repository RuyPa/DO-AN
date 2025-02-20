import csv
from io import BytesIO
import cloudinary
from flask import Flask, abort, request, jsonify, send_file, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
import threading
import shutil
import uuid
import time
import os
import requests
import yaml
from sklearn.model_selection import train_test_split
from ultralytics import YOLO
import torch
from db import get_db_connection

import os
os.environ["WANDB_MODE"] = "offline"
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")  # Sử dụng threading cho SocketIO

# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app, supports_credentials=True)  # Allow credentials for all domains


# # Database configuration
# app.config['DB_HOST'] = 'localhost'
# app.config['DB_USER'] = 'root'
# app.config['DB_PASSWORD'] = '123456'
# app.config['DB_DATABASE'] = 'traffic_sign'

app.config['DB_HOST'] = '45.252.248.164'
app.config['DB_USER'] = 'duyall'
app.config['DB_PASSWORD'] = 'Duydoba@02'
app.config['DB_DATABASE'] = 'traffic_sign'

# Import routes and services after app config
from services.traffic_sign_service import create_tables
from routes.routes import api_routes
from routes.sample_route import sample_bp
from routes.label_route import label_bp
from routes.model_sample_route import model_sample_bp
from routes.model_route import model_bp
from routes.auth_route import auth_bp
from routes.user_route import user_bp

# Cấu hình Cloudinary
cloudinary.config( 
    cloud_name="dkf74ju3o", 
    api_key="639453249624293", 
    api_secret="2GY34a7PT11RkkaTwEsKP9eYkwI",
    secure=True
)
# Register blueprints
app.register_blueprint(api_routes)
app.register_blueprint(sample_bp)
app.register_blueprint(label_bp)
app.register_blueprint(model_sample_bp)
app.register_blueprint(model_bp)

# Register the auth blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

from flask_bcrypt import Bcrypt

# app.secret_key = 'jkasKAHS7QFjhagd662QHFCASHFGAW56QAWFHIHAWIEFHCBvVAS'  # Needed for session management
bcrypt = Bcrypt(app)

app.config['JWT_SECRET_KEY'] = 'jkasKAHS7QFjhagd662QHFCASHFGAW56QAWFHIHAWIEFHCBvVAS'  # Thay bằng khóa bí mật của bạn
jwt = JWTManager(app)

# login_manager = LoginManager()
# login_manager.init_app(app)  # Attach the LoginManager to the app
# login_manager.login_view = 'login'  # Set the login view (route name)

# # Optionally, you can also set a custom message for unauthorized access
# login_manager.login_message = "Please log in to access this page."


from services.auth_service import User, role_required

# @login_manager.unauthorized_handler
# def unauthorized():
#     # This function runs if a user who is not logged in tries to access a protected route
#     return jsonify({'error': 'You must be logged in to access this resource'}), 401

# @login_manager.user_loader
# def load_user(user_id):
#     return User.get_user_by_id(user_id)

@jwt.unauthorized_loader
def custom_unauthorized_response(callback):
    return jsonify({
        'error': 'You must be logged in to access this resource',
        'message': 'Missing or invalid token'
    }), 401

# Callback khi token hết hạn
@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token has expired',
        'message': 'Please log in again to get a new token'
    }), 401

# Callback khi token không hợp lệ
@jwt.invalid_token_loader
def custom_invalid_token_response(callback):
    return jsonify({
        'error': 'Invalid token',
        'message': 'The provided token is not valid'
    }), 422

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-file', methods=['GET'])
def get_file():
    file_path = request.args.get('path')
    if not file_path or not os.path.exists(file_path):
        return abort(404, description="File not found")
    return send_file(file_path, as_attachment=False)

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

def on_rm_error(func, path, exc_info):
    """
    Error handler for `shutil.rmtree`.
    If the error is due to access rights (WinError 5), change permissions and retry.
    """
    import stat
    if not os.access(path, os.W_OK):
        # Change permission to allow write access
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def try_remove_directory(path, retries=3, delay=5):
    """
    Attempt to remove a directory with retries if a PermissionError occurs.
    """
    for attempt in range(retries):
        try:
            shutil.rmtree(path, onerror=on_rm_error)
            print(f"Successfully removed directory: {path}")
            break
        except PermissionError as e:
            print(f"PermissionError: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"Error removing directory {path}: {e}")
            break
    else:
        print(f"Failed to remove directory {path} after {retries} retries.")

def add_model_with_logging(app, sample_ids):
    with app.app_context():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Kiểm tra nếu sample_ids có phần tử đầu tiên là 0
        if sample_ids[0] == 0:
            # Nếu phần tử đầu tiên là 0, lấy tất cả các sample trong bảng tbl_sample
            query = '''
                SELECT 
                    s.path as sample_path, 
                    s.name as sample_name, 
                    s.code as sample_code,
                    l.centerX, l.centerY, l.height, l.width, 
                    ts.id as traffic_sign_id,
                    s.id as sample_id  -- Lấy thêm sample_id để giúp xác định mẫu
                FROM tbl_sample s
                LEFT JOIN tbl_label l ON s.id = l.sample_id
                LEFT JOIN tbl_traffic_sign ts ON l.traffic_sign_id = ts.id
                JOIN (
                    SELECT id
                    FROM tbl_sample
                    LIMIT 500
                ) subquery ON s.id = subquery.id;
            '''
            cursor.execute(query)
            samples_with_labels = cursor.fetchall()

            # Cập nhật lại sample_ids từ samples_with_labels
            sample_ids.clear()  # Xóa hết thông tin trong sample_ids
            sample_ids.extend([sample['sample_id'] for sample in samples_with_labels])  # Thêm các sample_id mới vào
        else:
            # Nếu không, lấy sample theo sample_ids
            format_strings = ','.join(['%s'] * len(sample_ids))
            query = f'''
                SELECT 
                    s.path as sample_path, 
                    s.name as sample_name, 
                    s.code as sample_code,
                    l.centerX, l.centerY, l.height, l.width, 
                    ts.id as traffic_sign_id,
                    s.id as sample_id  -- Lấy thêm sample_id để giúp xác định mẫu
                FROM tbl_sample s
                LEFT JOIN tbl_label l ON s.id = l.sample_id
                LEFT JOIN tbl_traffic_sign ts ON l.traffic_sign_id = ts.id
                WHERE s.id IN ({format_strings})
            '''
            cursor.execute(query, tuple(sample_ids))
            samples_with_labels = cursor.fetchall()

            # Cập nhật lại sample_ids từ samples_with_labels
            sample_ids.clear()  # Xóa hết thông tin trong sample_ids
            sample_ids.extend([sample['sample_id'] for sample in samples_with_labels])  # Thêm các sample_id mới vào

        # Emit log and yield progress to the frontend
        socketio.emit('progress', {'message': "Creating directories and preparing data...", 'progress': 10})
        time.sleep(0.1)

        # Create directories for train and validation
        base_dir = os.path.join('static', str(uuid.uuid4()))
        os.makedirs(os.path.join(base_dir, 'train', 'images'))
        os.makedirs(os.path.join(base_dir, 'train', 'labels'))
        os.makedirs(os.path.join(base_dir, 'valid', 'images'))
        os.makedirs(os.path.join(base_dir, 'valid', 'labels'))

        image_paths = {}
        labels = {}

        # Emit progress to the frontend
        socketio.emit('progress', {'message': "Processing samples and labels...", 'progress': 20})
        time.sleep(0.1)

        for sample in samples_with_labels:
            sample_path = sample['sample_path']  # Đây là URL từ cloud
            sample_name = sample['sample_name']

            # If there's a label, write the content, otherwise create an empty file
            label_content = f"{sample['traffic_sign_id']} {sample['centerX']} {sample['centerY']} {sample['height']} {sample['width']}\n" if sample['centerX'] and sample['centerY'] else ""

            if sample_name not in labels:
                labels[sample_name] = label_content
            else:
                labels[sample_name] += label_content

            # Save image URL (no need to keep the path if it's a URL)
            image_paths[sample_name] = sample_path

        # Emit progress to the frontend
        socketio.emit('progress', {'message': "Splitting data into training and validation sets...", 'progress': 30})
        time.sleep(0.1)

        # Split into train and valid datasets
        sample_names = list(image_paths.keys())
        train_samples, valid_samples = train_test_split(sample_names, test_size=0.3, random_state=42)

        # Download and save train samples
        for sample_name in train_samples:
            image_url = image_paths[sample_name]  # Cloud URL
            label_content = labels[sample_name]
            
            # Download image from Cloud
            image_save_path = os.path.join(base_dir, 'train', 'images', sample_name)
            label_save_path = os.path.join(base_dir, 'train', 'labels', sample_name.replace('.png', '.txt'))
            
            # Download image from Cloud
            download_and_save_image(image_url, image_save_path)
            write_label_file(label_save_path, label_content)

        # Download and save valid samples
        for sample_name in valid_samples:
            image_url = image_paths[sample_name]  # Cloud URL
            label_content = labels[sample_name]
            
            # Download image from Cloud
            image_save_path = os.path.join(base_dir, 'valid', 'images', sample_name)
            label_save_path = os.path.join(base_dir, 'valid', 'labels', sample_name.replace('.png', '.txt'))
            
            # Download image from Cloud
            download_and_save_image(image_url, image_save_path)
            write_label_file(label_save_path, label_content)

        # Emit progress to the frontend
        socketio.emit('progress', {'message': "Generating config.yaml...", 'progress': 60})
        time.sleep(0.1)

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

        relative_config_path = os.path.join(base_dir, 'config.yaml')

        # Emit progress to the frontend
        socketio.emit('progress', {'message': f"Config path: {relative_config_path}", 'progress': 70})
        time.sleep(0.1)

        socketio.emit('progress', {'message': "Starting model training...", 'progress': 80})
        time.sleep(0.1)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")

        # Train YOLO model
        model = YOLO('static/yolov8n.pt')
        # results = model.train(data=relative_config_path, epochs=10, imgsz=640, batch=4, device=0)
        results = model.train(data=relative_config_path, epochs=1, imgsz=640, batch=2, device=0)

        socketio.emit('progress', {'message': "Model training completed!", 'progress': 100})

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

            # Giả sử bạn đang đọc dữ liệu từ một file CSV
            for row in reader:
                count += 1
                
                # Kiểm tra và thay thế 'nan' bằng 0
                precision_value = float(row[4]) if row[4] != 'nan' else 0
                recall_value = float(row[5]) if row[5] != 'nan' else 0
                acc_value = float(row[7]) if row[7] != 'nan' else 0

                precision += precision_value
                recall += recall_value
                acc += acc_value
                
                # Tính F1 tại mỗi lần lặp
                if precision_value + recall_value != 0:
                    f1 += (2 * precision_value * recall_value) / (precision_value + recall_value)
                else:
                    f1 += 0

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

            # Close the connection
            cursor.close()
            connection.close()


@app.route('/api/start-model', methods=['POST'])
def start_model():
    data = request.get_json()

    if 'samples' not in data or not isinstance(data['samples'], list):
        return jsonify({'error': 'Missing or invalid sample list'}), 400

    sample_ids = data['samples']

    # Run model creation process in background thread
    threading.Thread(target=add_model_with_logging, args=(app, sample_ids)).start()

    return jsonify({'message': 'Model creation started!'})




def retrain_model_with_logging(app, sample_ids, id):
    with app.app_context():
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

        # Emit log and yield progress to the frontend
        socketio.emit('progress', {'message': "Creating directories and preparing data...", 'progress': 10})
        time.sleep(0.1)

        # Create directories for train and validation
        base_dir = os.path.join('static', str(uuid.uuid4()))
        os.makedirs(os.path.join(base_dir, 'train', 'images'))
        os.makedirs(os.path.join(base_dir, 'train', 'labels'))
        os.makedirs(os.path.join(base_dir, 'valid', 'images'))
        os.makedirs(os.path.join(base_dir, 'valid', 'labels'))

        image_paths = {}
        labels = {}

        # Emit progress to the frontend
        socketio.emit('progress', {'message': "Processing samples and labels...", 'progress': 20})
        time.sleep(0.1)

        for sample in samples_with_labels:
            sample_path = sample['sample_path']
            sample_name = sample['sample_name']

            # If there's a label, write the content, otherwise create an empty file
            label_content = f"{sample['traffic_sign_id']} {sample['centerX']} {sample['centerY']} {sample['height']} {sample['width']}\n" if sample['centerX'] and sample['centerY'] else ""

            if sample_name not in labels:
                labels[sample_name] = label_content
            else:
                labels[sample_name] += label_content

            # Save image URL (no need to keep the path if it's a URL)
            image_paths[sample_name] = sample_path

        # Emit progress to the frontend
        socketio.emit('progress', {'message': "Splitting data into training and validation sets...", 'progress': 30})
        time.sleep(0.1)

        # Split into train and valid datasets
        sample_names = list(image_paths.keys())
        train_samples, valid_samples = train_test_split(sample_names, test_size=0.3, random_state=42)

        # Download and save train samples
        for sample_name in train_samples:
            image_url = image_paths[sample_name]  # Cloudinary URL
            label_content = labels[sample_name]
            
            # Download image from Cloudinary
            image_save_path = os.path.join(base_dir, 'train', 'images', sample_name)
            label_save_path = os.path.join(base_dir, 'train', 'labels', sample_name.replace('.png', '.txt'))
            
            # Download image from Cloudinary
            download_and_save_image(image_url, image_save_path)
            write_label_file(label_save_path, label_content)

        # Download and save valid samples
        for sample_name in valid_samples:
            image_url = image_paths[sample_name]  # Cloudinary URL
            label_content = labels[sample_name]
            
            # Download image from Cloudinary
            image_save_path = os.path.join(base_dir, 'valid', 'images', sample_name)
            label_save_path = os.path.join(base_dir, 'valid', 'labels', sample_name.replace('.png', '.txt'))
            
            # Download image from Cloudinary
            download_and_save_image(image_url, image_save_path)
            write_label_file(label_save_path, label_content)

        # Emit progress to the frontend
        socketio.emit('progress', {'message': "Generating config.yaml...", 'progress': 60})
        time.sleep(0.1)

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

        relative_config_path = os.path.join(base_dir, 'config.yaml')

        # Emit progress to the frontend
        socketio.emit('progress', {'message': f"Config path: {relative_config_path}", 'progress': 70})
        time.sleep(0.1)

        socketio.emit('progress', {'message': "Starting model training...", 'progress': 80})
        time.sleep(0.1)

        # Fetch the model path based on the given id
        cursor.execute("SELECT md.path FROM tbl_model md WHERE md.id = %s", (id,))
        model_path_result = cursor.fetchone()
        model_path = model_path_result['path'] if model_path_result else 'static/yolov8n.pt'

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")

        # Train YOLO model using the fetched model path
        model = YOLO(model_path + "\weights\\best.pt")
        # results = model.train(data=relative_config_path, epochs=10, imgsz=640, batch=2, device=0)
        results = model.train(data=relative_config_path, epochs=1, imgsz=640, batch=2, device=0)
        socketio.emit('progress', {'message': "Model training completed!", 'progress': 100})

        # Fetch last model and create a new record in the database
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

                    # Giả sử bạn đang đọc dữ liệu từ một file CSV
            for row in reader:
                count += 1
                
                # Kiểm tra và thay thế 'nan' bằng 0
                precision_value = float(row[4]) if row[4] != 'nan' else 0
                recall_value = float(row[5]) if row[5] != 'nan' else 0
                acc_value = float(row[7]) if row[7] != 'nan' else 0

                precision += precision_value
                recall += recall_value
                acc += acc_value
                
                # Tính F1 tại mỗi lần lặp
                if precision_value + recall_value != 0:
                    f1 += (2 * precision_value * recall_value) / (precision_value + recall_value)
                else:
                    f1 += 0

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

            # Close the connection
            cursor.close()
            connection.close()
from PIL import Image

def download_and_save_image(image_url, save_path):
    # Download the image from URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.save(save_path)


@app.route('/api/retrain-model/<int:id>', methods=['POST'])
def retrain_model(id):
    data = request.get_json()

    if 'samples' not in data or not isinstance(data['samples'], list):
        return jsonify({'error': 'Missing or invalid sample list'}), 400

    sample_ids = data['samples']

    # Run model creation process in background thread
    threading.Thread(target=retrain_model_with_logging, args=(app, sample_ids, id)).start()

    return jsonify({'message': 'Model creation started!'})

if __name__ == '__main__':
    # socketio.run(app, host='127.0.0.1', port=5000, debug=False)
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)


from flask import Flask, abort, request, send_file
from flask_cors import CORS
import subprocess  # Thêm import subprocess
from flask import Flask, send_file, abort, request  # Đã thêm import request
import os  # Đã thêm import os

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Cấu hình cơ sở dữ liệu
app.config['DB_HOST'] = 'localhost'
app.config['DB_USER'] = 'root'
app.config['DB_PASSWORD'] = '123456'
app.config['DB_DATABASE'] = 'traffic_sign'

# Import các module sau khi cấu hình cơ sở dữ liệu
from services.traffic_sign_service import create_tables
from routes.routes import api_routes
from routes.sample_route import sample_bp
from routes.label_route import label_bp
from routes.model_sample_route import model_sample_bp
from routes.model_route import model_bp

@app.route('/get-file', methods=['GET'])
def get_file():
    # Lấy đường dẫn file từ query string, ví dụ: /get-file?path=C:/Users/YourName/Downloads/file.png
    file_path = request.args.get('path')

    # Kiểm tra xem file có tồn tại không
    if not file_path or not os.path.exists(file_path):
        return abort(404, description="File not found")

    # Trả về file sử dụng Flask's send_file
    return send_file(file_path, as_attachment=False)
# Đăng ký các blueprint
app.register_blueprint(api_routes)
app.register_blueprint(sample_bp)
app.register_blueprint(label_bp)
app.register_blueprint(model_sample_bp)
app.register_blueprint(model_bp)

if __name__ == '__main__':
    app.run(debug=False)

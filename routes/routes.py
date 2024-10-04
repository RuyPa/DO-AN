from flask import Blueprint, jsonify, request, abort
from models.traffic_sign import TrafficSign
from cloudinary.uploader import upload
import cloudinary
cloudinary.config( 
        cloud_name = "dkf74ju3o", 
        api_key = "639453249624293", 
        api_secret = "2GY34a7PT11RkkaTwEsKP9eYkwI",
        secure = True
    )
from services.traffic_sign_service import (
    get_all_signs,
    get_sign_by_id,
    add_sign,
    update_sign,
    delete_sign
)

api_routes = Blueprint('api_routes', __name__)


@api_routes.route('/api/traffic_signs', methods=['GET'])
def get_signs():
    signs = get_all_signs()
    return jsonify([sign.to_dict() for sign in signs])

@api_routes.route('/api/traffic_signs/<int:id>', methods=['GET'])
def get_sign(id):
    sign = get_sign_by_id(id)
    if sign is None:
        abort(404, description="Sign not found")
    return jsonify(sign.to_dict())

# @api_routes.route('/api/traffic_signs', methods=['POST'])
# def create_sign():
#     data = request.get_json()
    
#     if not data:
#         abort(400, description="Request body is missing or not valid JSON")
    
#     name = data.get('name')
#     code = data.get('code')  
#     description = data.get('description', '')  
#     path = data.get('path', '') 
    
#     if not name or not code:
#         abort(400, description="Name and Code are required")
    
#     sign = TrafficSign(name=name, code=code, description=description, path=path)
    
#     add_sign(sign)
    
#     return jsonify({'message': 'Traffic sign created successfully'}), 201
@api_routes.route('/api/traffic_signs', methods=['POST'])
def create_sign():
    data = request.form  # Dữ liệu không phải JSON, mà là form-data
    
    # Lấy thông tin từ form-data
    name = data.get('name')
    code = data.get('code')  
    description = data.get('description', '')  
    
    # Kiểm tra thông tin bắt buộc
    if not name or not code:
        abort(400, description="Name and Code are required")
    
    # Xử lý file ảnh
    file = request.files.get('image')  # Nhận file từ multipart/form-data
    if not file:
        abort(400, description="Image file is required")
    
    try:
        # Upload file lên Cloudinary
        upload_result = cloudinary.uploader.upload(file)
        path = upload_result.get('secure_url')  # Nhận URL an toàn của ảnh đã upload
        
    except Exception as e:
        abort(500, description=f"Image upload failed: {str(e)}")
    
    # Tạo object TrafficSign và thêm vào database
    sign = TrafficSign(name=name, code=code, description=description, path=path)
    add_sign(sign)
    
    return jsonify({'message': 'Traffic sign created successfully'}), 201

@api_routes.route('/api/traffic_signs/<int:id>', methods=['PUT'])
def update_sign_route(id):
    data = request.get_json()
    name = data.get('name')
    code = data.get('code')
    description = data.get('description')
    path = data.get('path')
    
    if not name or not code:
        abort(400, description="Name and Code are required")
    
    update_sign(id, name, code, description, path)
    
    return jsonify({'message': 'Traffic sign updated successfully'})

@api_routes.route('/api/traffic_signs/<int:id>', methods=['DELETE'])
def delete_sign_route(id):
    delete_sign(id)
    return jsonify({'message': 'Traffic sign deleted successfully'})

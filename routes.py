# from flask import Blueprint, jsonify, request, abort
# from models.traffic_sign import TrafficSign
# from services.traffic_sign_service import (
#     get_all_signs,
#     get_sign_by_id,
#     add_sign,
#     update_sign,
#     delete_sign
# )

# api_routes = Blueprint('api_routes', __name__)

# @api_routes.route('/api/signs', methods=['GET'])
# def get_signs():
#     signs = get_all_signs()
#     return jsonify([sign.to_dict() for sign in signs])

# @api_routes.route('/api/signs/<int:id>', methods=['GET'])
# def get_sign(id):
#     sign = get_sign_by_id(id)
#     if sign is None:
#         abort(404, description="Sign not found")
#     return jsonify(sign.to_dict())

# @api_routes.route('/api/signs', methods=['POST'])
# def create_sign():
#     data = request.get_json()
    
#     if not data:
#         abort(400, description="Request body is missing or not valid JSON")
    
#     name = data.get('name')
#     description = data.get('description', '')  
#     img_url = data.get('img_url', '') 
    
#     if not name:
#         abort(400, description="Name is required")
    
#     sign = TrafficSign(name=name, description=description, img_url=img_url)
    
#     add_sign(sign)
    
#     return jsonify({'message': 'Sign created successfully'}), 201

# @api_routes.route('/api/signs/<int:id>', methods=['PUT'])
# def update_sign_route(id):
#     data = request.json
#     name = data.get('name')
#     description = data.get('description')
#     img_url = data.get('img_url')
#     if not name:
#         abort(400, description="Name is required")
#     update_sign(id, name, description, img_url)
#     return jsonify({'message': 'Sign updated successfully'})

# @api_routes.route('/api/signs/<int:id>', methods=['DELETE'])
# def delete_sign_route(id):
#     delete_sign(id)
#     return jsonify({'message': 'Sign deleted successfully'})

from flask import Blueprint, jsonify, request, abort
from models.traffic_sign import TrafficSign
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

@api_routes.route('/api/traffic_signs', methods=['POST'])
def create_sign():
    data = request.get_json()
    
    if not data:
        abort(400, description="Request body is missing or not valid JSON")
    
    name = data.get('name')
    code = data.get('code')  
    description = data.get('description', '')  
    path = data.get('path', '') 
    
    if not name or not code:
        abort(400, description="Name and Code are required")
    
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

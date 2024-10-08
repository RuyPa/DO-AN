from flask import Blueprint, jsonify
from services.model_service import get_model_by_id, get_all_models

model_bp = Blueprint('model_bp', __name__)

# API lấy tất cả models
@model_bp.route('/api/models', methods=['GET'])
def get_models():
    models = get_all_models()
    return jsonify([model.to_dict() for model in models]), 200

# API lấy model theo id
@model_bp.route('/api/models/<int:id>', methods=['GET'])
def get_model(id):
    model = get_model_by_id(id)
    if model:
        return jsonify(model.to_dict()), 200
    else:
        return jsonify({'message': 'Model not found'}), 404

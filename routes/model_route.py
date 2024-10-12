import random
from flask import Blueprint, jsonify, request
from services.model_service import add_model, get_model_by_id, get_all_models

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


@model_bp.route('/api/models', methods=['POST'])
def create_model():
    data = request.get_json()

    if 'samples' not in data or not isinstance(data['samples'], list):
        return jsonify({'error': 'Missing or invalid sample list'}), 400

    # Lấy danh sách các id từ đối tượng samples
    sample_ids = [sample['id'] for sample in data['samples']]

    # Gọi add_model với danh sách id
    add_model(sample_ids)

    return jsonify({'message': 'Model created successfully'})

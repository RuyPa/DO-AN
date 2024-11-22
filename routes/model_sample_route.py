from flask import Blueprint, jsonify, request, abort
from models.model_sample import ModelSample
from services.auth_service import role_required
from services.model_sample_service import (
    get_model_sample_by_id,
    add_model_sample,
    get_model_samples_by_model_id
)
from services.sample_service import get_sample_by_id

model_sample_bp = Blueprint('model_sample_bp', __name__)

# API lấy model samples theo model_id
@model_sample_bp.route('/api/model_samples/model/<int:model_id>', methods=['GET'])
@role_required('admin')
def get_model_samples_by_model_id_route(model_id):
    model_samples = get_model_samples_by_model_id(model_id)
    if not model_samples:
        abort(404, description="No model samples found for the given model ID")
    return jsonify([model_sample.to_dict() for model_sample in model_samples])

@model_sample_bp.route('/api/model_samples/<int:id>', methods=['GET'])
@role_required('admin')
def get_model_sample_route(id):
    model_sample = get_model_sample_by_id(id)
    if model_sample is None:
        abort(404, description="Model Sample not found")
    return jsonify(model_sample.to_dict())

@model_sample_bp.route('/api/model_samples', methods=['POST'])
@role_required('admin')
def create_model_sample_route():
    data = request.get_json()
    
    model_id = data.get('model_id')
    sample_id = data.get('sample_id')
    created_date = data.get('created_date')
    created_by = data.get('created_by')
    
    if not model_id or not sample_id or not created_date or not created_by:
        abort(400, description="All fields are required")
    
    sample = get_sample_by_id(sample_id)
    if not sample:
        abort(404, description="Sample not found")
    
    model_sample = ModelSample(
        id=None,
        model_id=model_id,
        sample=sample,
        created_date=created_date,
        created_by=created_by
    )
    
    add_model_sample(model_sample)
    
    return jsonify({'message': 'Model Sample created successfully'}), 201

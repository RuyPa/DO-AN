from flask import Blueprint, jsonify, request, abort
from models.sample import Sample
from services.sample_service import (
    get_all_samples,
    get_sample_by_id,
    add_sample,
    update_sample,
    delete_sample
)

sample_bp = Blueprint('sample_bp', __name__)

@sample_bp.route('/api/samples', methods=['GET'])
def get_samples():
    samples = get_all_samples()
    return jsonify([sample.to_dict() for sample in samples])

@sample_bp.route('/api/samples/<int:id>', methods=['GET'])
def get_sample(id):
    sample = get_sample_by_id(id)
    if sample is None:
        abort(404, description="Sample not found")
    return jsonify(sample.to_dict())

@sample_bp.route('/api/samples', methods=['POST'])
def create_sample():
    data = request.get_json()
    
    if not data:
        abort(400, description="Request body is missing or not valid JSON")
    
    code = data.get('code')
    path = data.get('path', '')  
    name = data.get('name', '') 
    
    if not code:
        abort(400, description="Code is required")
    
    sample = Sample(code=code, path=path, name=name)
    
    add_sample(sample)
    
    return jsonify({'message': 'Sample created successfully'}), 201

@sample_bp.route('/api/samples/<int:id>', methods=['PUT'])
def update_sample_route(id):
    data = request.json

    sample = get_sample_by_id(id)
    if sample is None:
        abort(404, description="Sample not found")

    code = data.get('code', sample.code)
    path = data.get('path', sample.path)
    name = data.get('name', sample.name)

    if code == sample.code and path == sample.path and name == sample.name:
        return jsonify({'message': 'No changes made'}), 200

    update_sample(id, code, path, name)
    
    return jsonify({'message': 'Sample updated successfully'})

@sample_bp.route('/api/samples/<int:id>', methods=['DELETE'])
def delete_sample_route(id):
    delete_sample(id)
    return jsonify({'message': 'Sample deleted successfully'})

from flask import Blueprint, jsonify, request, abort
from models.label import Label
from models.traffic_sign import TrafficSign
from services.label_service import (
    create_label,
    get_all_labels,
    get_label_by_id,
    update_label,
    delete_label
)

label_bp = Blueprint('label_bp', __name__)

@label_bp.route('/api/labels', methods=['GET'])
def get_labels():
    labels = get_all_labels()
    return jsonify([label.to_dict() for label in labels])

@label_bp.route('/api/labels/<int:id>', methods=['GET'])
def get_label(id):
    label = get_label_by_id(id)
    if label is None:
        abort(404, description="Label not found")
    return jsonify(label.to_dict())

@label_bp.route('/api/labels', methods=['POST'])
def create_label_route():
    data = request.get_json()

    if not data:
        abort(400, description="Request body is missing or not valid JSON")

    centerX = data.get('centerX')
    centerY = data.get('centerY')
    height = data.get('height')
    width = data.get('width')
    sample_id = data.get('sample_id')
    traffic_sign_id = data.get('traffic_sign_id')

    # Kiểm tra các trường bắt buộc
    if centerX is None or centerY is None or height is None or width is None or sample_id is None or traffic_sign_id is None:
        abort(400, description="All fields are required")

    label = Label(centerX=centerX, centerY=centerY, height=height, width=width, sample_id=sample_id, traffic_sign = TrafficSign.from_req(traffic_sign_id) )
    
    create_label(label)
    
    return jsonify({'message': 'Label created successfully'}), 201

@label_bp.route('/api/labels/<int:id>', methods=['PUT'])
def update_label_route(id):
    data = request.json
    label = get_label_by_id(id)
    if label is None:
        abort(404, description="Label not found")

    centerX = data.get('centerX', label.centerX)
    centerY = data.get('centerY', label.centerY)
    height = data.get('height', label.height)
    width = data.get('width', label.width)
    sample_id = data.get('tbl_sample_id', label.sample_id)
    traffic_sign_id = data.get('traffic_sign_id', label.traffic_sign_id)

    update_label(id, centerX, centerY, height, width, sample_id, traffic_sign_id)
    return jsonify({'message': 'Label updated successfully'})

@label_bp.route('/api/labels/<int:id>', methods=['DELETE'])
def delete_label_route(id):
    delete_label(id)
    return jsonify({'message': 'Label deleted successfully'})

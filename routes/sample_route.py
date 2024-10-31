from flask import Blueprint, jsonify, request, abort
from models.label import Label
from models.sample import Sample
from models.traffic_sign import TrafficSign
from services.label_service import create_label, delete_label, update_label, delete_labels_by_sample_id
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

# @sample_bp.route('/api/samples', methods=['POST'])
# def create_sample():
#     data = request.get_json()
    
#     if not data:
#         abort(400, description="Request body is missing or not valid JSON")
    
#     code = data.get('code')
#     path = data.get('path', '')  
#     name = data.get('name', '') 
    
#     if not code:
#         abort(400, description="Code is required")
    
#     sample = Sample(code=code, path=path, name=name)
    
#     add_sample(sample)
    
#     return jsonify({'message': 'Sample created successfully'}), 201
@sample_bp.route('/api/samples', methods=['POST'])
def create_sample():
    data = request.get_json()
    
    if not data:
        abort(400, description="Request body is missing or not valid JSON")
    
    code = data.get('code')
    path = data.get('path', '')  
    name = data.get('name', '') 
    labels_data = data.get('labels', [])  # Nhận danh sách labels từ body request
    
    if not code:
        abort(400, description="Code is required")
    
    # Tạo đối tượng Sample và thêm các labels nếu có
    sample = Sample(code=code, path=path, name=name)
    
    # Xử lý danh sách labels nếu có trong request
    for label_data in labels_data:
        # Tạo đối tượng Label từ dữ liệu của từng label trong danh sách
        label = Label(
            centerX=label_data.get('centerX'),
            centerY=label_data.get('centerY'),
            height=label_data.get('height'),
            width=label_data.get('width'),
            traffic_sign= TrafficSign.from_req(label_data.get('traffic_sign_id'))  # Ví dụ, các thuộc tính cần thiết khác
        )
        sample.labels.append(label)  # Thêm label vào danh sách labels của sample
    
    # Thêm sample và các labels vào database
    add_sample(sample)
    
    return jsonify({'message': 'Sample created successfully'}), 201

@sample_bp.route('/api/samples/<int:id>', methods=['PUT'])
def update_sample_route(id):
    data = request.json
    sample = get_sample_by_id(id)
    if sample is None:
        abort(404, description="Sample not found")

    # Cập nhật thông tin của Sample nếu có
    updated = False
    if 'code' in data:
        sample.code = data['code']
        updated = True
    if 'path' in data:
        sample.path = data['path']
        updated = True
    if 'name' in data:
        sample.name = data['name']
        updated = True

    # Lưu thay đổi vào cơ sở dữ liệu nếu có thay đổi
    if updated:
        update_sample(sample)  # Gọi hàm để cập nhật sample trong DB

    # Xử lý danh sách labels
    labels_data = data.get('labels', [])
    existing_labels = {label.id: label for label in sample.labels}

    for label_data in labels_data:
        label_id = label_data.get('id')

        # Kiểm tra nếu label cần xóa
        if label_data.get('isDeleted'):  # Nếu có trường isDeleted là true
            if label_id in existing_labels:
                # Xóa label khỏi sample
                sample.labels = [label for label in sample.labels if label.id != label_id]
                delete_label(label_id)  # Gọi hàm để xóa label trong DB
            continue  # Bỏ qua vòng lặp này, vì label đã được xử lý

        if label_id in existing_labels:
            label = existing_labels[label_id]

            # Cập nhật các thuộc tính của label nếu có
            if 'centerX' in label_data:
                label.centerX = label_data['centerX']
            if 'centerY' in label_data:
                label.centerY = label_data['centerY']
            if 'height' in label_data:
                label.height = label_data['height']
            if 'width' in label_data:
                label.width = label_data['width']
            if 'traffic_sign_id' in label_data:
                label.traffic_sign =  TrafficSign.from_req(label_data['traffic_sign_id'])

            # Lưu thay đổi vào cơ sở dữ liệu
            update_label(label)  # Gọi hàm để cập nhật label trong DB
        else:
            # Thêm label mới nếu ID không tồn tại
            new_label = Label(
                centerX=label_data.get('centerX'),
                centerY=label_data.get('centerY'),
                height=label_data.get('height'),
                width=label_data.get('width'),
                traffic_sign=TrafficSign.from_req(label_data.get('traffic_sign_id')),
                sample_id=id
            )
            create_label(label= new_label)

    # Lưu tất cả các thay đổi vào cơ sở dữ liệu
    update_sample(sample)

    return jsonify({'message': 'Sample updated successfully'}), 200




@sample_bp.route('/api/samples/<int:id>', methods=['DELETE'])
def delete_sample_route(id):
    # Xóa tất cả các label liên quan đến sample
    delete_labels_by_sample_id(id)
    
    # Xóa sample
    delete_sample(id)
    
    return jsonify({'message': 'Sample and its labels deleted successfully'})


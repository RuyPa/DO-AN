import os
import uuid
from flask import Blueprint, jsonify, request, abort
from models.label import Label
from models.sample import Sample
from models.traffic_sign import TrafficSign
from services.auth_service import role_required
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
@role_required('admin', 'user')
def get_samples():
    samples = get_all_samples()
    return jsonify([sample.to_dict() for sample in samples])

@sample_bp.route('/api/samples/<int:id>', methods=['GET'])
@role_required('admin', 'user')
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
@role_required('admin', 'user')
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
@role_required('admin', 'user')
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
@role_required('admin')
def delete_sample_route(id):
    # Xóa tất cả các label liên quan đến sample
    delete_labels_by_sample_id(id)
    
    # Xóa sample
    delete_sample(id)
    
    return jsonify({'message': 'Sample and its labels deleted successfully'})



from cloudinary.uploader import upload
import cloudinary
cloudinary.config( 
        cloud_name = "dkf74ju3o", 
        api_key = "639453249624293", 
        api_secret = "2GY34a7PT11RkkaTwEsKP9eYkwI",
        secure = True
    )

# List of images to exclude from upload
excluded_images = ['3.png', '5.png', '6.png', '16.png', '17.png', '334.png']

@sample_bp.route('/api/samples/temp', methods=['GET'])
def create_sample_temp():
    # Lấy đường dẫn đến thư mục ảnh và thư mục nhãn
    image_folder = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\vn1\\valid\\images"
    label_folder = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\vn1\\valid\\labels"
    
    if not image_folder or not label_folder:
        abort(400, description="Both image folder and label folder are required")
    
    # Kiểm tra nếu thư mục ảnh và nhãn tồn tại
    if not os.path.exists(image_folder) or not os.path.exists(label_folder):
        abort(400, description="Image or label folder does not exist")

    try:
        # Lấy danh sách các tệp ảnh trong thư mục ảnh
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'png', 'jpeg'))]
        
        # Lặp qua từng ảnh trong thư mục ảnh
        for image_file in image_files:
            # Skip the excluded images
            if image_file in excluded_images:
                continue  # Bỏ qua ảnh nếu tên của ảnh có trong danh sách ngoại trừ
            
            image_path = os.path.join(image_folder, image_file)
            label_file = os.path.splitext(image_file)[0] + '.txt'  # Giả sử tệp nhãn có cùng tên với ảnh nhưng định dạng .txt
            label_path = os.path.join(label_folder, label_file)

            # Kiểm tra nếu tệp nhãn có tồn tại
            if not os.path.exists(label_path):
                continue  # Bỏ qua nếu không có tệp nhãn tương ứng
            
            # Upload ảnh lên Cloudinary
            upload_result = cloudinary.uploader.upload(image_path)
            image_url = upload_result.get('secure_url')  # Lấy URL an toàn của ảnh đã upload

            # Đọc tệp nhãn
            with open(label_path, 'r') as label_file:
                labels_data = label_file.readlines()  # Đọc từng dòng trong tệp nhãn

            # Tạo đối tượng Sample
            sample = Sample(code=str(uuid.uuid4()), path=image_url, name=image_file)

            # Xử lý các nhãn
            for label_data in labels_data:
                # Mỗi dòng trong tệp nhãn có thể có thông tin nhãn dạng: traffic_sign_id centerX centerY height width
                label_info = label_data.strip().split()  # Giả sử các trường cách nhau bằng khoảng trắng

                if len(label_info) < 5:
                    continue  # Bỏ qua nếu dữ liệu không đầy đủ

                # Lấy thông tin nhãn từ tệp
                traffic_sign_id = int(label_info[0])
                centerX, centerY, height, width = map(float, label_info[1:])

                # Tạo đối tượng TrafficSign từ traffic_sign_id
                traffic_sign = TrafficSign.from_req(traffic_sign_id)  # Tạo đối tượng TrafficSign từ ID
                
                # Tạo đối tượng Label và thêm vào Sample
                label = Label(centerX=centerX, centerY=centerY, height=height, width=width, traffic_sign=traffic_sign)
                sample.labels.append(label)
            
            # Lưu sample vào cơ sở dữ liệu
            add_sample(sample)

        return jsonify({'message': 'Samples created successfully'}), 201

    except Exception as e:
        abort(500, description=f"An error occurred: {str(e)}")

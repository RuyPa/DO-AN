# class Label:
#     def __init__(self, id=None, centerX=0.0, centerY=0.0, height=0.0, width=0.0, sample_id=None, traffic_sign_id=None):
#         self.id = id
#         self.centerX = centerX
#         self.centerY = centerY
#         self.height = height
#         self.width = width
#         self.sample_id = sample_id
#         self.traffic_sign_id = traffic_sign_id

#     @staticmethod
#     def from_row(row):
#         return Label(
#             id=row['id'],
#             centerX=row['centerX'],
#             centerY=row['centerY'],
#             height=row['height'],
#             width=row['width'],
#             sample_id=row['sample_id'],
#             traffic_sign_id=row['traffic_sign_id']
#         )
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'centerX': self.centerX,
#             'centerY': self.centerY,
#             'height': self.height,
#             'width': self.width,
#             'sample_id': self.sample_id,
#             'traffic_sign_id': self.traffic_sign_id
#         }
from models.traffic_sign import TrafficSign

class Label:
    def __init__(self, id=None, centerX=0, centerY=0, height=0, width=0, sample_id=None, traffic_sign=None):
        self.id = id
        self.centerX = centerX
        self.centerY = centerY
        self.height = height
        self.width = width
        self.sample_id = sample_id
        self.traffic_sign = traffic_sign  # Đối tượng TrafficSign tương ứng với label

    @staticmethod
    def from_row(row, traffic_sign=None):
        """Tạo đối tượng Label từ một bản ghi cơ sở dữ liệu, kèm theo thông tin về TrafficSign."""
        return Label(
            id=row['id'],
            centerX=row['centerX'],
            centerY=row['centerY'],
            height=row['height'],
            width=row['width'],
            sample_id=row['sample_id'],
            traffic_sign=traffic_sign  # Nhận đối tượng TrafficSign
        )
    
    def to_dict(self):
        """Chuyển đổi Label thành từ điển, bao gồm thông tin của TrafficSign."""
        return {
            'id': self.id,
            'centerX': self.centerX,
            'centerY': self.centerY,
            'height': self.height,
            'width': self.width,
            'sample_id': self.sample_id,
            'traffic_sign': self.traffic_sign.to_dict() if self.traffic_sign else None  # Chuyển đối tượng TrafficSign thành từ điển
        }

class Label:
    def __init__(self, id=None, centerX=0.0, centerY=0.0, height=0.0, width=0.0, sample_id=None, traffic_sign_id=None):
        self.id = id
        self.centerX = centerX
        self.centerY = centerY
        self.height = height
        self.width = width
        self.sample_id = sample_id
        self.traffic_sign_id = traffic_sign_id

    @staticmethod
    def from_row(row):
        return Label(
            id=row['id'],
            centerX=row['centerX'],
            centerY=row['centerY'],
            height=row['height'],
            width=row['width'],
            sample_id=row['sample_id'],
            traffic_sign_id=row['traffic_sign_id']
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'centerX': self.centerX,
            'centerY': self.centerY,
            'height': self.height,
            'width': self.width,
            'sample_id': self.sample_id,
            'traffic_sign_id': self.traffic_sign_id
        }

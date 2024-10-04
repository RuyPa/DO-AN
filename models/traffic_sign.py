class TrafficSign:
    def __init__(self, id=None, name='', code='', description='', path=''):
        self.id = id
        self.name = name
        self.code = code
        self.description = description
        self.path = path

    @staticmethod
    def from_row(row):
        """Tạo đối tượng TrafficSign từ một bản ghi cơ sở dữ liệu."""
        return TrafficSign(
            id=row['id'],
            name=row['name'],
            code=row['code'],
            description=row['description'],
            path=row['path']
        )
    
    def to_dict(self):
        """Chuyển đối tượng TrafficSign thành từ điển."""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'path': self.path
        }

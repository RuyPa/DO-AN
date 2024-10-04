class Sample:
    def __init__(self, id=None, code='', path='', name=''):
        self.id = id
        self.code = code
        self.path = path
        self.name = name

    @staticmethod
    def from_row(row):
        """Tạo đối tượng Sample từ một bản ghi cơ sở dữ liệu."""
        return Sample(
            id=row['id'],
            code=row['code'],
            path=row['path'],
            name=row['name']
        )

    def to_dict(self):
        """Chuyển đối tượng Sample thành từ điển."""
        return {
            'id': self.id,
            'code': self.code,
            'path': self.path,
            'name': self.name
        }

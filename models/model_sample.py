class ModelSample:
    def __init__(self, id, model_id, sample, created_date, created_by):
        self.id = id
        self.model_id = model_id
        self.sample = sample  # Đây là đối tượng Sample
        self.created_date = created_date
        self.created_by = created_by

    @classmethod
    def from_row(cls, row, sample):
        return cls(
            id=row['id'],
            model_id=row['model_id'],
            sample=sample,
            created_date=row['created_date'],
            created_by=row['created_by']
        )
    
    @classmethod
    def from_prj(cls, row, sample):
        return cls(
            id=row['model_sample_id'],
            model_id=row['model_id'],
            sample=sample,
            created_date=row['created_date'],
            created_by=row['created_by']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'model_id': self.model_id,
            'sample': self.sample.to_dict(),  # Trả về đối tượng Sample dưới dạng dictionary
            'created_date': self.created_date,
            'created_by': self.created_by
        }

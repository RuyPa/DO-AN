class Model:
    def __init__(self, id, name, path, date, acc, pre, f1, recall, status, model_samples=[]):
        self.id = id
        self.name = name
        self.path = path
        self.date = date
        self.acc = acc
        self.pre = pre
        self.f1 = f1
        self.recall = recall
        self.status = status
        self.model_samples = model_samples

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            name=row['name'],
            path=row['path'],
            date=row['date'],
            acc=row['acc'],
            pre=row['pre'],
            f1=row['f1'],
            recall=row['recall'],
            status=row['status']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'date': self.date,
            'acc': self.acc,
            'pre': self.pre,
            'f1': self.f1,
            'recall': self.recall,
            'status': self.status,
            'model_samples': [model_sample.to_dict() for model_sample in self.model_samples]
        }

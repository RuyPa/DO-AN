class SearchParams:
    def __init__(self, keyword=None, page=1, page_size=10):
        self.keyword = keyword
        self.page = max(page, 1)  # Ensure the page is at least 1
        self.page_size = min(max(page_size, 1), 100)  # Ensure page size is between 1 and 100

    @property
    def offset(self):
        return (self.page - 1) * self.page_size

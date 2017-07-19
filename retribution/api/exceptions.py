class APIError(Exception):

    def __init__(self, status_code=None, detail=''):
        self.status_code = status_code
        self.detail = detail

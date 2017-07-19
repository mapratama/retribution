class LockAquisitionError(Exception):
    pass


class RetributionAPIError(Exception):

    def __init__(self, error_messages):
        self.error_messages = error_messages

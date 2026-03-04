class NotFoundException(Exception):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message

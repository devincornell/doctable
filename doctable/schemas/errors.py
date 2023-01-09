

class SlotsRequiredError(BaseException):
    pass

# DEPRICATED: KEPT FOR BACKWARDS-COMPATIBILITY
class DataNotAvailableError(BaseException):
    pass

class RowDataNotAvailableError(DataNotAvailableError):
    pass

class TypeNotRecognizedError(BaseException):
    pass



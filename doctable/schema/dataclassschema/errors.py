
#class RowDataConversionFailedError(BaseException):
#    pass
# DEPRICATED: KEPT FOR BACKWARDS-COMPATIBILITY
class DataNotAvailableError(BaseException):
    pass


class RowDataNotAvailableError(DataNotAvailableError):
    pass

class SlotsRequiredError(BaseException):
    pass

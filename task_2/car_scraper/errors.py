class SearchCarsApiError(ValueError):
    pass

class TooHighOffsetError(SearchCarsApiError):
    pass

class SearchUntilDatetimeEnd(Exception):
    pass
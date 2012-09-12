class LxxlException(Exception):
    pass


class HTTPRequestException(LxxlException):

    def __init__(self, resp):
        self.code = resp.status_code
        self.response = resp

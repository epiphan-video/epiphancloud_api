class EpiphanCloudException(Exception):
    """Base class for Epiphan Cloud exceptions"""


class EpiphanCloudHTTPError(EpiphanCloudException):
    """Generic HTTP error (400-s errors)"""

    def __init__(self, response):
        self.message = "HTTP error {}: {}".format(response.status_code, response.text)
        self.status_code = response.status_code


class EpiphanCloudUnauthorized(EpiphanCloudException):
    """Invalid auth token"""

    def __init__(self):
        self.message = "Unauthorized (the auth token is invalid or was not specified)"


class EpiphanCloudIsUnavailable(EpiphanCloudHTTPError):
    """Epiphan Cloud returns 500-s"""

    def __init__(self, response):
        super.__init__(response)
        self.message = "Epiphan Cloud " + self.message

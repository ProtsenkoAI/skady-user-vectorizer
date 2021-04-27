from ..executing import ParseRes


class ExternalErrorsHandler:
    """The class to process errors sent by service (API, website) we work with"""
    # TODO: separate each method to class with method handle()
    def auth_error(self, error: Exception, auth_data: dict):
        ...

    def api_response_error(self, parsed_results: ParseRes):
        ...

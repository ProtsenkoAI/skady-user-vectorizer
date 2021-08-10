from abc import ABC, abstractmethod


from ..executing import ParseRes


class ExternalErrorsHandler(ABC):
    """The class to process errors sent by service (API, website) we work with"""

    @abstractmethod
    def response_error(self, parsed_results: ParseRes):
        ...

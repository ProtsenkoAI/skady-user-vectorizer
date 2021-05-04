from ..executing import ParseRes
from ..listen_notify.request_success import RequestSuccessNotifier
from .parsed_processor_impl import ParsedProcessorImpl


class SuccessNotifierProcessor(ParsedProcessorImpl, RequestSuccessNotifier):
    def __init__(self, *args, **kwargs):
        ParsedProcessorImpl.__init__(self, *args, **kwargs)
        RequestSuccessNotifier.__init__(self)

    """Notifies if request succeeded"""
    def process_success(self, res: ParseRes):
        self.notify_request_success(res.user, res.request_type)
        super().process_success(res)

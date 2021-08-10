from suvec.common.executing.error_codes import PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED, ACCESS_ERROR, ACCESS_DENIED
from suvec.common.executing import ParseRes
from suvec.common.events_tracking import TerminalEventsTracker
from suvec.common.external_errors_handling import ExternalErrorsHandler
from suvec.common.listen_notify import UserUnrelatedErrorNotifier


class VkApiErrorsHandler(ExternalErrorsHandler, UserUnrelatedErrorNotifier):
    """The class to process errors sent by service (API, website) we work with"""
    # TODO: refactor logging/working with tracker

    # TODO: add method for errors not specific to any instrument or operation (JSONDecodeError, RemoteDisconnected, etc)

    # TODO: issue with listener-notifier pattern: if we'll make request not from executor (for example, creds tester),
    #   and then process session_error, executor will get notification, despite it has no connection with the request

    # TODO: if 600 responses have access error, the notify_access_error() will be called 600 times, which
    #  is not a good thing. Can change interfaces to process by batches

    def __init__(self, events_tracker: TerminalEventsTracker, process_captcha=False):
        UserUnrelatedErrorNotifier.__init__(self)
        self.process_captcha = process_captcha

        self.tracker = events_tracker

    def response_error(self, parsed_results: ParseRes):
        if int(parsed_results.error.code) == ACCESS_ERROR:
            self.notify_user_unrelated_error(parsed_results.request)

        elif parsed_results.error.code in [PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED, ACCESS_DENIED]:
            self.tracker.skip_user(user=parsed_results.request.user, msg=f"Bad user (private, blocked, etc)")
        else:
            msg = (f"Unknown error occurred: {parsed_results.error.code} "
                   f"User: {parsed_results.request.user}")
            self.tracker.error_occurred(msg)
            raise ValueError(msg)

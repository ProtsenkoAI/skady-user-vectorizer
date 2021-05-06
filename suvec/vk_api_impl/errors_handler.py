from vk_api import exceptions
from requests.exceptions import ProxyError

from suvec.common.executing.error_codes import PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED, ACCESS_ERROR
from suvec.common.executing import ParseRes, ErrorObj
from suvec.common.listen_notify import BadPasswordNotifier
from suvec.common.events_tracking import TerminalEventsTracker
from suvec.common.external_errors_handling import ExternalErrorsHandler
from suvec.common.listen_notify import AccessErrorNotifier


class VkApiErrorsHandler(ExternalErrorsHandler, BadPasswordNotifier, AccessErrorNotifier):
    """The class to process errors sent by service (API, website) we work with"""

    # TODO: instead of many if-else, maybe use small objects processing one type of error
    def __init__(self, events_tracker: TerminalEventsTracker):
        BadPasswordNotifier.__init__(self)
        AccessErrorNotifier.__init__(self)

        self.tracker = events_tracker

    def auth_error(self, error: exceptions.VkApiError, auth_data: dict):
        session = auth_data["session"]
        del auth_data["session"]

        error_code = getattr(error, "code", None)
        wrapped_error = ErrorObj(error_code, error)
        if isinstance(error, exceptions.Captcha):
            print("captcha needed")
            print(f"Captcha url: {error.get_url()}")
            captcha_answer = input("Please enter captcha text: \n")
            try:
                error.try_again(captcha_answer)
            except exceptions.VkApiError as exception:
                error_obj = ErrorObj(code=None, error=exception)
                self.tracker.error_occurred(error_obj, msg="can't handle auth error")
            if session is None:
                raise ValueError("Captcha error occurred, but you have not passed session object, thus can't auth")
            else:
                session.auth()
        elif isinstance(error, exceptions.BadPassword):
            # Funny fact: vk_api can return Bad password even if it's not the problem.
            # One time it returned bad password when we didn't pass User agent in requests session
            # SO if there'll be bugs, consider find REAL root of the problem
            self.tracker.message("Bad password error occurred")
            self.notify_bad_password()

        elif isinstance(error, ProxyError):
            error_obj = ErrorObj(code=None, error=error)
            self.tracker.error_occurred(error_obj, "The proxy doesn't work. Try to send some request from it."
                                               f"Auth data: {auth_data}")
            # TODO: notify bad proxy, otherwise parsing will fail

        else:
            self.tracker.error_occurred(error=wrapped_error, msg=f"Unknown auth error")
            raise ValueError("Unknown auth error", error)

        error_msg_to_log = f"Auth error: auth_data = {auth_data}"
        self.tracker.message(msg=error_msg_to_log)

    def api_response_error(self, parsed_results: ParseRes):
        if int(parsed_results.error.code) == ACCESS_ERROR:
            self.notify_access_error_listeners(user=parsed_results.user,
                                               type_of_request=parsed_results.request_type)

        elif parsed_results.error.code in [PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED]:
            self.tracker.skip_user(user=parsed_results.user, msg=f"Profile is private")
        else:
            msg = (f"Unknown error occurred: {parsed_results.error.code} "
                   f"User: {parsed_results.user}")
            self.tracker.error_occurred(error=parsed_results.error, msg=msg)
            raise ValueError(msg)

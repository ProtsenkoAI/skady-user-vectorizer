import logging

from vk_api import exceptions
from requests.exceptions import ProxyError

from suvec.common.executing.error_codes import PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED, ACCESS_ERROR, ACCESS_DENIED
from suvec.common.executing import ParseRes, ErrorObj
from suvec.common.events_tracking import TerminalEventsTracker
from suvec.common.external_errors_handling import ExternalErrorsHandler
from suvec.common.listen_notify import AccessErrorNotifier, BadPasswordNotifier


class VkApiErrorsHandler(ExternalErrorsHandler, BadPasswordNotifier, AccessErrorNotifier):
    """The class to process errors sent by service (API, website) we work with"""
    # TODO: refactor logging/working with tracker

    # TODO: add method for errors not specific to any instrument or operation (JSONDecodeError, RemoteDisconnected, etc)

    # TODO: issue with listener-notifier pattern: if we'll make request not from executor (for example, creds tester),
    #   and then process access_error, executor will get notification, despite it has no connection with the request

    # TODO: if 600 responses have access error, the notify_access_error() will be called 600 times, which
    #  is not a good thing. Can change interfaces to process by batches
    def __init__(self, events_tracker: TerminalEventsTracker, process_captcha=False):
        BadPasswordNotifier.__init__(self)
        AccessErrorNotifier.__init__(self)
        self.process_captcha = process_captcha

        self.tracker = events_tracker

    def auth_error(self, error: exceptions.VkApiError, auth_data: dict, session_id: int):
        session = auth_data["session"]
        del auth_data["session"]

        error_code = getattr(error, "code", None)
        wrapped_error = ErrorObj(error_code, error)
        if isinstance(error, exceptions.Captcha) and self.process_captcha:
            print("captcha needed")
            print(f"Captcha url: {error.get_url()}")
            captcha_answer = input("Please enter captcha text: \n")
            try:
                error.try_again(captcha_answer)
            except exceptions.VkApiError as exception:
                self.tracker.error_occurred("can't handle auth error")
            if session is None:
                raise ValueError("Captcha error occurred, but you have not passed session object, thus can't auth")
            else:
                session.auth()
        elif isinstance(error, exceptions.BadPassword):
            # Funny fact: vk_api can return Bad password even if it's not the problem.
            # One time it returned bad password when we didn't pass User agent in requests session
            # SO if there'll be bugs, consider find REAL root of the problem
            self.notify_bad_password(session_id)

        elif isinstance(error, ProxyError):
            self.tracker.error_occurred("The proxy doesn't work. Try to send some request from it. "
                                        f"Auth data: {auth_data}")

        else:
            self.tracker.error_occurred(f"Unknown auth error, error: {wrapped_error.code, wrapped_error.error}")
            raise ValueError("Unknown auth error", error)

        error_msg_to_log = f"Auth error: auth_data = {auth_data}"
        logging.error(error_msg_to_log)

    def response_error(self, parsed_results: ParseRes):
        if int(parsed_results.error.code) == ACCESS_ERROR:
            self.notify_access_error_listeners(parsed_results.request)

        elif parsed_results.error.code in [PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED, ACCESS_DENIED]:
            self.tracker.skip_user(user=parsed_results.request.user, msg=f"Bad user (private, blocked, etc)")
        else:
            msg = (f"Unknown error occurred: {parsed_results.error.code} "
                   f"User: {parsed_results.request.user}")
            self.tracker.error_occurred(msg)
            raise ValueError(msg)

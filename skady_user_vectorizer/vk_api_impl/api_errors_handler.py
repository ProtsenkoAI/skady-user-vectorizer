from vk_api import exceptions
import vk_api
from typing import Optional

from .error_codes import PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED
from .parse_res import ParseRes, VkApiErrorObj
from .bad_password import BadPasswordNotifier
from .events_tracker import EventsTracker


class VkApiErrorsHandler(BadPasswordNotifier):
    def __init__(self, events_tracker: EventsTracker):
        self.tracker = events_tracker
        super().__init__()

    def auth_error(self, error: exceptions.VkApiError, auth_data: dict, session: Optional[vk_api.VkApi] = None):
        error_code = getattr(error, "code", None)
        wrapped_error = VkApiErrorObj(error_code, error)
        if isinstance(error, exceptions.Captcha):
            print("captcha needed")
            print(f"Captcha url: {error.get_url()}")
            captcha_answer = input("Please enter captcha text: \n")
            error.try_again(captcha_answer)
            if session is None:
                raise ValueError("Captcha error occurred, but you have not passed session object, thus can't auth")
            else:
                session.auth()

        elif isinstance(error, exceptions.BadPassword):
            # Funny fact: vk_api can return Bad password even if it's not the problem.
            # One time it returned bad password when we didn't pass User agent in requests session
            # SO if there'll be bugs, consider find REAL root of the problem
            self.tracker.message("Bad password error occured")
            self.notify_bad_password()

        else:
            self.tracker.error_occurred(error=wrapped_error, msg=f"Unknown auth error")
            raise ValueError("Unknown auth error", error)

        error_msg_to_log = f"Auth error: auth_data = {auth_data}"
        self.tracker.message(msg=error_msg_to_log)

    def api_response_error(self, parsed_results: ParseRes):
        if parsed_results.error.code in [PROFILE_IS_PRIVATE, ACCOUNT_IS_BLOCKED]:
            self.tracker.skip_user(user=parsed_results.user, msg=f"Profile is private")
        else:
            msg = (f"Unknown error occurred: {parsed_results.error.code} "
                   f"User: {parsed_results.user}")
            self.tracker.error_occurred(error=parsed_results.error, msg=msg)
            raise ValueError(msg)

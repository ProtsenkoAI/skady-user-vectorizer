from vk_api import exceptions
import vk_api
from typing import Optional

from .parse_res import ParseRes
from .bad_password import BadPasswordNotifier


class VkApiErrorsHandler(BadPasswordNotifier):
    def __init__(self, events_tracker):
        self.tracker = events_tracker
        super().__init__()

    def auth_error(self, error: exceptions.VkApiError, auth_data: dict, session: Optional[vk_api.VkApi] = None):
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
            self.notify_bad_password()

        else:
            self.tracker.error_occured(error=error, msg=f"Unknown auth error")
            raise ValueError("Unknown auth error", error)

        error_msg_to_log = f"Auth error: auth_data = {auth_data}"
        self.tracker.error_occured(error=error, msg=error_msg_to_log)

    def api_response_error(self, parsed_results: ParseRes):
        if parsed_results.error.code == 30:
            self.tracker.skip_user(user=parsed_results.user, msg=f"Profile is private")
        else:
            msg = (f"Unknown error occurred: {parsed_results.error.code}"
                   f"User: {parsed_results.user}")
            self.tracker.error_occured(error=parsed_results.error, msg=msg)
            raise ValueError(msg)

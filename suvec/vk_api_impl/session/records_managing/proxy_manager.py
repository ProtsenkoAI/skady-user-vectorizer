from .auth_record_manager import AuthRecordManager
from .terminal_out_of_records import TerminalOutOfProxy


class ProxyManager(AuthRecordManager):
    def __init__(self, *args, use_out_of_proxy_manager: bool = False, **kwargs):
        if use_out_of_proxy_manager:
            out_of_proxy_manager = TerminalOutOfProxy()
        else:
            out_of_proxy_manager = None
        super().__init__(*args, out_of_records_handler=out_of_proxy_manager, **kwargs)

    def test_with_record_tester(self, record_tester, proxy):
        return record_tester.test_proxy(proxy)

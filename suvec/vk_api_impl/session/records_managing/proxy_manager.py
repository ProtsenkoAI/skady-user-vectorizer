from .records import ProxyRecord
from .auth_record_manager import AuthRecordManager
from .terminal_out_of_records import TerminalOutOfProxy


class ProxyManager(AuthRecordManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, out_of_records_handler=TerminalOutOfProxy(), **kwargs)

    def test_with_record_tester(self, record_tester, proxy):
        return record_tester.test_proxy(proxy)

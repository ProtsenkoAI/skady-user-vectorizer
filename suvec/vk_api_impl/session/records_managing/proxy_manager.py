from .records import ProxyRecord
from .auth_record_manager import AuthRecordManager


class ProxyManager(AuthRecordManager):
    def prepare_record(self, record: ProxyRecord):
        return record.proxy

    def test_with_record_tester(self, record_tester, proxy):
        return record_tester.test_proxy(proxy)

from .auth_record_manager import AuthRecordManager


class ProxyManager(AuthRecordManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

from .auth_record_manager import AuthRecordManager
from .records_storing.creds_storage import CredsStorage
from .terminal_out_of_records import TerminalOutOfCreds


class CredsManager(AuthRecordManager):
    def __init__(self, storage: CredsStorage, *args, use_out_of_creds_manager: bool = False, **kwargs):
        if use_out_of_creds_manager:
            out_of_creds_manager = TerminalOutOfCreds
        else:
            out_of_creds_manager = None
        super().__init__(storage, *args, out_of_records_handler=out_of_creds_manager, **kwargs)

    def mark_bad_password(self, creds_id):
        self.storage: CredsStorage
        self.storage.set_bad_password(creds_id)

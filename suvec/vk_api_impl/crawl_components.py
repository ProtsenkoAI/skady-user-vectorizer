from suvec.common.requesting import EconomicRequester
from suvec.common.postproc.data_managers.data_long_term_saver import DataLongTermSaver

from suvec.vk_api_impl.session.session_units import AioVkSessionUnit
from suvec.common.requesting.requested_users_storage import RequestedUsersFileStorage
from suvec.common.requesting.users_filter import DuplicateUsersFilter
from .executing.async_pool_executor import AsyncVkApiPoolExecutor
from .executing.mutli_session_async_pool_executor import MultiSessionAsyncVkApiPoolExecutor
from .executing.responses_factory import AioVkResponsesFactory
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from .requesting import VkApiRequestsCreator
from .errors_handler import VkApiErrorsHandler
from .session.records_managing.proxy_manager import ProxyManager
from .session.records_managing.creds_manager import CredsManager
from .session import SessionManagerImpl


from suvec.common.postproc.data_managers.ram_data_manager import RAMDataManager
from suvec.common.postproc import ParsedProcessorWithHooks
from suvec.common.postproc.processor_hooks import HookSuccessParseNotifier


class CrawlComps:
    def __init__(self,
                 proxy_storage: ProxyStorage,
                 creds_storage: CredsStorage,
                 long_term_save_pth: str,
                 data_backup_path: str,
                 tracker=None,
                 requester_max_requests_per_loop=10000,
                 access_resource_reload_hours=24,
                 nb_sessions=1,
                 dmp_long_term_steps=2000):

        self.tracker = tracker

        requests_creator = VkApiRequestsCreator()

        friends_req_storage = RequestedUsersFileStorage("./resources/checkpoints/dumped_friends_requests.txt")
        groups_req_storage = RequestedUsersFileStorage("./resources/checkpoints/dumped_groups_requests.txt")
        users_filter = DuplicateUsersFilter()
        self.requester = EconomicRequester(
            requests_creator,
            friends_req_storage=friends_req_storage,
            groups_req_storage=groups_req_storage,
            users_filter=users_filter,
            max_requests_per_call=requester_max_requests_per_loop
        )

        self.errors_handler = VkApiErrorsHandler(tracker)

        proxy_manager = ProxyManager(proxy_storage, tracker,
                                     hours_for_resource_reload=access_resource_reload_hours)
        creds_manager = CredsManager(creds_storage, tracker,
                                     hours_for_resource_reload=access_resource_reload_hours)

        self.session_manager = SessionManagerImpl(proxy_manager, creds_manager)

        responses_factory = AioVkResponsesFactory()
        if nb_sessions == 1:
            session_unit = AioVkSessionUnit(self.session_manager)
            self.executor = AsyncVkApiPoolExecutor(responses_factory, session_unit)
        else:
            session_units = [AioVkSessionUnit(self.session_manager) for _ in range(nb_sessions)]
            self.executor = MultiSessionAsyncVkApiPoolExecutor(responses_factory, session_units)

        long_term_saver = DataLongTermSaver(long_term_save_pth, data_backup_path)
        self.data_manager = RAMDataManager(long_term_saver, dmp_long_term_every=dmp_long_term_steps)

        self.parsed_processor = ParsedProcessorWithHooks(self.data_manager, tracker,
                                                         errors_handler=self.errors_handler)

        self.success_request_notifier = HookSuccessParseNotifier()

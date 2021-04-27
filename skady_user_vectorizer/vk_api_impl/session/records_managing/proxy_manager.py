from .auth_record_manager import AuthRecordManager


class ProxyManager(AuthRecordManager):
    def get(self):
        """Process contained resource as subclass wants and return it to user class (probably session manager)"""
        return self.resource.proxy

    def send_tracker_reset_message(self, resources_total_cnt: int, usable_resources_left_cnt: int):
        self.tracker.proxy_report(resources_total_cnt, usable_resources_left_cnt, changed=True)

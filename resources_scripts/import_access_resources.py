"""Takes .txt file with list of proxies from webshare.com and adds proxies to parser
"""
from pathlib import Path
import json

from suvec.vk_api_impl.session.records_managing.resources_import import WebshareFileProxyImporter, VkFileCredsImporter
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from suvec.vk_api_impl.session.records_managing.records_storing.serializers import ProxyRecordsSerializer, \
    CredsRecordsSerializer


def import_webshare_proxy(webshare_txt_pth: str, proxy_storage: ProxyStorage):
    proxy_importer = WebshareFileProxyImporter(
        path_to_resources=webshare_txt_pth,
        min_obj_id=proxy_storage.get_next_record_id()
    )
    proxy_importer.import_records(proxy_storage)


def import_vk_accounts_txt(accounts_txt_pth: str, creds_storage: CredsStorage):
    creds_importer = VkFileCredsImporter(
        path_to_resources=accounts_txt_pth,
        min_obj_id=creds_storage.get_next_record_id()
    )
    creds_importer.import_records(creds_storage)


if __name__ == "__main__":
    settings_path = Path("../settings.json")
    res_path = settings_path.parent / json.load(settings_path.open())["resources"]["res_path"]

    proxy_file_pth = res_path / "other" / "webshare_proxy.txt"
    accounts_file_pth = res_path / "other" / "vk_accounts.txt"

    proxies_save_pth = res_path / "access" / "proxies.json"
    creds_save_pth = res_path / "access" / "creds.json"

    proxy_storage = ProxyStorage(proxies_save_pth, ProxyRecordsSerializer())
    creds_storage = CredsStorage(creds_save_pth, CredsRecordsSerializer())

    import_webshare_proxy(proxy_file_pth, proxy_storage)
    import_vk_accounts_txt(accounts_file_pth, creds_storage)

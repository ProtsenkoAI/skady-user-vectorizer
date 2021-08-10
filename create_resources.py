"""Creates start resources/ directory state with needed structure. Resources/ is needed to store vk accounts, proxy ips,
checkpoints of engine etc."""
import shutil
import json
import utils


def _create_resources_dir(settings_path="./settings.json", force_create: bool = False):
    """
    :param force_create: deletes existing directory and creates new if True
    """

    res_settings = utils.get_res_settings(settings_path)
    res_dir = utils.get_resources_path(settings_path)

    if force_create:
        shutil.rmtree(str(res_dir), ignore_errors=True)
    if res_dir.exists():
        raise RuntimeError("resources dir already exists")

    checkpoints_dir = res_dir / "checkpoints"
    access_dir = res_dir / "access"
    backups_dir = res_dir / "backups"
    test_files_dir = res_dir / "testing"

    res_dir.mkdir()
    checkpoints_dir.mkdir()
    access_dir.mkdir()
    backups_dir.mkdir()
    test_files_dir.mkdir()

    result_file = res_dir / res_settings["result_file"]
    result_file.touch()

    creds_pth = access_dir / res_settings["access"]["creds_file"]
    proxy_pth = access_dir / res_settings["access"]["proxy_file"]

    start_file_value = []
    for pth in [creds_pth, proxy_pth]:
        json.dump(start_file_value, pth.open(mode="w"))


if __name__ == "__main__":
    _create_resources_dir()

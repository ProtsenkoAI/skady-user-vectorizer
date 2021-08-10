import json

import utils


def check_types_and_unique_users(pth):
    met_users = set()
    empty_friends_or_groups_cnt = 0
    cnt_user_id_as_str = 0
    with open(pth) as f:
        for line in f:
            data_row = json.loads(line)
            user_id, data = data_row["user_id"], data_row["data"]
            friends = data["friends"]
            groups = data["groups"]

            if isinstance(user_id, str):
                cnt_user_id_as_str += 1
            else:
                assert isinstance(user_id, int)

            assert isinstance(friends, list)
            assert isinstance(groups, list)

            try:
                assert isinstance(friends[0], int)
                assert isinstance(groups[0], int)
            except IndexError:
                empty_friends_or_groups_cnt += 1
            assert user_id not in met_users
            met_users.add(user_id)

    print("Number of empty friends or groups list", empty_friends_or_groups_cnt)
    print("Number of user_ids of type str", cnt_user_id_as_str)


if __name__ == "__main__":
    settings_path = "../settings.json"
    result_file_pth = utils.get_result_path(settings_path)
    check_types_and_unique_users(result_file_pth)

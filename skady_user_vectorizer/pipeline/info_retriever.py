class InfoRetriever:
    # TODO: passing some config to __init__ is bad practice, have to use creator or something like that
    #   idea: rename this class to creator and generate VkRetriever, etc.
    def __init__(self, config):
        self.config = config

    def get_friends(self, users):
        result = []
        for user in users:
            result += [1, 2, 3]
        return result

    def check_groups_open(self, users):
        result = []
        for user in users:
            if user in [1, 2]:
                result.append(True)
            else:
                result.append(False)
        return result

from vk_api.requests_pool import RequestResult
from suvec.common.executing import ResponsesFactory, FriendsParseRes, GroupsParseRes
from suvec.common.requesting import Request


class ResponsesFactoryImpl(ResponsesFactory):
    def __init__(self, friends_parser, groups_parser, request_data_retriever):
        self.friends_parser = friends_parser
        self.groups_parser = groups_parser
        self.request_data_retriever = request_data_retriever

    def create_friends_response(self, request_res: RequestResult, req: Request, session_id):
        error = self.request_data_retriever.get_error(request_res)
        if error is not None:
            friends = None
        else:
            resp_data = self.request_data_retriever.get_resp_data(request_res)
            friends = self.friends_parser.parse(resp_data)

        return FriendsParseRes(friends=friends, error=error, request=req, session_id=session_id)

    def create_groups_response(self, request_res: RequestResult, req: Request, session_id):
        error = self.request_data_retriever.get_error(request_res)
        if error is not None:
            groups = None
        else:
            resp_data = self.request_data_retriever.get_resp_data(request_res)
            groups = self.groups_parser.parse(resp_data)

        return GroupsParseRes(groups=groups, error=error, request=req, session_id=session_id)

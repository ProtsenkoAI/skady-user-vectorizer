from interfaces import Tracker


class StdOutTracker(Tracker):
    # TODO: refactor and add more functionality
    def __init__(self, *args, **kwargs):
        self.friends_added_total = 0
        self.cnt_users_whose_friends_added = 0
        super().__init__(*args, **kwargs)

        self.next_print_friends_nb = self.print_every

    def friends_added(self, friends_nb: int):
        self.friends_added_total += friends_nb
        self.cnt_users_whose_friends_added += 1

        self._print_if_need()

    def groups_added(self, groups_nb: int):
        # TODO: do something!
        ...

    def _print_if_need(self):
        if self.cnt_users_whose_friends_added >= self.next_print_friends_nb:
            self.next_print_friends_nb += self.print_every
            print(f"Total users added: {self.cnt_users_whose_friends_added}")

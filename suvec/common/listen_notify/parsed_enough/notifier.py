from .listener import ParsedEnoughListener


class ParsedEnoughNotifier:
    def __init__(self):
        self.parsed_enough_listeners = []

    def register_parsed_enough_listener(self, listener: ParsedEnoughListener):
        self.parsed_enough_listeners.append(listener)

    def notify_parsed_enough(self):
        for listener in self.parsed_enough_listeners:
            listener.parsed_enough()

from .listener import ParsedEnoughListener


class ParsedEnoughNotifier:
    def __init__(self):
        self.listeners = []

    def register_parsed_enough_listener(self, listener: ParsedEnoughListener):
        self.listeners.append(listener)

    def notify_parsed_enough_listeners(self):
        for listener in self.listeners:
            listener.parsed_enough()

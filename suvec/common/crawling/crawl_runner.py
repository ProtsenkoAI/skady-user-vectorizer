from abc import ABC, abstractmethod

from ..events_tracking import EventsTracker


class CrawlRunner(ABC):
    @abstractmethod
    def __init__(self, *args, tracker: EventsTracker, **kwargs):
        self._tracker = tracker

    @abstractmethod
    def run(self):
        ...

    @abstractmethod
    def stop(self):
        ...

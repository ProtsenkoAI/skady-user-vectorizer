from abc import ABC, abstractmethod

from ..events_tracking import EventsTracker


class CrawlRunner(ABC):
    @abstractmethod
    def run(self):
        ...

    @abstractmethod
    def stop(self):
        ...

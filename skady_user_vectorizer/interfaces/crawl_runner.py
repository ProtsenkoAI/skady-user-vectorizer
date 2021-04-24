from abc import ABC, abstractmethod


class CrawlRunner(ABC):
    @abstractmethod
    def run(self):
        ...

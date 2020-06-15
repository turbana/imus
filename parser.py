from abc import ABC, abstractmethod


class AbstractParser(ABC):
    @abstractmethod
    def parse(self, raw_data):
        pass

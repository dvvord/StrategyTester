from abc import ABCMeta, abstractmethod


class DataHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, symbol, n=1):
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def update(self):
        raise NotImplementedError("Should implement update_bars()")
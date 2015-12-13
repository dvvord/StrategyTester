from __future__ import print_function
from abc import ABCMeta, abstractmethod


class ExecutionHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self):
        raise NotImplementedError("Should implement execute_order()")


class SimulatedExecution(ExecutionHandler):
    def execute_order(self, event):
        pass


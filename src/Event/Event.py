class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type = 'MARKET'


class SignalEvent(Event):
    def __init__(self):
        self.type = 'SIGNAL'


class OrderEvent(Event):
    def __init__(self):
        self.type = 'ORDER'


class FillEvent(Event):
    def __init__(self):
        self.type = 'FILL'


class StopEvent(Event):
    def __init__(self):
        self.type = 'STOP'


class PauseEvent(Event):
    def __init__(self):
        self.type = 'PAUSE'
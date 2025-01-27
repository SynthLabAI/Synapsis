import Synapsis

class Strategy(Synapsis.Bot):
    def __init__(self):
        super.__init__()
        self.price_event_funcs = []
    def main(self, args):
        self.Ticker_manager.create_ticker(callback=self.price_event)

    def price_event(self, tick):
        for func in self.price_event_funcs:
            func(tick, self.coin)

    def add_price_event(self, func, resolution):
        self.price_event_funcs.append(Synapsis.Scheduler(func, resolution))
import Synapsis

class Strategy(Synapsis.Bot):
    def main(self, args):
        self.ticker = self.Ticker_manager.create_ticker(callback=self.price_event)
        self.orderbook = self.Orderbook_manager.create_orderbook(callback=self.orderbook_event)

    def add_price_event(self, callback, resolution):
        """
        Add Orderbook Event
        Args:
            callback: The price event callback that will be added to the current ticker and run at the proper resolution
            resolution: The resolution that the callback will be run
        """
        self.ticker.append_callback(Synapsis.Scheduler(callback, resolution))

    def add_orderbook_event(self, callback):
        """
        Add Orderbook Event
        Args:
            callback: The Orderbook callback that will be added to the current ticker orderbook
        """
        self.orderbook.append_callback(callback)
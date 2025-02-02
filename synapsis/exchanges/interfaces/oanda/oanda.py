from synapsis.exchanges.exchange import Exchange


class Oanda(Exchange):
    def __init__(self, portfolio_name=None, keys_path="keys.json", settings_path=None):
        Exchange.__init__(self, 'oanda', portfolio_name, keys_path, settings_path)

    def get_exchange_state(self):
        return self.interface.get_fees()

    def get_asset_state(self, symbol):
        return self.interface.get_account(symbol)

    def get_direct_calls(self) -> alpaca_trade_api.REST:
        return self.calls

    def get_market_clock(self):
        return self.calls.get_clock()
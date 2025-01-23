"""
    Logic to provide consistency across exchanges
    Copyright (C) 2021  Emerson Dove

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from Synapsis.Coinbase_Pro.Coinbase_Pro_Tickers import Tickers as Coinbase_Pro_Ticker
import Synapsis.Coinbase_Pro.Coinbase_Pro_Utils as Coinbase_Pro_Utils


class APIInterface:
    def __init__(self, type, authenticated_API):
        self.__type = type
        self.__calls = authenticated_API

    """
    Get all currencies in an account
    """
    def get_currencies(self, id=None):
        if self.__type == "coinbase_pro":
            if id is None:
                return self.__calls.get_portfolio()
            else:
                return self.__calls.get_portfolio("id")

    """
    Used for buying or selling market orders
    """
    def market_order(self, size, side, id):
        if self.__type == "coinbase_pro":
            order = Coinbase_Pro_Utils.CoinbaseProUtils().generate_market_order(size, side, id)
            # TODO exchange object needs to be generated here and then returned at some point, this invovles creating a ticker. Tickers are something that need to be managed carefully
            self.__calls.placeOrder(order)

    """
    Used for buying or selling limit orders
    """
    def limit_order(self, size, price, side, id):
        if self.__type == "coinbase_pro":
            order = Coinbase_Pro_Utils.CoinbaseProUtils().generate_limit_order(size, price, side, id)
            # TODO exchange object needs to be generated here and then returned at some point, this invovles creating a ticker. Tickers are something that need to be managed carefully
            self.__calls.placeOrder(order)

    """
    Creates ticker connection.
    """
    def create_ticker(self, callback, currency_id, log=""):
        if self.__type == "coinbase_pro":
            ticker = Coinbase_Pro_Ticker(currency_id, log=log)
            ticker.append_callback(callback)
            return ticker
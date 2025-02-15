"""
    Binance Futures Exchange object.
    Copyright (C) 2021 Matias Kotlik

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
from binance.client import Client

from synapsis.exchanges.auth.auth_constructor import AuthConstructor
from synapsis.exchanges.futures.futures_exchange import FuturesExchange
from synapsis.exchanges.interfaces.binance_futures.binance_futures_interface import BinanceFuturesInterface
from synapsis.exchanges.interfaces.futures_exchange_interface import FuturesExchangeInterface


class BinanceFutures(FuturesExchange):

    def __init__(self,
                 portfolio_name=None,
                 keys_path="keys.json",
                 preferences_path=None):
        super().__init__("binance_futures", portfolio_name, preferences_path)

        # Load auth from keys file
        auth = AuthConstructor(keys_path, portfolio_name, 'binance_futures',
                               ['API_KEY', 'API_SECRET'])

        self.__calls = Client(
            api_key=auth.keys['API_KEY'],
            api_secret=auth.keys['API_SECRET'],
            # pretty sure this breaks futures
            # tld=self.preferences["settings"]['binance']["binance_tld"],
            testnet=self.preferences['settings']['use_sandbox'])

        self.__interface = BinanceFuturesInterface(self.exchange_type,
                                                   self.calls)

        self.initialize()

    @property
    def calls(self):
        return self.__calls

    @property
    def interface(self) -> FuturesExchangeInterface:
        return self.__interface

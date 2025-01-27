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


import time
import warnings
import pandas as pd
import Synapsis.utils.utils as utils
import Synapsis.utils.paper_trading.utils as paper_trade
import Synapsis.utils.paper_trading.local_account.trade_local as trade_local
from Synapsis.utils.exceptions import InvalidOrder
from Synapsis.utils.purchases.limit_order import LimitOrder
from Synapsis.utils.purchases.market_order import MarketOrder

from Synapsis.interface.currency_Interface import CurrencyInterface


class CoinbaseProInterface(CurrencyInterface):
    def __init__(self, exchange_name, authenticated_API):
        super().__init__(exchange_name, authenticated_API)

    def init_exchange(self):
        fees = self.calls.get_fees()
        try:
            if fees['message'] == "Invalid API Key":
                raise LookupError("Invalid API Key - are you trying to use your normal exchange keys "
                                  "while in sandbox mode?")
        except KeyError:
            pass
        self.__exchange_properties = {
            "maker_fee_rate": fees['maker_fee_rate'],
            "taker_fee_rate": fees['taker_fee_rate']
        }

    def get_products(self):
        needed = self.needed['get_products']
        """
        [
            {
                "id": "BTC-USD",
                "base_currency": "BTC",
                "quote_currency": "USD",
                "base_min_size": "0.0001",
                "base_max_size": "280",
                "quote_increment": "0.01",
                "base_increment": "0.00000001",
                "display_name": "BTC/USD",
                "min_market_funds": "5",
                "max_market_funds": "1000000",
                "margin_enabled": False,
                "post_only": False,
                "limit_only": False,
                "cancel_only": False,
                "trading_disabled": False,
                "status": "online",
                "status_message": "",
            },
        ]
        """
        products = self.calls.get_products()
        for i in range(len(products)):
            # Rename needed
            products[i]["currency_id"] = products[i].pop("id")
            # Isolate unimportant
            products[i] = utils.isolate_specific(needed, products[i])
        return products

    def get_account(self, currency=None, override_paper_trading=False):
        """
        Get all currencies in an account, or sort by currency/account_id
        Args:
            currency (Optional): Filter by particular currency
            override_paper_trading (Optional bool): If paper trading is enabled, setting this to true will get the
             actual account values

            These arguments are mutually exclusive
        Coinbase Pro: get_account
        Binance: get_account["balances"]
        """
        currency, internal_paper_trade = super().get_account(currency=currency, override_paper_trading=override_paper_trading)

        needed = self.needed['get_account']
        """
        [
            {
                "id": "71452118-efc7-4cc4-8780-a5e22d4baa53",
                "currency": "BTC",
                "balance": "0.0000000000000000",
                "available": "0.0000000000000000",
                "hold": "0.0000000000000000",
                "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
            },
            {
                ...
            }
        ]
        """
        if not internal_paper_trade:
            accounts = self.calls.get_accounts()
        else:
            local_account = trade_local.get_accounts()
            accounts = []
            for key, value in local_account.items():
                accounts.append({
                    'currency': key,
                    'balance': value,
                    'available': value,
                    'hold': 0
                })
        # We have to sort through it if the accounts are none
        if currency is None:
            # If this is also none we just return raw, which we do later
            pass
        else:
            for i in accounts:
                if i["currency"] == currency:
                    parsed_value = utils.isolate_specific(needed, i)
                    return parsed_value
            warnings.warn("Currency not found")
        for i in range(len(accounts)):
            accounts[i] = utils.isolate_specific(needed, accounts[i])
        return accounts

    def market_order(self, product_id, side, funds) -> MarketOrder:
        """
        Used for buying or selling market orders
        Args:
            product_id: currency to buy
            side: buy/sell
            funds: desired amount of quote currency to use
        """
        needed = self.needed['market_order']
        """
        {
            'id': '8d3a6ea5-8d6d-4486-9c98-b266bae9a67c', 
            'product_id': 'BTC-USD', 
            'side': 'buy', 
            'stp': 'dc', 
            'funds': '39.92015968', 
            'specified_funds': '40', 
            'type': 'market', 
            'post_only': False, 
            'created_at': 1621015423.292914, 
            'fill_fees': '0', 
            'filled_size': '0', 
            'executed_value': '0', 
            'status': 'pending', 
            'settled': False
        }
        """
        order = {
            'funds': funds,
            'side': side,
            'product_id': product_id,
            'type': 'market'
        }
        if not self.paper_trading:
            response = self.calls.place_market_order(product_id, side, funds=funds)
            if "message" in response:
                raise InvalidOrder("Invalid Order: " + response["message"])
            response["created_at"] = utils.epoch_from_ISO8601(response["created_at"])
        else:
            print("Paper trading...")
            creation_time = time.time()
            price = self.get_price(product_id)
            min_funds = float(self.get_market_limits(product_id)["exchange_specific"]["min_market_funds"])
            if funds < min_funds:
                raise InvalidOrder("Invalid Order: funds is too small. Minimum is: " + str(min_funds))

            if not trade_local.test_trade(product_id, side, funds / price, price):
                raise InvalidOrder("Invalid Order: Insufficient funds")
            # Create coinbase pro-like id
            coinbase_pro_id = paper_trade.generate_coinbase_pro_id()
            response = {
                'id': str(coinbase_pro_id),
                'side': str(side),
                'type': 'market',
                'status': 'done',
                'product_id': str(product_id),
                'funds': str(funds - funds * float((self.__exchange_properties["maker_fee_rate"]))),
                'specified_funds': str(funds),
                'post_only': 'false',
                'created_at': str(creation_time),
                'done_at': str(time.time()),
                'done_reason': 'filled',
                'fill_fees': str(funds * float((self.__exchange_properties["maker_fee_rate"]))),
                'filled_size': str(funds - funds * float((self.__exchange_properties["maker_fee_rate"])) / price),
                'executed_value': str(funds - funds * float((self.__exchange_properties["maker_fee_rate"]))),
                'settled': 'true'
            }
            self.paper_trade_orders.append(response)
        response = utils.isolate_specific(needed, response)
        return MarketOrder(order, response, self)

    def limit_order(self, product_id, side, price, size) -> LimitOrder:
        """
        Used for buying or selling limit orders
        Args:
            product_id: currency to buy
            side: buy/sell
            price: price to set limit order
            size: amount of currency (like BTC) for the limit to be valued
            kwargs: specific arguments that may be used by each exchange, (if exchange is known)
        """
        needed = self.needed['limit_order']
        """
        {
            "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
            "price": "0.10000000",
            "size": "0.01000000",
            "product_id": "BTC-USD",
            "side": "buy",
            "stp": "dc",
            "type": "limit",
            "time_in_force": "GTC",
            "post_only": false,
            "created_at": "2016-12-08T20:02:28.53864Z",
            "fill_fees": "0.0000000000000000",
            "filled_size": "0.00000000",
            "executed_value": "0.0000000000000000",
            "status": "pending",
            "settled": false
        }
        """
        order = {
            'size': size,
            'side': side,
            'price': price,
            'product_id': product_id,
            'type': 'limit'
        }
        if not self.paper_trading:
            response = self.calls.place_limit_order(product_id, side, price, size=size)
            if "message" in response:
                raise InvalidOrder("Invalid Order: " + response["message"])
            response["created_at"] = utils.epoch_from_ISO8601(response["created_at"])
        else:
            print("Paper trading...")
            creation_time = time.time()
            min_base = float(self.get_market_limits(product_id)["base_min_size"])
            if size < min_base:
                raise InvalidOrder("Invalid Order: Order quantity is too small. Minimum is: " + str(min_base))

            if not trade_local.test_trade(product_id, side, size, price):
                raise InvalidOrder("Invalid Order: Insufficient funds")

            # Create coinbase pro-like id
            coinbase_pro_id = paper_trade.generate_coinbase_pro_id()
            response = {
                'id': str(coinbase_pro_id),
                'price': str(price),
                'size': str(size),
                'product_id': str(product_id),
                'side': str(side),
                'stp': 'dc',
                'type': 'limit',
                "time_in_force": "GTC",
                'post_only': 'false',
                'created_at': str(creation_time),
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                'status': 'pending',
                'settled': 'false'
            }
            self.paper_trade_orders.append(response)
        response = utils.isolate_specific(needed, response)
        return LimitOrder(order, response, self)

    def cancel_order(self, currency_id, order_id) -> dict:
        """
        Returns:
            dict: Containing the order_id of cancelled order. Example::
            { "order_id": "c5ab5eae-76be-480e-8961-00792dc7e138" }
        """
        if not self.paper_trading:
            return {"order_id": self.calls.cancel_order(order_id)[0]}
        else:
            """
            This block could potentially work for both exchanges
            """
            order_index = None
            for i in range(len(self.paper_trade_orders)):
                index = self.paper_trade_orders[i]
                if index['status'] == 'pending' and index['id'] == order_id:
                    order_index = i

            if order_index is not None:
                id = self.paper_trade_orders[order_index]['id']
                del self.paper_trade_orders[order_index]
                return {"order_id": id}

    def get_open_orders(self, product_id=None):
        """
        List open orders.
        """
        needed = self.needed['get_open_orders']
        """
        [
            {
                "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
                "price": "0.10000000",
                "size": "0.01000000",
                "product_id": "BTC-USD",
                "side": "buy",
                "stp": "dc",
                "type": "limit",
                "time_in_force": "GTC",
                "post_only": false,
                "created_at": "2016-12-08T20:02:28.53864Z",
                "fill_fees": "0.0000000000000000",
                "filled_size": "0.00000000",
                "executed_value": "0.0000000000000000",
                "status": "open",
                "settled": false
            },
            {
                ...
            }
        ]
        """
        if not self.paper_trading:
            if product_id is None:
                orders = list(self.calls.get_orders())
            else:
                orders = list(self.calls.get_orders(product_id=product_id))

            if len(orders) == 0:
                return []
            if orders[0] == 'message':
                raise InvalidOrder("Invalid Order: " + str(orders))

            for i in range(len(orders)):
                orders[i] = utils.isolate_specific(needed, orders[i])

            return orders
        else:
            open_orders = []
            for i in self.paper_trade_orders:
                if i["status"] == "open":
                    open_orders.append(i)

            return open_orders

    def get_order(self, currency_id, order_id) -> dict:
        needed = self.needed['get_order']
        """
        {
            "created_at": "2017-06-18T00:27:42.920136Z",
            "executed_value": "0.0000000000000000",
            "fill_fees": "0.0000000000000000",
            "filled_size": "0.00000000",
            "id": "9456f388-67a9-4316-bad1-330c5353804f",
            "post_only": true,
            "price": "1.00000000",
            "product_id": "BTC-USD",
            "settled": false,
            "side": "buy",
            "size": "1.00000000",
            "status": "pending",
            "stp": "dc",
            "time_in_force": "GTC",
            "type": "limit"
        }
        This is the response for a market order
        {
            'id': '8d3a6ea5-8d6d-4486-9c98-b266bae9a67c', 
            'side': 'buy', 
            'type': 'market', 
            'status': 'done',
            'product_id': 'BTC-USD',
            'profile_id': '4107a8cc-9fee-4ed4-b609-d87011675ed5',
            'funds': '39.9201596800000000', 
            'specified_funds': '40.0000000000000000',
            'post_only': False, 
            'created_at': '2021-05-14T18:03:43.292914Z',
            'done_at': '2021-05-14T18:03:43.297Z', 
            'done_reason': 'filled',
            'fill_fees': '0.0798400768200000', 
            'filled_size': '0.00078825',
            'executed_value': '39.9200384100000000', 
            'settled': True
        }
        """
        if not self.paper_trading:
            response = self.calls.get_order(order_id)
            return utils.isolate_specific(needed, response)
        else:
            for i in self.paper_trade_orders:
                if i["id"] == order_id:
                    return i

    """
    Coinbase Pro: get_fees
    Binance: get_trade_fee
    """

    def get_fees(self):
        needed = self.needed['get_fees']
        """
        {
            'maker_fee_rate': '0.0050',
            'taker_fee_rate': '0.0050',
            'usd_volume': '37.69'
        }
        """
        fees = self.calls.get_fees()
        return utils.isolate_specific(needed, fees)

    """
    Coinbase Pro: get_account_history
    Binance: 
        get_deposit_history
        get_withdraw_history

    """

    def get_product_history(self, product_id, epoch_start, epoch_stop, granularity):
        """
        Returns the product history from an exchange
        Args:
            product_id: Synapsis product ID format (BTC-USD)
            epoch_start: Time to begin download
            epoch_stop: Time to stop download
            granularity: Resolution in seconds between tick (ex: 60 = 1 per minute)
        Returns:
            Dataframe with *at least* 'time (epoch)', 'low', 'high', 'open', 'close', 'volume' as columns.
        """
        epoch_start, epoch_stop = super().get_product_history(product_id, epoch_start, epoch_stop, granularity)

        accepted_grans = [60, 300, 900, 3600, 21600, 86400]
        if granularity not in accepted_grans:
            warnings.warn("Granularity is not an accepted granularity...rounding to nearest valid value.")
            granularity = accepted_grans[min(range(len(accepted_grans)),
                                             key=lambda i: abs(accepted_grans[i] - granularity))]

        # Figure out how many points are needed
        need = int((epoch_stop - epoch_start) / granularity)
        window_open = epoch_start
        history = []
        # Iterate while its more than max
        while need > 300:
            # Close is always 300 points ahead
            window_close = window_open + 300 * granularity
            open_iso = utils.ISO8601_from_epoch(window_open)
            close_iso = utils.ISO8601_from_epoch(window_close)
            history = history + self.calls.get_product_historic_rates(product_id, open_iso, close_iso,
                                                                      granularity)

            window_open = window_close
            need -= 300
            time.sleep(1)

        # Fill the remainder
        open_iso = utils.ISO8601_from_epoch(window_open)
        close_iso = utils.ISO8601_from_epoch(epoch_stop)
        history_block = history + self.calls.get_product_historic_rates(product_id, open_iso, close_iso,
                                                                        granularity)
        history_block.sort(key=lambda x: x[0])
        return pd.DataFrame(history_block, columns=['time', 'low', 'high', 'open', 'close', 'volume'])

    """
    Coinbase Pro: Get Currencies
    Binance: get_products
    """

    def get_market_limits(self, product_id):
        needed = self.needed['get_market_limits']
        renames = [
            ["id", "market"]
        ]
        """
        Returns:
        list: List of available currency pairs. Example::
            [
                {
                    "id": "BTC-USD",
                    "display_name": "BTC/USD",
                    "base_currency": "BTC",
                    "quote_currency": "USD",
                    "base_increment": "0.00000001",
                    "quote_increment": "0.01000000",
                    "base_min_size": "0.00100000",
                    "base_max_size": "280.00000000",
                    "min_market_funds": "5",
                    "max_market_funds": "1000000",
                    "status": "online",
                    "status_message": "",
                    "cancel_only": false,
                    "limit_only": false,
                    "post_only": false,
                    "trading_disabled": false
                },
                ...
            ]
            """
        response = self.calls.get_products()
        products = None
        for i in response:
            if i["id"] == product_id:
                products = i

        if products is None:
            raise LookupError("Specified market not found")

        products = utils.rename_to(renames, products)
        products["min_price"] = 0
        # These don't really exist on this exchange
        products["max_price"] = -1
        products["max_orders"] = -1
        return utils.isolate_specific(needed, products)

    def get_price(self, currency_pair) -> float:
        """
        Returns just the price of a currency pair.
        """
        """
        {
            'trade_id': 28976297, 
            'price': '57579.72', 
            'size': '0.00017367', 
            'time': '2021-05-01T17:01:32.717482Z', 
            'bid': '57579.72', 
            'ask': '57579.74', 
            'volume': '31137.51184419'
        }
        """
        response = self.calls.get_product_ticker(currency_pair)
        return float(response['price'])

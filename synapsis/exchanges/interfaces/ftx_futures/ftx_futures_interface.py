import operator

from synapsis.enums import MarginType, HedgeMode, Side, PositionMode, TimeInForce, ContractType, OrderStatus, OrderType
from synapsis.exchanges.interfaces.ftx.ftx_api import FTXAPI
from synapsis.exchanges.interfaces.futures_exchange_interface import FuturesExchangeInterface
from synapsis.exchanges.orders.futures.futures_order import FuturesOrder
from synapsis.utils import utils as utils, exceptions
import datetime


class FTXFuturesInterface(FuturesExchangeInterface):
    calls: FTXAPI

    @staticmethod
    def get_contract_type(symbol: str) -> ContractType:
        if '-PERP' in symbol:
            return ContractType.PERPETUAL
        elif '-MOVE' in symbol:
            return ContractType.MOVE
        return ContractType.EXPIRING

    @staticmethod
    def parse_timestamp(time: str) -> int:
        return int(datetime.datetime.fromisoformat(time).timestamp())

    @staticmethod
    def to_order_status(status: str, cancel: bool = False) -> OrderStatus:
        if status in ('new', 'open'):
            return OrderStatus.OPEN
        elif status == 'closed':
            if cancel:
                return OrderStatus.CANCELED
            else:
                return OrderStatus.FILLED
        raise ValueError(f'invalid order status: {status}')

    @staticmethod
    def to_order_type(type: str) -> OrderType:
        if type == 'market':
            return OrderType.MARKET
        elif type == 'limit':
            return OrderType.LIMIT
        elif type == 'takeProfit':
            return OrderType.TAKE_PROFIT
        elif type == 'stop':
            return OrderType.STOP
        raise ValueError(f'invalid order type: {type}')

    def parse_order_response(self,
                             response: dict,
                             cancel: bool = False) -> FuturesOrder:
        return FuturesOrder(
            symbol=response['future'],
            id=int(response['id']),
            status=self.to_order_status(response['status'], cancel),
            size=float(response['size']),
            created_at=self.parse_timestamp(response['createdAt']),
            type=self.to_order_type(response['type']),
            contract_type=self.get_contract_type(response['future']),
            side=Side(response['side']),
            position=PositionMode.BOTH,
            price=float(response['price']),
            time_in_force=TimeInForce.IOC
            if response['ioc'] else TimeInForce.GTC,
            response=response,
            interface=self)

    def init_exchange(self):
        # will throw exception if our api key is stinky
        self.calls.get_account_info()

    def get_products(self) -> dict:
        res = self.calls.list_futures()
        return {
            symbol['name']: utils.AttributeDict({
                'base': symbol['underlying'],
                'quote': 'USD',
                'contract_type': self.get_contract_type(symbol['name']),
                'exchange_specific': symbol
            })
            for symbol in res
        }

    def get_account(self, filter: str = None) -> utils.AttributeDict:
        balances = self.calls.get_balances()
        coins = self.calls.get_coins()
        accounts = utils.AttributeDict({
            coin['id']: utils.AttributeDict({'available': 0})
            for coin in coins
        })

        for bal in balances:
            accounts[bal['coin']] = utils.AttributeDict({
                'available': float(bal['free']),
                'exchange_specific': bal
            })

        if filter:
            return accounts[filter]
        return accounts

    def get_positions(self, filter: str = None) -> utils.AttributeDict:
        leverage = self.get_leverage()

        positions = {
            future['name']: utils.AttributeDict({'size': 0})
            for future in self.calls.list_futures()
        }

        res = self.calls.get_positions()
        for position in res:
            positions[position['future']] = utils.AttributeDict({
                'size': position['netSize'],
                'side': PositionMode(position['side'].lower()),
                'entry_price': float(position['entryPrice']),
                'contract_type': self.get_contract_type(position['future']),
                'leverage': leverage,
                'margin_type': MarginType.CROSSED,
                'unrealized_pnl': float(
                    position['unrealizedPnl']),  # TODO not sure on this one
                'exchange_specific': position
            })

        if filter:
            return positions[filter]
        return positions


    def market_order(self,
                     symbol: str,
                     side: Side,
                     size: float,
                     position: PositionMode = PositionMode.BOTH,
                     reduce_only: bool = False) -> FuturesOrder:
        # TODO these checks could be moved out of the order methods?
        if position != PositionMode.BOTH:
            raise ValueError(
                f'position mode {position} not supported on FTX Futures')
        res = self.calls.place_order(symbol, side, None, size, 'market',
                                     reduce_only)
        return self.parse_order_response(res)

    def limit_order(
            self,
            symbol: str,
            side: Side,
            price: float,
            size: float,
            position: PositionMode = PositionMode.BOTH,
            reduce_only: bool = False,
            time_in_force: TimeInForce = TimeInForce.GTC) -> FuturesOrder:
        if time_in_force == TimeInForce.GTC:
            ioc = False
        elif time_in_force == TimeInForce.IOC:
            ioc = True
        else:
            raise ValueError(
                f'time in force {time_in_force} not supported on FTX Futures')
        if position != PositionMode.BOTH:
            raise ValueError(
                f'position mode {position} not supported on FTX Futures')
        res = self.calls.place_order(symbol,
                                     side,
                                     price,
                                     size,
                                     'limit',
                                     reduce_only,
                                     ioc=ioc)
        return self.parse_order_response(res)

    def take_profit(
            self,
            symbol: str,
            side: Side,
            price: float,
            size: float,
            position: PositionMode = PositionMode.BOTH) -> FuturesOrder:
        if position != PositionMode.BOTH:
            raise ValueError(
                f'position mode {position} not supported on FTX Futures')
        res = self.calls.place_conditional_order(symbol,
                                                 side,
                                                 size,
                                                 'takeProfit',
                                                 trigger_price=price)
        return self.parse_order_response(res)

    def stop_loss(self,
                  symbol: str,
                  side: Side,
                  price: float,
                  size: float,
                  position: PositionMode = PositionMode.BOTH) -> FuturesOrder:
        if position != PositionMode.BOTH:
            raise ValueError(
                f'position mode {position} not supported on FTX Futures')
        res = self.calls.place_conditional_order(symbol,
                                                 side,
                                                 size,
                                                 'stop',
                                                 trigger_price=price)
        return self.parse_order_response(res)

    @utils.order_protection
    def set_hedge_mode(self, hedge_mode: HedgeMode):
        if hedge_mode == HedgeMode.HEDGE:
            raise Exception('HEDGE mode not supported on FTX Futures')
        pass  # FTX only has ONEWAY mode

    @utils.order_protection
    def set_leverage(self, leverage: int, symbol: str = None):
        if symbol:
            raise Exception(
                'FTX Futures does not allow setting leverage per symbol. Use interface.set_leverage(leverage) to set '
                'account-wide leverage instead. ')
        self.calls.change_account_leverage(leverage)

    def get_leverage(self, symbol: str = None) -> float:
        return self.calls.get_account_info()['leverage']

    @utils.order_protection
    def set_margin_type(self, symbol: str, type: MarginType):
        if type == MarginType.ISOLATED:
            raise Exception('ISOLATED margin not supported on FTX Futures')
        pass

    def cancel_order(self, symbol: str, order_id: int) -> FuturesOrder:
        res = self.get_order(symbol, order_id)
        res.status = OrderStatus.CANCELED
        self.calls.cancel_order(str(order_id))
        return res

    def get_open_orders(self, symbol: str) -> list:
        return [
            self.parse_order_response(o) for o in self.calls.get_open_orders()
        ]

    def get_order(self, symbol: str, order_id: int) -> FuturesOrder:
        response = self.calls.get_order_by_id(str(order_id))
        if response['symbol'] != symbol:
            raise Exception(
                'response symbol did not match parameter -- this should never happen'
            )
        return self.parse_order_response(response)

    def get_price(self, symbol: str) -> float:
        return float(self.calls.get_future(symbol)['mark'])

    def get_funding_rate_history(self, symbol: str, epoch_start: int,
                                 epoch_stop: int) -> list:
        if self.get_contract_type(symbol) != ContractType.PERPETUAL:
            return []

        # TODO dedup binance_futures_exchange maybe?
        history = []
        resolution = self.get_funding_rate_resolution()
        LIMIT = 500
        window_start = epoch_start
        window_end = epoch_start + LIMIT * resolution

        response = True
        while response:
            response = self.calls.get_funding_rates(window_start, window_end,
                                                    symbol)

            history.extend({
                'rate': float(e['rate']),
                'time': self.parse_timestamp(e['time'])
            } for e in response)

            if response:
                window_start = window_end
                window_end = min(epoch_stop, window_start + LIMIT * resolution)

        return sorted(history, key=operator.itemgetter('time'))

    def get_funding_rate_resolution(self) -> int:
        return 60 * 60  # hour

    def get_product_history(self, symbol, epoch_start, epoch_stop, resolution):
        raise NotImplementedError

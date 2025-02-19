"""
    __init__ file to give the module access to the libraries.
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
import synapsis.utils.utils
import synapsis.data as data
from synapsis.exchanges.interfaces.coinbase_pro.coinbase_pro import CoinbasePro
from synapsis.exchanges.interfaces.binance.binance import Binance
from synapsis.exchanges.interfaces.alpaca.alpaca import Alpaca
from synapsis.exchanges.interfaces.oanda.oanda import Oanda
from synapsis.exchanges.interfaces.kucoin.kucoin import Kucoin
from synapsis.exchanges.interfaces.ftx.ftx import FTX
from synapsis.exchanges.interfaces.okx.okx import Okx
from synapsis.exchanges.interfaces.paper_trade.paper_trade import PaperTrade
from synapsis.exchanges.interfaces.keyless.keyless import KeylessExchange
from synapsis.frameworks.strategy import Strategy as Strategy
from synapsis.frameworks.model.model import Model as Model
from synapsis.frameworks.strategy import StrategyState as StrategyState
from synapsis.frameworks.screener.screener import Screener
from synapsis.frameworks.screener.screener_state import ScreenerState

from synapsis.exchanges.managers.ticker_manager import TickerManager
from synapsis.exchanges.managers.orderbook_manager import OrderbookManager
from synapsis.exchanges.managers.general_stream_manager import GeneralManager
from synapsis.exchanges.interfaces.abc_exchange_interface import ABCExchangeInterface as Interface
from synapsis.frameworks.multiprocessing.synapsis_bot import SynapsisBot
from synapsis.utils.utils import trunc
import synapsis.utils.utils as utils
from synapsis.utils.scheduler import Scheduler
import synapsis.indicators as indicators
from synapsis.utils import time_builder

from synapsis.enums import Side, OrderType, OrderStatus, TimeInForce

from synapsis.deployment.reporter_headers import Reporter as __Reporter_Headers
is_deployed = False
_screener_runner = None



_backtesting = synapsis.utils.check_backtesting()
try:
    from synapsis_external import Reporter as __Reporter
    reporter = __Reporter
    is_deployed = True
except ImportError:
    reporter = __Reporter_Headers()

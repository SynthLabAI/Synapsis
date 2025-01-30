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

from Synapsis.exchanges.interfaces.coinbase_pro.coinbase_pro import CoinbasePro
from Synapsis.exchanges.interfaces.Binance.Binance import Binance
from Synapsis.exchanges.interfaces.Alpaca.alpaca import Alpaca
from Synapsis.exchanges.interfaces.paper_trade.paper_trade import PaperTrade
from Synapsis.strategy import Strategy as Strategy
from Synapsis.strategy import StrategyState as StrategyState

from Synapsis.exchanges.managers.ticker_manager import TickerManager
from Synapsis.exchanges.managers.orderbook_manager import OrderbookManger
from Synapsis.exchanges.managers.general_stream_manager import GeneralManager
from Synapsis.exchanges.interfaces.abc_exchange_interface import ABCExchangeInterface as Interface
from Synapsis.strategy.synapsis_bot import SynapsisBot
import Synapsis.utils.utils as utils
from Synapsis.utils.scheduler import Scheduler
import Synapsis.indicators as indicators
from Synapsis.utils import time_builder

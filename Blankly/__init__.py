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

from Synapsis.exchanges.interfaces.Coinbase_Pro.Coinbase_Pro import Coinbase_Pro as Coinbase_Pro
from Synapsis.exchanges.interfaces.Binance.Binance import Binance as Binance
from Synapsis.exchanges.interfaces.Alpaca.Alpaca import Alpaca as Alpaca
from Synapsis.exchanges.interfaces.Paper_Trade.Paper_Trade import PaperTrade

from Synapsis.exchanges.managers.ticker_manager import TickerManager as TickerManager
from Synapsis.exchanges.managers.orderbook_manager import OrderbookManger as OrderbookManager
from Synapsis.exchanges.managers.general_stream_manager import GeneralManager as GeneralManager
from Synapsis.exchanges.interfaces.abc_currency_interface import ICurrencyInterface as Interface
from Synapsis.strategy.synapsis_bot import SynapsisBot
import Synapsis.utils.utils as utils
from Synapsis.utils.scheduler import Scheduler
import Synapsis.indicators as indicators
from Synapsis.utils import time_builder

from Synapsis.strategy.strategy_base import Strategy

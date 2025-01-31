from Synapsis.auth.Alpaca.auth import AlpacaAuth
from Synapsis.auth.direct_calls_factory import InterfaceFactory
import pytest

from Synapsis.exchanges.Alpaca.alpaca_api_interface import AlpacaInterface
from tests.helpers.comparisons import is_sub_dict
from pathlib import Path
import logging
import datetime
import time
import pytz

timeZ_Ny = pytz.timezone('America/New_York')

MARKET_OPEN = datetime.time(hour=9, minute=0, second=0, tzinfo=timeZ_Ny)
MARKET_CLOSE = datetime.time(hour=17, minute=0, second=0, tzinfo=timeZ_Ny)

@pytest.fixture
def alpaca_interface() -> None:
    keys_file_path = Path("tests/config/keys.json").resolve()
    settings_file_path = Path("tests/config/settings.json").resolve()

    auth_obj = AlpacaAuth(keys_file_path, "alpaca test portfolio")
    _, alpaca_interface = InterfaceFactory.create("alpaca", auth_obj, settings_file_path)
    return alpaca_interface


def test_get_exchange(alpaca_interface: AlpacaInterface) -> None:
    assert alpaca_interface.get_exchange_type() == 'alpaca'

def test_get_buy_sell(alpaca_interface: AlpacaInterface) -> None:
    ny_time = datetime.datetime.now(timeZ_Ny).time()
    if ny_time > MARKET_CLOSE or ny_time < MARKET_OPEN:
        return

    known_apple_info = {
              "id": "904837e3-3b76-47ec-b432-046db621571b",
              "class": "us_equity",
              "exchange": "NASDAQ",
              "symbol": "AAPL",
              "status": "active",
              "tradable": True,
              "marginable": True,
              "shortable": True,
              "easy_to_borrow": True,
              "fractionable": True
            }

    # query for the unique ID of AAPL
    products = alpaca_interface.get_products()
    apple_id = None

    for product in products:
        if product['base_currency'] == 'AAPL':
            apple_id = product['currency_id']

    assert apple_id

    market_order = alpaca_interface.market_order(apple_id, 'buy', 200)

    num_retries = 0
    # wait until order is filled
    while alpaca_interface.get_order('AAPL', market_order.get_id())['price'] is None:
        time.sleep(1)
        num_retries += 1
        if num_retries > 10:
            raise TimeoutError("Too many retries, cannot get order status")

    resp = alpaca_interface.get_order('AAPL', market_order.get_id())

    # get_position(symbol)

    # get_asset(symbol)

    # place sell order

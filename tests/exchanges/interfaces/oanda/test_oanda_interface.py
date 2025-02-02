import datetime
import time
from datetime import datetime as dt
from pathlib import Path

import pytest
import pytz

from synapsis.exchanges.interfaces.oanda.oanda_api import OandaAPI
from synapsis.exchanges.interfaces.oanda.oanda_auth import OandaAuth
from synapsis.exchanges.interfaces.oanda.oanda_interface import OandaInterface
from synapsis.exchanges.interfaces.direct_calls_factory import DirectCallsFactory

timeZ_Ny = pytz.timezone('America/New_York')
MARKET_OPEN = datetime.time(hour=9, minute=0, second=0, tzinfo=timeZ_Ny)
MARKET_CLOSE = datetime.time(hour=17, minute=0, second=0, tzinfo=timeZ_Ny)


@pytest.fixture
def oanda_interface():
    keys_file_path = Path("tests/config/keys.json").resolve()
    settings_file_path = Path("tests/config/settings.json").resolve()

    auth_obj = OandaAuth(str(keys_file_path), "oanda test portfolio")
    _, oanda_interface = DirectCallsFactory.create("oanda", auth_obj, str(settings_file_path))
    return oanda_interface


def test_get_exchange(oanda_interface: OandaInterface) -> None:
    assert oanda_interface.get_exchange_type() == 'oanda'

def test_market_order(oanda_interface: OandaInterface) -> None:
    resp = oanda_interface.market_order("EUR_USD", "buy", 100)
    print(resp)
    assert False

def test_get_all_open_orders(oanda_interface: OandaInterface) -> None:
    resp = oanda_interface.get_open_orders()
    print(resp)
    assert False

def test_get_order(oanda_interface: OandaInterface) -> None:
    resp = oanda_interface.get_order("hello", 4)
    print(resp)
    assert False

def test_api() -> None:
    keys_file_path = Path("tests/config/keys.json").resolve()
    settings_file_path = Path("tests/config/settings.json").resolve()

    auth_obj = OandaAuth(str(keys_file_path), "oanda test portfolio")
    api, _ = DirectCallsFactory.create("oanda", auth_obj, str(settings_file_path))
    assert isinstance(api, OandaAPI)
    x = api.get_all_accounts()
    print(api.get_all_accounts())
    print(api.get_account())
    print(api.get_account_summary())
    print(api.get_account_instruments())
    print(api.get_account_changes('3'))
    y = api.get_all_open_orders()
    z = api.get_orders("EUR_CAD")
    assert(False)

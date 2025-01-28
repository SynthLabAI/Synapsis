from Synapsis.auth.Alpaca.auth import alpaca_auth
from Synapsis.interface.currency_factory import InterfaceFactory

def test_alpaca_interface():
    auth_obj = alpaca_auth("/Users/arunannamalai/Documents/Synapsis/Examples/keys.json", "paper account")
    alpaca_interface = InterfaceFactory.create_interface("alpaca", None, auth_obj)


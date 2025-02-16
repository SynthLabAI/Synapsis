from synapsis.exchanges.exchange import Exchange
from synapsis.exchanges.auth.auth_constructor import AuthConstructor
from synapsis.exchanges.interfaces.okex.okex_api import SpotAPI as OkexAPI


class Okex(Exchange):
    def __init__(self, portfolio_name=None, keys_path="keys.json", settings_path=None):
        Exchange.__init__(self, "okex", portfolio_name, settings_path)

        # Load the auth from the keys file
        auth = AuthConstructor(keys_path, portfolio_name, 'okex', ['API_KEY', 'API_SECRET', 'API_PASS'])
        keys = auth.keys

        calls = OkexAPI(api_key=keys['API_KEY'],
                        api_secret_key=keys['API_SECRET'],
                        passphrase=keys['API_PASS'])

        # Always finish the method with this function
        super().construct_interface_and_cache(calls)

    """
    Builds information about the asset on this exchange by making particular API calls
    """

    def get_asset_state(self, symbol):
        """
        This determines the internal properties of the exchange block.
        Should be implemented per-class because it requires different types of interaction with each exchange.
        """
        # TODO Populate this with useful information
        return self.interface.get_account(symbol)

    def get_exchange_state(self):
        """
        Exchange state is the external properties for the exchange block
        """
        # TODO Populate this with useful information
        return self.interface.get_fees()

    def get_direct_calls(self) -> dict:
        return self.calls

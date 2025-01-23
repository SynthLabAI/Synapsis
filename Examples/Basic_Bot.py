import time
import Synapsis
from Synapsis import SynapsisBot


class Bot(SynapsisBot):
    def __init__(self):
        super().__init__()

    def main(self, args=None):
        """
        Main function to write the trading logic
        """
        # Use this to get IDE autofill
        assert isinstance(self.Interface, Synapsis.APIInterface)

        # Add a heartbeat example to report to GUI
        self.update_state("Heartbeat", 0)

        # Example on how to interact with API
        # print(self.Interface.get_currencies())

        while True:
            """ Demo interface call """
            self.update_state("Heartbeat", self.get_state()["Heartbeat"] + 1)
            time.sleep(1)

    def price_event(self, tick):
        """
        Is called on price event updates by the ticker
        """
        # Example of updating the price state for the GUI
        self.update_state("Price", tick["price"])
        print("New price tick at: " + tick["price"])


if __name__ == "__main__":
    """
    Easily setup and run a model on any exchange
    """
    # Define preferences, base currency is needed for the trading.
    user_preferences = {
        # Example portion of the settings to make a minimum example
        "settings": {
            "base_currency": "USD"
        }
    }

    # Keys file contains authentication keys
    import Keys

    auth = [Keys.API_KEY, Keys.API_SECRET, Keys.API_PASS]

    # This creates an authenticated exchange. Now we can append models.
    exchange = Synapsis.Coinbase_Pro(name="API Exchange", user_preferences=user_preferences, auth=auth)
    # Imagine this:
    #   Coinbase Pro <-- Choosing to assign this bot to this exchange
    #   Kraken
    #   Bitfinex

    # Create the bot and add it to run as a coinbase_pro bitcoin model.
    bot = Bot()

    exchange.append_model(bot, "GRT")
    # Imagine this:
    #   Coinbase Pro:
    #       Bitcoin
    #       Ethereum
    #       Stellar
    #       The Graph <-- Added to the data from this currency

    # Begins running the main() function of the model on a different process
    exchange.start_models()
    # Imagine this:
    #   Coinbase Pro:
    #       Bitcoin
    #       Ethereum
    #       Stellar
    #       The Graph <-- Bot <-- Asking to start

    # Now other processes can be created or just continue with this one.
    while True:
        # Print the state every 2 seconds
        print(exchange.get_currency_state("GRT"))
        time.sleep(1)

import Synapsis


def price_event(price, product_id):
    # Run this every "hour"
    interface = strategy.Interface

    usd_amount = interface.get_account('USDT')['available']

    # Try to make our account value match 1/100 of the price.
    price = price/100

    delta = price-usd_amount
    if delta > 10:
        strategy.Interface.market_order(product_id, 'sell', delta)
    if delta < -10:
        strategy.Interface.market_order(product_id, 'buy', -1*delta)


if __name__ == "__main__":
    """
    Authenticate
    """
    print("Authenticating...")
    # Create an authenticated coinbase pro object
    coinbase_pro = Synapsis.Binance()

    # Create a strategy object
    strategy = Synapsis.Strategy(coinbase_pro)

    """
    Backtest
    """
    print("Backtesting...")
    # Add the function to the strategy class
    strategy.add_price_event(price_event, 'BTC-USDT', resolution='1m')

    # The backtest function will now turn our strategy class into a class that can be backtested
    print(strategy.backtest(to='1w'))

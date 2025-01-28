from Synapsis.strategy.order import Order
import Synapsis
from Synapsis.strategy.strategy_base import Strategy


def golden_cross(price, currency_pair, **kwargs):
    # we give you an assortment of values 
    # as well as access to the underlying strategy or interface
    portfolio_value = kwargs['portfolio_value']
    resolution = kwargs['resolution'] # get the resolution that this price event is stored at
    variables = kwargs['variables'] # each price event has it's own local variable state


    historical_prices = Synapsis.historical(currency_pair, 50, resolution=resolution)
    sma50 = Synapsis.analysis.calculate_sma(historical_prices, window=50)[-1] # last 50 day sma value is the value we want
    if price > sma50 and not variables['open_order']:
        variables['open_order'] = True
        return Order(currency_pair, 'market', 'buy', portfolio_value * 0.25)
    elif price < sma50 and variables['open_order']: # only sell if there's an open position
        variables['open_order'] = False
        return Order(currency_pair, 'market', 'sell', portfolio_value * 0.25)

def rsi(price, currency_pair, **kwargs):
    portfolio_value = kwargs['portfolio_value']
    resolution = kwargs['resolution']
    variables = kwargs['variables']
    
    historical_prices = Synapsis.historical(currency_pair, 50)
    historical_prices = Synapsis.historical(currency_pair, 50, resolution=resolution)
    rsi = Synapsis.analysis.calculate_rsi(historical_prices, window=10)[-1] # last 50 day sma value is the value we want
    if rsi < 30 and not variables['open_order']:
        variables['open_order'] = True
        return Order(currency_pair, 'market', 'buy', portfolio_value * 0.35)
    elif rsi > 70 and variables['open_order']: # only sell if there's an open position
        variables['open_order'] = False
        return Order(currency_pair, 'market', 'buy', portfolio_value * 0.35)


if __name__ == "__main__":
    coinbase_pro = Synapsis.Coinbase_Pro()
    coinbase_strategy = Strategy(coinbase_pro)

    coinbase_strategy.add_price_event(golden_cross, currency_pair='BTC-USD', resolution='15m')
    coinbase_strategy.add_price_event(rsi, currency_pair='XLM-USD', resolution='15m')
    coinbase_strategy.add_price_event(golden_cross, currency_pair='COMP-USD', resolution='30m')
    coinbase_strategy.add_price_event(rsi, currency_pair='COMP-USD', resolution='15m')

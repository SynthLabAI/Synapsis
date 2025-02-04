from synapsis.frameworks import strategy
import synapsis
from synapsis.utils import trunc



def price_event(price, symbol, state: synapsis.StrategyState):
    """ This function will give an updated price every 15 seconds from our definition below """
    state.variables['history'].append(price)
    rsi = synapsis.indicators.rsi(state.variables['history'])
    if rsi[-1] < 30 and not state.variables['owns_position']:
        # Dollar cost average buy
        buy = trunc(state.interface.cash * 0.5, 2)
        state.interface.market_order(symbol, side='buy', funds=buy)
        state.variables['owns_position'] = True
    elif rsi[-1] > 70 and state.variables['owns_position']:
        # Dollar cost average sell
        curr_value = trunc(state.interface.account[symbol].available * price, 2)
        state.interface.market_order(symbol, side='sell', funds=curr_value)
        state.variables['owns_position'] = False

def init(symbol, state: synapsis.StrategyState):
    # Download price data to give context to the algo
    state.variables['history'] = state.interface.history(symbol, to=150, return_as='deque')['close']
    state.variables['owns_position'] = False


if __name__ == "__main__":
    # Authenticate coinbase pro strategy
    alpaca = synapsis.Alpaca()

    # Use our strategy helper on coinbase pro
    strategy = synapsis.Strategy(alpaca)

    # Run the price event function every time we check for a new price - by default that is 15 seconds
    strategy.add_price_event(price_event, symbol='AAPL', resolution='1d', init=init)
    strategy.add_price_event(price_event, symbol='MSFT', resolution='1d', init=init)

    # Start the strategy. This will begin each of the price event ticks
    # strategy.start()
    # Or backtest using this
    results = strategy.backtest(to='1y', initial_values={'USD': 100})
    print(results)

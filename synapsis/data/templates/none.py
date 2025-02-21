import synapsis

if __name__ == "__main__":
    exchange = synapsis.EXCHANGE_CLASS()
    strategy = synapsis.Strategy(exchange)

    if synapsis.is_deployed:
        strategy.start()
    else:
        strategy.backtest(to='1y', initial_values={'QUOTE_ASSET': 10000})

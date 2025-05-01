

<br />

<div align="center">
   <img style="margin: 0 auto; padding-bottom: 15px; padding-top: 30px" width=70%" src="https://github.com/user-attachments/assets/c3d1cdb1-2fac-454e-877e-5f3c906ace95">
</div>
<br />

<div align="center">
  <b>💨  Rapidly build and deploy quantitative models for stocks, crypto, and forex  🚀</b>
</div>
<br />

<p align="center">
    <a target="_blank" href="https://synthlabai.github.io/synapsis-docs/">View Docs</a>
    ·
    <a target="_blank" href="https://synthlabai.github.io/synapsis-docs/">Our Website</a>
    ·
    <a target="_blank" href="https://synapsis.substack.com">Join Our Newsletter</a>
    ·
    <a href="#quickstart">Getting Started</a>
  </p>

---

## Why Synapsis? 

Synapsis is a complete ecosystem for algorithmic traders, allowing anyone to build, monetize, and scale trading strategies across stocks, crypto, futures, and forex. With just a single line change, the same code can be backtested, paper traded, sandbox tested, or executed live. Build locally, then deploy, iterate, and collaborate using the Synapsis platform.

The Synapsis package is built for exceptional accuracy in both simulated and live environments, with engineering decisions focused on delivering highly realistic and reliable performance.

The synapsis package is designed to be **extremely precise** in both simulation and live trading. **The engineering considerations for highly accurate simulation are described [here](synapsis/BACKTESTING_ENGINEERING.md)**

Getting started is easy - just `pip install synapsis` and `synapsis init`.

Check out our [docs](https://synthlabai.github.io/synapsis-docs/).


---------

### Trade Stocks, Crypto, Futures, and Forex

```python
from synapsis import Alpaca, CoinbasePro

stocks = Alpaca()
crypto = CoinbasePro()
futures = BinanceFutures()

# Easily perform the same actions across exchanges & asset types
stocks.interface.market_order('AAPL', 'buy', 1)
crypto.interface.market_order('BTC-USD', 'buy', 1)
# Full futures feature set
futures.interface.get_hedge_mode()
```

### Backtest your trades, events, websockets, and custom data

```python
import synapsis
"""
This example shows how backtest over tweets
"""

class TwitterBot(synapsis.Model):
    def main(self, args):
        while self.has_data:
            self.backtester.value_account()
            self.sleep('1h')

    def event(self, type_: str, data: str):
        # Now check if it's a tweet about Tesla
        if 'tsla' in data.lower() or 'gme' in data.lower():
            # Buy, sell or evaluate your portfolio
            pass


if __name__ == "__main__":
    exchange = synapsis.Alpaca()
    model = TwitterBot(exchange)

    # Add the tweets json here
    model.backtester.add_custom_events(synapsis.data.JsonEventReader('./tweets.json'))
    # Now add some underlying prices at 1 month
    model.backtester.add_prices('TSLA', '1h', start_date='3/20/22', stop_date='4/15/22')

    # Backtest or run live
    print(model.backtest(args=None, initial_values={'USD': 10000}))

```

**Check out alternative data examples [here](https://synthlabai.github.io/synapsis-docs/examples/model-framework)**

#### Accurate Backtest Holdings

<div align="center">
    <a><img src="https://github.com/user-attachments/assets/4f87c4d7-ae72-4081-8768-ed5103bb899a" style="border-radius:10px"></a>
</div>


### Go Live in One Line

Seamlessly run your model live!

```python
# Just turn this
strategy.backtest(to='1y')
# Into this
strategy.start()
```

Dates, times, and scheduling adjust on the backend to make the experience instant.

## Quickstart

### Installation

1. First install Synapsis using `pip`. Synapsis is hosted on [PyPi](https://pypi.org/project/Synapsis/).

```bash
$ pip install synapsis
```

2. Next, just run:
```bash
$ synapsis init
```
This will initialize your working directory.

The command will create the files `keys.json`, `settings.json`, `backtest.json`, `synapsis.json` and an example script called `bot.py`.

If you don't want to use our `init` command, you can find the same files in the `examples` folder under [`settings.json`](https://github.com/Synapsis-Finance/Synapsis/blob/main/examples/settings.json) and [`keys_example.json`](https://github.com/Synapsis-Finance/Synapsis/blob/main/examples/keys_example.json)

3. From there, **insert your API keys** from your exchange into the generated `keys.json` file or take advantage of the CLI keys prompt.

More information can be found on our [docs](https://synthlabai.github.io/synapsis-docs)

### Directory format

The working directory format should have *at least* these files:
```
project/
   |-bot.py
   |-keys.json
   |-settings.json
```

#### Additional Info

Make sure you're using a supported version of python. The module is currently tested on these versions:

- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10

For more info, and ways to do more advanced things, check out our [getting started docs](https://docs.synapsis.finance).

## Supported Exchanges

| Exchange            | Live Trading | Websockets | Paper Trading | Backtesting |
| ------------------- |--------------| ---------- |--------------| ----------- |
| Coinbase Pro        | 🟢           | 🟢          | 🟢           | 🟢           |
| Binance             | 🟢           | 🟢          | 🟢           | 🟢           |
| Alpaca              | 🟢           | 🟢          | 🟢           | 🟢           |
| OANDA               | 🟢           |  | 🟢           | 🟢           |
| FTX                 | 🟢           | 🟢          | 🟢           | 🟢           |
| KuCoin              | 🟢           | 🟢        | 🟢           | 🟢           |
| Binance Futures | 🟢 | 🟢 | 🟢 | 🟢 |
| FTX Futures | 🟡 | 🟡 | 🟢 | 🟢 |
| Okx | 🟢 | 🟢 | 🟢 | 🟢 |
| Kraken              | 🟡           | 🟡          | 🟡           | 🟡           |
| Keyless Backtesting |              |            |              | 🟢           |
| TD Ameritrade       | 🔴           | 🔴          | 🔴           | 🔴           |
| Webull              | 🔴           | 🔴          | 🔴           | 🔴           |
| Robinhood           | 🔴           | 🔴          | 🔴           | 🔴           |


🟢  = working

🟡  = in development, some or most features are working

🔴  = planned but not yet in development

## RSI Example

We have a pre-built cookbook examples that implement strategies such as RSI, MACD, and the Golden Cross found in our [examples](https://docs.synapsis.finance/examples/golden-cross).

Other Info

### Subscribe to our news!
https://synapsis.substack.com/p/coming-soon

### Bugs

Please report any bugs or issues on the GitHub's Issues page.

### Disclaimer 

Trading is risky. We are not responsible for losses incurred using this software, software fitness for any particular purpose, or responsibility for any issues or bugs.
This is free software.

### Contributing

If you would like to support the project, pull requests are welcome.

### Licensing 

**Synapsis** is distributed under the [**LGPL License**](https://www.gnu.org/licenses/lgpl-3.0.en.html). See the [LICENSE](/LICENSE) for more details.

New updates every day 💪.

import synapsis

if __name__ == "__main__":
    exchanges = [
        synapsis.Alpaca(),
        synapsis.Binance(),
        synapsis.CoinbasePro(),
        synapsis.Kucoin(),
        synapsis.Oanda()
    ]

    for i in exchanges:
        try:
            orders = i.interface.get_open_orders()

            for order in orders:
                print(f"Canceling {order['id']} on {order['symbol']}")
                i.interface.cancel_order(order['symbol'], order['id'])
        except Exception as e:
            print(e)
            continue

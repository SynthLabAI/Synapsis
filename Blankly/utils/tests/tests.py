import Synapsis


if __name__ == "__main__":
    print("Hello world")

    interface = Synapsis.Coinbase_Pro().get_interface()

    print(interface.get_fees())

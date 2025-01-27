"""
    Unit test class to ensure that each exchange gives the same result with the same types.
    Copyright (C) 2021  Emerson Dove

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import Synapsis
import unittest


def compare_dictionaries(dict1, dict2) -> bool:
    """
    Compare two output dictionaries to check if they have the same keys (excluding "exchange_specific")
    Args:
        dict1 (dict): First dictionary to compare
        dict2 (dict): Second dictionary to compare
    Returns:
        bool: Are the non specific tags the same?
    """
    if "exchange_specific" not in dict1:
        raise KeyError("Exchange specific tag not in: " + str(dict1))

    if "exchange_specific" not in dict2:
        raise KeyError("Exchange specific tag not in: " + str(dict2))

    # Safely remove keys now
    del dict1["exchange_specific"]
    del dict2["exchange_specific"]

    valid_keys = []

    for key, value in dict1.items():
        # Check to make sure that key is in the other dictionary
        if key in dict2:
            # Now are they the same type
            if not isinstance(dict2[key], type(value)):
                # Issue detected
                print("Type of key " + dict1[key] + " in dict1 is " + str(type(dict1[key])) +
                      ", but is " + str(type(dict2[key])) + " in dict2.")
                return False
            else:
                valid_keys.append(key)
        else:
            # Issue detected
            print(key + " found in dict1 but not in " + str(dict2))
            return False

    # Delete these keys so we can check for differences
    for i in valid_keys:
        del dict1[i]
        del dict2[i]

    if dict1 == {} and dict2 == {}:
        return True
    else:
        print("Differing keys:")
        print(dict1)
        print(dict2)
        return False


class InterfaceHomogeneity(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.Coinbase_Pro = Synapsis.Coinbase_Pro(portfolio_name="Sandbox Portfolio")
        cls.Coinbase_Pro_Interface = cls.Coinbase_Pro.get_interface()

        cls.Binance = Synapsis.Binance(portfolio_name="Spot Test Key")
        cls.Binance_Interface = cls.Binance.get_interface()

    def test_get_products(self):
        cbp_products = self.Coinbase_Pro_Interface.get_products()
        binance_products = self.Binance_Interface.get_products()

        # TODO this could compare every key against every other key
        self.assertTrue(compare_dictionaries(cbp_products[0], binance_products[0]))

    def test_get_account(self):
        cbp_products = self.Coinbase_Pro_Interface.get_products()
        binance_products = self.Binance_Interface.get_products()

        # TODO this could compare every key against every other key
        self.assertTrue(compare_dictionaries(cbp_products[0], binance_products[0]))

    def test_market_order(self):
        binance_status = self.Binance_Interface.get_paper_trading_status()
        coinbase_pro_status = self.Binance_Interface.get_paper_trading_status()

        self.assertTrue(binance_status)
        self.assertTrue(coinbase_pro_status)

        if binance_status and coinbase_pro_status:
            pass
            # buy = self.Binance_Interface.market_order('BTC-USD', 'buy', 20)
            # sell = self.Binance_Interface.market_order('BTC-USD', 'sell', 20)
            #
            # self.assertEqual(buy.get_type(), 'market')
            # self.assertLess(buy.get_funds(), 20)
            #
            # self.assertEqual(buy.get_side(), 'buy')
            #
            # # Finally, check that the responses are homogenized
            # self.assertTrue(compare_dictionaries(buy.get_response(), sell.get_response()))

            # self.Coinbase_Pro_Interface.market_order('BTC-USD', 'buy', 20)
        else:
            print("Either binance or coinbase pro not in paper trading mode. Is one in sandbox?")


"""
    Stop-limit Order
    Copyright (C) 2022 Matias Kotlik

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
from synapsis.exchanges.orders.futures.futures_order import FuturesOrder


class FuturesStopLimitOrder(FuturesOrder):
    needed = {
        *FuturesOrder.needed,
        ['time_in_force', str],
        ['stop_price', str],
    }

    def __init__(self, response, order, interface):
        super().__init__(response, order, interface)

    def get_time_in_force(self) -> str:
        return self.response['time_in_force']

    def get_stop_price(self) -> float:
        return self.response['stop_price']

    def __str__(self):
        return super().__str__() + f"""Stop Limit Order Parameters:
Stop Price: {self.get_stop_price()}
Time In Force: {self.get_time_in_force()}"""

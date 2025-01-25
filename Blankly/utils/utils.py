"""
    Utils file for assisting with trades or market analysis.
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

import datetime as DT
import dateutil.parser as DP
import json
import numpy
import warnings
import time_builder

from sklearn.linear_model import LinearRegression


# def printJSON(jsonObject):
#     """
#     Json pretty printer for show arguments
#     """
#     print(pretty_print_JSON(jsonObject))

# Recursively check if the user has all the preferences, inform when defaults are missing
def __compare_dicts(default_settings, user_settings):
    for k, v in default_settings.items():
        if isinstance(v, dict):
            if k in user_settings:
                __compare_dicts(v, user_settings[k])
            else:
                if not repress_preferences_warning:
                    warning_string = "\"" + str(k) + "\" not specified in preferences, defaulting to: \"" + str(v) + \
                                     "\""
                    warnings.warn(warning_string)
                user_settings[k] = v
        else:
            if k in user_settings:
                continue
            else:
                if not repress_preferences_warning:
                    warning_string = "\"" + str(k) + "\" not specified in preferences, defaulting to: \"" + str(v) + \
                                     "\""
                    warnings.warn(warning_string)
                user_settings[k] = v
    return user_settings


repress_preferences_warning = False

default_settings = {
    "settings": {
        "account_update_time": 5000,
        "paper_trade": True,
        "binance_tld": "us",
        "orderbook_buffer_size": 100000,
        "ticker_buffer_size": 10000
    }
}


def load_user_preferences(override_path=None):
    try:
        if override_path is None:
            f = open("Settings.json", )
            preferences = json.load(f)
        else:
            f = open(override_path, )
            preferences = json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError("Make sure a Settings.json file is placed in the same folder as the project "
                                "working directory!")
    preferences = __compare_dicts(default_settings, preferences)
    global repress_preferences_warning
    repress_preferences_warning = True
    return preferences


def pretty_print_JSON(json_object):
    """
    Json pretty printer for general string usage
    """
    out = json.dumps(json_object, indent=2)
    print(out)
    return out


def epoch_from_ISO8601(ISO8601):
    return DP.parse(ISO8601).timestamp()


def ISO8601_from_epoch(epoch):
    return DT.datetime.utcfromtimestamp(epoch).isoformat() + 'Z'


def get_price_derivative(ticker, point_number):
    """
    Performs regression n points back
    """
    feed = numpy.array(ticker.get_ticker_feed()).reshape(-1, 1)
    times = numpy.array(ticker.get_time_feed()).reshape(-1, 1)
    if point_number > len(feed):
        point_number = len(feed)

    feed = feed[-point_number:]
    times = times[-point_number:]
    prices = []
    for i in range(point_number):
        prices.append(feed[i][0]["price"])
    prices = numpy.array(prices).reshape(-1, 1)

    regressor = LinearRegression()
    regressor.fit(times, prices)
    regressor.predict(times)
    return regressor.coef_[0][0]


def fit_parabola(ticker, point_number):
    """
    Fit simple parabola
    """
    feed = ticker.get_ticker_feed()
    times = ticker.get_time_feed()
    if point_number > len(feed):
        point_number = len(feed)

    feed = feed[-point_number:]
    times = times[-point_number:]
    prices = []
    for i in range(point_number):
        prices.append(float(feed[i]["price"]))
        times[i] = float(times[i])

    # Pull the times back to x=0 so we can know what happens next
    latest_time = times[-1]
    for i in range(len(prices)):
        times[i] = times[i] - latest_time

    return numpy.polyfit(times, prices, 2, full=True)


def to_synapsis_coin_id(coin_id, exchange, base_currency):
    if exchange == "binance":
        index = int(coin_id.find(base_currency))
        coin_id = coin_id[0:index]
        return coin_id + "-" + base_currency
    if exchange == "coinbase_pro":
        return coin_id


def to_exchange_coin_id(synapsis_coin_id, exchange):
    if exchange == "binance":
        return synapsis_coin_id.replace('-', '')
    if exchange == "coinbase_pro":
        return synapsis_coin_id


def get_base_currency(synapsis_coin_id):
    # Gets the BTC of the BTC-USD
    return synapsis_coin_id.split('-')[0]


def get_quote_currency(synapsis_coin_id):
    # Gets the USD of the BTC-USD
    return synapsis_coin_id.split('-')[1]


def __time_interval_to_seconds(interval_string):
    """
    Extract the number of seconds in an interval string
    """
    # Extract intervals
    magnitude = int(interval_string[:-1])
    unit = interval_string[-1]

    # Switch units
    base_unit = None
    if unit == "m":
        base_unit = time_builder.build_minute()
    elif unit == "h":
        base_unit = time_builder.build_hour()
    elif unit == "d":
        base_unit = time_builder.build_day()
    elif unit == "w":
        base_unit = time_builder.build_week()
    elif unit == "M":
        base_unit = time_builder.build_month()

    # Scale by the magnitude
    return base_unit * magnitude


def scheduler(time):
    """
    Wrapper for functions that run at a set interval
    Args:
        time: int of delay between calls in seconds, or a string that takes units m, h, d w, M (minute, hour, day, week,
        month) and any magnitude - such as "4m" or "6h"
    """
    if isinstance(time, str):
        time = __time_interval_to_seconds(time)
    elif isinstance(time, int):
        pass


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

import synapsis

import datetime
import json
import sys
from datetime import datetime as dt, timezone
from math import ceil, trunc as math_trunc
from typing import Callable, Union
import re

import dateutil.parser as dp
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
from sklearn.linear_model import LinearRegression

from synapsis.utils.time_builder import time_interval_to_seconds

def is_in_list( val, allowable, case_sensitive : bool = False) -> bool:
    """
    Check if provided value is in the allowable list
    
    Args:
        val : value to check. Can be of any type
        allowable: list (or single element) to compare the val field to
        case_sensitive: boolean flag for use when comparing strings
    """

    # Force any single element allowable args to be a list
    if is_list(allowable) == False:
        allowable = [allowable]

    # If the results are not case sensitive, force comparison
    # on lower-case, so the user does not get an error from using caps
    if is_string(val) and not case_sensitive:
        val = val.lower()

    return val in allowable

def is_bool(val) -> bool:
    """
    Check if the provided argument is a boolean type
    """
    return isinstance(val, bool)

def is_positive( val ) -> bool:
    """
    Check if the provided argument is numeric and positive
    """
    return is_num(val) and val >= 0   

def is_string(val) -> bool:
    """
    Check if the provided argument is a string
    """
    return isinstance(val, str)

def is_num( val ) -> bool:
    """
    Check if the provided argument is real and an int or float
    """
    return np.isreal(val) & isinstance(val,(int, float))

def is_timeframe(val : str, allowable : list[str]) -> bool:
    """
    Check if the provided val argument is in the list of allowable args

    Args:
        val : string to evaluate
        allowable: list of timeframe suffixes ex: ["d", "m", "y"]
    """
    if not is_string(val):
        return False

    magnitude = int(val[:-1])
    base = val[-1]
    return is_positive(magnitude) and is_in_list(base, allowable)

def in_range( val , allowable_range : tuple, inclusive : bool = True ) -> bool:
    """
    Check if the provided val is within the specified range

    Args:
        val : int or float to check
        allowable_range : tuple specifying the min and max value
        inclusive : boolean flag to specify if the value can be equal to
            the provide min and max range. Default of True means if the value
            is equal to the min or max, the function returns True
    """
    max_val = max(allowable_range)
    min_val = min(allowable_range)
    
    if not is_num(val):
        return False

    if inclusive:
        does_pass = min_val <= val and val <= max_val
    else:
        does_pass = min_val < val and val < max_val

    return does_pass 

def is_list(val) -> bool:
    """
    Check if the provided argument is a list
    """
    return isinstance(val, list)

def let_pass(vals) -> bool:
    """
    Return true, regardless of the provided argument
    """
    return True
    
def are_valid_elements(vals : list, element_constraint : Callable) -> bool:
    """
    Check if the elements of a list conform to the provided constraint

    Args:
        vals : list of values to iterate through and check
        element_constraint : function reference used to check each element of the list
    """
    does_pass = is_list(vals)
    for val in vals:
        does_pass &= element_constraint(val)
    
    return does_pass

def is_valid_phone_number(val):
    """
    Check if the provided argument is a valid phone number
    """
    # Regular Expression source, https://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number
    REG_EX = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    try:
        re.fullmatch(REG_EX, val)
    except:
        return False

    return True

def is_valid_email(val):
    """
    Check if the provided argument is a valid email address
    """
    # Regular Expression soruce https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    REG_EX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    try:
        re.fullmatch(REG_EX, val)
    except:
        return False

    return True
    
        
class User_Input_Parser():

    def __init__(self, default_val, logic_check : Callable, logic_check_args : dict = None):
        """
        Create a new User Input Checker to ensure inputs from the user are valid.
        
        Args:
            default_val : If there is an error with the user's input, this is the value the field will default to
            logic_check : function reference that will be used to validate the user's input
            logic_check_args : dictionary of arguments to be passed to the logic_check function. Dictionary
                keys must match logic_check function keyword arguments.
        """
        self.__default_arg                  = default_val
        self.__check_callback   : Callable  = logic_check
        self.__callback_args    : dict      = logic_check_args
        self.__warning_str      : str       = ""
        self.__user_arg                     = None
        self.__valid            : bool      = None

    @property
    def default(self):
        """
        Get the default argument provided by the user
        """
        return self.__default_arg
    
    @property
    def valid(self) -> bool:
        """
        Get the boolean flag indicating if the user's input was valid.
        Note, this field is None until is_valid() is called
        """
        return self.__valid

    @property
    def user_arg(self):
        """
        Get the original argument provided by the user
        """
        return self.__user_arg

    @property
    def warning_str(self) -> str:
        """
        Get the warning string that is constructed when a user's input is invalid
        """
        return self.__warning_str

    def is_valid(self, user_arg) -> bool:   
        """
        Take the provided user_arg and run it through the logic_check function
        """

        # Save the provided user arg incase it is needed for error messages
        self.__user_arg = user_arg

        # Check if a dictionary of arguments was provided and add it to the call
        if self.__callback_args is None:
            user_input_valid = self.__check_callback(user_arg)
        else:
            user_input_valid = self.__check_callback(user_arg, **self.__callback_args)

        if user_input_valid:
            self.__valid = True

        # Create warning message 
        else:

            warning_string =  [f"Provided value of \'{user_arg}\' did not meet the constraints enforced by: {self.__check_callback.__name__}(). "]
            warning_string += [f"Overwriting user-provided value with the default value: \'{self.default}\' \n"]
        
            if self.__callback_args is not None:
                warning_string += ["\t"*3 + "Arguments passed to constraint function: \n"]
                warning_string += ["\t"*4 + f"\t - {k} : {v.__name__ if isinstance(v, Callable) else v} \n" for k, v in self.__callback_args.items()]
            
            # Join the lists of messages together and assign
            self.__warning_str = "".join(warning_string)
            self.__valid = False

        return self.valid


# Copy of settings to compare defaults vs overrides
default_general_settings = {
    "settings": {
        "account_update_time"       : User_Input_Parser(5000, in_range, {"allowable_range" : (1000,10000)}),
        "use_sandbox"               : User_Input_Parser(False, is_bool),
        "use_sandbox_websockets"    : User_Input_Parser(False, is_bool),
        "websocket_buffer_size"     : User_Input_Parser(10000, in_range, {"allowable_range" : (0,10000)}),
        "test_connectivity_on_auth" : User_Input_Parser(True, is_bool),

        "coinbase_pro": {
            "cash"  : User_Input_Parser("USD", is_in_list, {"allowable" : "USD", "case_sensitive" : True})
        },
        "binance": {
            "cash"          : User_Input_Parser("USDT",is_in_list, {"allowable" : "USDT", "case_sensitive" : True}),
            "binance_tld"   : User_Input_Parser("us", is_in_list, {"allowable" : "us"})
        },
        "alpaca": {
            "websocket_stream"  : User_Input_Parser("iex", is_in_list, {"allowable" : "iex"}),
            "cash"              : User_Input_Parser("USD", is_in_list, {"allowable" : "USD", "case_sensitive" : True})
        }
    }
}

default_backtest_settings = {
    "price_data": {
        "assets": User_Input_Parser([],are_valid_elements, {"element_constraint" : is_string})
    },
    "settings": {
        "use_price"                     : User_Input_Parser("close", is_in_list, {"allowable" : ["close", "open", "high", "low"]}),
        "smooth_prices"                 : User_Input_Parser(False, is_bool),
        "GUI_output"                    : User_Input_Parser(True, is_bool),
        "show_tickers_with_zero_delta"  : User_Input_Parser(False, is_bool),
        "save_initial_account_value"    : User_Input_Parser(True, is_bool),
        "show_progress_during_backtest" : User_Input_Parser(True, is_bool),

        "cache_location" : User_Input_Parser("./price_caches", is_string),

        "continuous_caching"                : User_Input_Parser(True, is_bool),
        "resample_account_value_for_metrics": User_Input_Parser("1d", is_timeframe, {"allowable" : ["s", "m", "h", "d", "w", "M","y", "D", "c", "l"]}),      
        "quote_account_value_in"            : User_Input_Parser("USD", is_in_list, {"allowable" : "USD", "case_sensitive" : True}),
        "ignore_user_exceptions"            : User_Input_Parser(False, is_bool),
        "risk_free_return_rate"             : User_Input_Parser(0.0, in_range, {"allowable_range" : (0,0.1)})
    }
}

default_notify_settings = {
  "email": {
    "port"          : User_Input_Parser(465, is_in_list, {"allowable" :[25, 2525, 587, 465, 25, 2526] }),
    "smtp_server"   : User_Input_Parser("smtp.website.com", is_string), # Assuming any errors will get caught on connection
    "sender_email"  : User_Input_Parser("email_attached_to_smtp_account@web.com", is_valid_email),
    "receiver_email": User_Input_Parser("email_to_send_to@web.com", is_valid_email),
    "password"      : User_Input_Parser("my_password", is_string)
  },
  "text": {
    "phone_number"  : User_Input_Parser("1234567683", is_valid_phone_number),
    "provider"      : User_Input_Parser("verizon", is_in_list, {"allowable" : ["verizon", "att", "boost", "cricket", "sprint", "t_mobile", "us_cellular", "virgin_mobile"]})
  }
}


def load_json_file(override_path=None):
    f = open(override_path, )
    json_file = json.load(f)
    f.close()
    return json_file


class __SynapsisSettings:
    def __init__(self, default_path: str, default_settings: dict, not_found_err: str):
        """
        Create a class that can manage caching for loading and writing to user preferences with a low overhead.

        This can dramatically accelerate instantiation of new interfaces or other objects

        Args:
            default_path: The default path to look for settings - such as ./settings.json
            default_settings: The default settings in which to compare the loaded settings to. This helps the user
             learn if they're missing important settings and avoids keyerrors later on
            not_found_err: A string that is shown if the file they specify is not found
        """
        self.__settings_cache = {}
        self.__default_path = default_path
        self.__default_settings = default_settings
        self.__not_found_err = not_found_err

    # Recursively check if the user has all the preferences, inform when defaults are missing
    def __compare_dicts(self, default_settings, user_settings):
        for k, v in default_settings.items():
            if isinstance(v, dict):
                if k in user_settings:
                    self.__compare_dicts(v, user_settings[k])
                else:
                    warning_string = "\"" + str(k) + "\" not specified in preferences, defaulting to: \"" + str(v) + \
                                     "\""
                    info_print(warning_string)
                    user_settings[k] = v.default
            else:

                # V is an instance of User_Input_Checker 
                v : User_Input_Parser

                if k in user_settings:
                    
                    # Check if the user's input is valid
                    if v.is_valid(user_settings[k]):
                        continue
                    
                    else:
                        warning_string = [f"User-provided value for key \'{k}\' is invalid: "]
                        warning_string += v.warning_str
                        info_print("".join(warning_string))
                        user_settings[k] = v.default


                else:
                    warning_string = "\"" + str(k) + "\" not specified in preferences, defaulting to: \"" + str(v.default) + \
                                     "\""
                    info_print(warning_string)
                    user_settings[k] = v.default
        return user_settings

    def load(self, override_path=None) -> dict:
        # Make overrides sticky by changing how the default is set. This is cool because the user can put settings in
        # obscure locations and then continue to load from them
        if override_path is not None:
            self.__default_path = override_path

        if self.__default_path not in self.__settings_cache:
            try:
                preferences = load_json_file(self.__default_path)
            except FileNotFoundError:
                raise FileNotFoundError(self.__not_found_err)
            preferences = self.__compare_dicts(self.__default_settings, preferences)
            self.__settings_cache[self.__default_path] = preferences
            return preferences
        else:
            return self.__settings_cache[self.__default_path]

    def write(self, json_information: dict, override_path: str = None):
        # In this case on writes it doesn't change the default path if its overridden globally
        if override_path is None:
            self.__settings_cache[self.__default_path] = json_information
            f = open(self.__default_path, "w")
        else:
            self.__settings_cache[override_path] = json_information
            f = open(override_path, "w")
        f.write(json.dumps(json_information, indent=2))


general_settings = __SynapsisSettings('./settings.json', default_general_settings,
                                     "Make sure a settings.json file is placed in the same folder as the project "
                                     "working directory!")

backtest_settings = __SynapsisSettings('./backtest.json', default_backtest_settings,
                                      "To perform a backtest, make sure a backtest.json file is placed in the same "
                                      "folder as the project working directory!")

notify_settings = __SynapsisSettings('./notify.json', default_notify_settings,
                                    "To send emails locally, make sure a notify.json file is placed in the same folder "
                                    "as the project working directory. This is not necessary when deployed live on "
                                    "synapsis cloud.")


def load_user_preferences(override_path=None) -> dict:
    return general_settings.load(override_path)


def load_backtest_preferences(override_path=None) -> dict:
    return backtest_settings.load(override_path)


def write_backtest_preferences(json_file, override_path=None):
    backtest_settings.write(json_file, override_path)


def load_notify_preferences(override_path=None) -> dict:
    return notify_settings.load(override_path)


def pretty_print_JSON(json_object, actually_print=True):
    """
    Json pretty printer for general string usage
    """
    out = json.dumps(json_object, indent=2)
    if actually_print:
        print(out)
    return out


def epoch_from_ISO8601(ISO8601) -> float:
    return dp.parse(ISO8601).timestamp()


def convert_input_to_epoch(value: Union[str, dt]) -> float:
    if isinstance(value, str):
        return epoch_from_ISO8601(value)
    elif isinstance(value, dt):
        return value.timestamp()
    elif isinstance(value, float):
        return value
    raise ValueError("Incorrect value input given, expected string or value but got: {}".format(type(value)))


def ISO8601_from_epoch(epoch) -> str:
    return dt.utcfromtimestamp(epoch).isoformat() + 'Z'


def get_price_derivative(ticker, point_number):
    """
    Performs regression n points back
    """
    feed = np.array(ticker.get_ticker_feed()).reshape(-1, 1)
    times = np.array(ticker.get_time_feed()).reshape(-1, 1)
    if point_number > len(feed):
        point_number = len(feed)

    feed = feed[-point_number:]
    times = times[-point_number:]
    prices = []
    for i in range(point_number):
        prices.append(feed[i][0]["price"])
    prices = np.array(prices).reshape(-1, 1)

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

    return np.polyfit(times, prices, 2, full=True)


def to_synapsis_symbol(symbol, exchange, quote_guess=None) -> str:
    if exchange == "binance":
        if quote_guess is not None:
            index = int(symbol.find(quote_guess))
            symbol = symbol[0:index]
            return symbol + "-" + quote_guess
        else:
            # Try your best to try to parse anyway
            quotes = ['BNB', 'BTC', 'TRX', 'XRP', 'ETH', 'USDT', 'BUSD', 'AUD', 'BRL', 'EUR', 'GBP', 'RUB',
                      'TRY', 'TUSD', 'USDC', 'PAX', 'BIDR', 'DAI', 'IDRT', 'UAH', 'NGN', 'VAI', 'BVND']
            for i in quotes:
                if __check_ending(symbol, i):
                    return to_synapsis_symbol(symbol, 'binance', quote_guess=i)
            raise LookupError("Unable to parse binance coin id of: " + str(symbol))

    if exchange == "coinbase_pro":
        return symbol


def __check_ending(full_string, checked_ending) -> bool:
    check_length = len(checked_ending)
    return checked_ending == full_string[-check_length:]


def to_exchange_symbol(synapsis_symbol, exchange):
    if exchange == "binance":
        return synapsis_symbol.replace('-', '')
    if exchange == "alpaca":
        return get_base_asset(synapsis_symbol)
    if exchange == "coinbase_pro":
        return synapsis_symbol


def get_base_asset(symbol):
    # Gets the BTC of the BTC-USD
    return symbol.split('-')[0]


def get_quote_asset(symbol):
    # Gets the USD of the BTC-USD
    split = symbol.split('-')
    if len(split) > 1:
        return split[1]
    else:
        # This could go wrong
        return 'USD'


def rename_to(keys_array, renaming_dictionary):
    """
    Args:
        keys_array: A two dimensional array that contains information on which keys are changed:
            keys_array = [
                ["key1", "new name"],
                ["id", "user_id"],
                ["frankie", "gerald"],
            ]
        renaming_dictionary: Dictionary to perform the renaming on
    """
    mutated_dictionary = {**renaming_dictionary}
    if "exchange_specific" not in mutated_dictionary:
        mutated_dictionary["exchange_specific"] = {}

    for i in keys_array:
        if i[1] in renaming_dictionary:
            # If we're here this key has already been defined, push it to the specific
            mutated_dictionary["exchange_specific"][i[1]] = renaming_dictionary[i[1]]
            # Then continue with adding the key that we were going to add anyway
        mutated_dictionary[i[1]] = renaming_dictionary[(i[0])]
        del mutated_dictionary[i[0]]
    return mutated_dictionary


# Non-recursive check
def isolate_specific(needed, compare_dictionary):
    """
    This is the parsing algorithm used to homogenize the dictionaries
    """
    # Make a copy of the dictionary so we don't modify it if you loop over
    compare_dictionary = {**compare_dictionary}
    # Create a row vector for the keys
    column = [column[0] for column in needed]  # ex: ['currency', 'available', 'hold']
    # Create an area to hold the specific data
    if 'exchange_specific' in compare_dictionary:
        exchange_specific = compare_dictionary['exchange_specific']
        del compare_dictionary['exchange_specific']
    else:
        exchange_specific = {}

    for k, v in compare_dictionary.items():
        required = False
        # Check if the value is one of the keys
        for index, val in enumerate(column):
            required = False
            # If it is, there is a state value for it
            if k == val:
                # Push type to value
                if v is not None:
                    compare_dictionary[k] = needed[index][1](v)
                else:
                    compare_dictionary[k] = v
                required = True
                break
        # Must not be found
        # Append non-necessary to the exchange specific dict
        # There has to be a way to do this without raising a flag value
        if not required:
            exchange_specific[k] = compare_dictionary[k]

    # Now we need to remove the keys that we appended to exchange_specific
    for k, v in exchange_specific.items():
        del compare_dictionary[k]

    # If there exists the exchange specific dict in the compare dictionary
    # This is done because after renaming, if there are naming conflicts they will already have been pushed here
    # Because we pulled out the naming conflicts dictionary we just just write this directly
    compare_dictionary["exchange_specific"] = exchange_specific

    return compare_dictionary


def convert_epochs(epoch):
    """
    If an epoch time is very long it means that it includes decimals - generally milliseconds. We like the decimal
    format because its unambiguous
    """
    # Hope nobody is fixing this on Friday, June 11, 2128 at 8:53:20 AM (GMT)
    while epoch > 5000000000:
        epoch = epoch / 10
    return epoch


def compare_dictionaries(dict1, dict2, force_exchange_specific=True) -> bool:
    """
    Compare two output dictionaries to check if they have the same keys (excluding "exchange_specific")
    Args:
        dict1 (dict): First dictionary to compare
        dict2 (dict): Second dictionary to compare
        force_exchange_specific (bool): Check if the the exchange_specific tag is in the dictionary
    Returns:
        bool: Are the non specific tags the same?
    """

    # Make copies of the dictionaries
    dict1 = {**dict1}
    dict2 = {**dict2}

    if force_exchange_specific:
        if "exchange_specific" not in dict1:
            raise KeyError("Exchange specific tag not in: " + str(dict1))

        if "exchange_specific" not in dict2:
            raise KeyError("Exchange specific tag not in: " + str(dict2))

        # Safely remove keys now
        del dict1["exchange_specific"]
        del dict2["exchange_specific"]
    else:
        # Remove the tag if its there anyway
        try:
            del dict1["exchange_specific"]
        except KeyError:
            pass
        try:
            del dict2["exchange_specific"]
        except KeyError:
            pass

    valid_keys = []

    for key, value in dict1.items():
        # Check to make sure that key is in the other dictionary
        if key in dict2:
            # Now are they the same type
            if not isinstance(dict2[key], type(value)):
                # Issue detected
                print("Type of key " + str(dict1[key]) + " in dict1 is " + str(type(dict1[key])) +
                      ", but is " + str(type(dict2[key])) + " in dict2.")
                return False
            else:
                # If it's a dictionary, go inside of it
                if isinstance(type(value), dict):
                    print("comparing:")
                    print(value)
                    print(dict2[key])
                    if not compare_dictionaries(value, dict2[key], force_exchange_specific=False):
                        return False

                valid_keys.append(key)
                # This code can more specifically compare the key pairs
                # if dict1[key] == dict2[key]:
                #     valid_keys.append(key)
                # else:
                #     print("Types of keys are the same, however " + str(dict1[key]) + " != " + str(dict2[key]) + ".")
                #     return False
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


def update_progress(progress):
    # From this great post: https://stackoverflow.com/a/15860757/8087739
    # update_progress() : Displays or updates a console progress bar
    # Accepts a float between 0 and 1. Any int will be converted to a float.
    # A value under 0 represents a 'halt'.
    # A value at 1 or bigger represents 100%
    bar_length = 10  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(bar_length * progress))
    text = "\rProgress: [{0}] {1}% {2}".format("#" * block + "-" * (bar_length - block), round(progress * 100, 2),
                                               status)
    sys.stdout.write(text)
    sys.stdout.flush()


def split_df(df, n):
    return df.groupby(np.arange(len(df)) // n)


def get_ohlcv(candles, n, from_zero: bool):
    if len(candles) < n:
        raise ValueError("Not enough candles provided, required at least {} candles, "
                         "but only received {}".format(n, len(candles)))
    new_candles = pd.DataFrame()
    df = split_df(candles, n)
    new_candles['high'] = df['high'].max().reset_index(drop=True)
    new_candles['low'] = df['low'].min().reset_index(drop=True)
    new_candles['volume'] = df['volume'].sum().reset_index(drop=True)
    new_candles['volume'] = new_candles['volume'].apply(lambda x: float(x))
    if from_zero:
        new_candles['close'] = candles['close'].iloc[0::n].reset_index(drop=True)
        new_candles['open'] = candles['open'].iloc[0::n].reset_index(drop=True)
        new_candles['time'] = candles['time'].iloc[0::n].reset_index(drop=True).astype('int64')
        new_candles['time'] = new_candles['time'].apply(lambda x: np.int64(x))
    else:
        new_candles['close'] = candles['close'].iloc[::n].reset_index(drop=True)
        new_candles['open'] = candles['open'].iloc[::n].reset_index(drop=True)
        new_candles['time'] = candles.index.to_series().iloc[::n].reset_index(drop=True)
        new_candles['time'] = new_candles['time'].apply(lambda x: np.int64(x.timestamp()))
    return new_candles


def aggregate_candles(history: pd.DataFrame, aggregation_size: int):
    """
    Aggregate history data (such as turn 1m data into 15m data)

    Args:
        history: A synapsis generated dataframe
        aggregation_size: How many rows of history to aggregate - ex: aggregation_size=15 on 1m data produces
         15m intervals
    """
    aggregated = pd.DataFrame()
    splits = split_df(history, aggregation_size)
    for i in splits:
        # Build candles from the split dataframes
        frame: dict = i[1].to_dict()
        try:
            tick = {
                'time': list(frame['time'].values())[0],
                'open': list(frame['open'].values())[0],
                'high': max(frame['high'].values()),
                'low': min(frame['low'].values()),
                'close': list(frame['close'].values())[-1],
                'volume': sum(frame['volume'].values()),
            }
        except IndexError:
            continue
        aggregated = aggregated.append(tick, ignore_index=True)
    return aggregated


def get_ohlcv_from_list(tick_list: list, last_price: float):
    """
    Created with the purpose of parsing ticker data into a viable OHLCV pattern. The

    Args:
        tick_list (list): List of data containing price ticks. Needs to be at least: [{'price': 343, 'size': 3.4}, ...]
            The data must also be ordered oldest to most recent at the end
        last_price (float): The last price in case there isn't any valid data
    """
    out = {
        'open': last_price,
        'high': last_price,
        'low': last_price,
        'close': last_price,
        'volume': 0
    }
    if len(tick_list) > 0:
        out['open'] = tick_list[0]['price']
        out['close'] = tick_list[-1]['price']

    for i in tick_list:
        out['volume'] = out['volume'] + i['size']

        if i['price'] > out['high']:
            out['high'] = i['price']
        elif i['price'] < out['low']:
            out['low'] = i['price']

    return out


def ceil_date(date, **kwargs):
    secs = datetime.timedelta(**kwargs).total_seconds()
    return dt.fromtimestamp(date.timestamp() + secs - date.timestamp() % secs)


OVERESTIMATE_CONSTANT = 1.5


def get_estimated_start_from_limit(limit, end_epoch, resolution_str, resolution_multiplier):

    nyse = mcal.get_calendar('NYSE')
    required_length = ceil(limit * OVERESTIMATE_CONSTANT)
    resolution = time_interval_to_seconds(resolution_str)

    if resolution == 60 and limit < (1440 / resolution_multiplier):
        return end_epoch - 4 * 86400  # worst case is three day weekend at 9:30am open

    if resolution == 3600 and limit < (24 / resolution_multiplier):
        return end_epoch - 4 * 86400  # worst case is three day weekend at 9:30am open

    temp_start = end_epoch - limit * resolution * resolution_multiplier
    end_date = dt.fromtimestamp(end_epoch, tz=timezone.utc)
    start_date = dt.fromtimestamp(temp_start, tz=timezone.utc)

    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    date_range = mcal.date_range(schedule, frequency='1D')

    count = 1
    while len(date_range) < required_length:
        temp_start -= 3600 * OVERESTIMATE_CONSTANT * count
        start_date = dt.fromtimestamp(temp_start)
        schedule = nyse.schedule(start_date=start_date, end_date=end_date)
        date_range = mcal.date_range(schedule, frequency='1D')
        count += 1

    return temp_start


class AttributeDict(dict):
    """
    This is adds functions to the dictionary class, no other modifications. This gives dictionaries abilities like:

    print(account.BTC) -> {'available': 1, 'hold': 0}

    account.BTC = "cool"
    print(account.BTC) -> cool

    Basically you can get and set attributes with a dot instead of [] - like dict.available rather than
     dict['available']
    """
    def __getattr__(self, attr):
        # Try catch is wrapped to support copying objects
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def format_with_new_line(original_string, *components):
    for i in components:
        original_string += str(i)

    original_string += '\n'

    return original_string


def trunc(number: float, decimals: int) -> float:
    """
    Truncate a number instead of rounding (ex: trunc(9.9999999, 2) == 9.99 instead of round(9.9999999, 2) == 10.0)

    Args:
        number (float): Number to truncate
        decimals (int): Number of decimals to keep: trunc(9.9999999, 2) == 9.99
    """
    stepper = 10.0 ** decimals
    return math_trunc(stepper * number) / stepper


def info_print(message):
    """
    This prints directly to stderr which allows a way to distinguish package info calls/errors from generic stdout

    Args:
        message: The message to print. INFO: will be prepended
    """
    print('INFO: ' + message, file=sys.stderr)


class Email:
    """
    Object wrapper for simplifying interaction with SMTP servers & the synapsis.reporter.email function.

    Alternatively a notify.json can be created which automatically integrates with synapsis.reporter.email()
    """
    def __init__(self, smtp_server: str, sender_email: str, password: str, port: int = 465):
        """
        Create the email wrapper:

        Args:
            smtp_server: The address of the smtp server
            sender_email: The email attached to the smtp account
            password: The password to log into SMTP
            port: SMTP port - sometimes will fail if not 465
        """
        self.__server = smtp_server
        self.__sender_email = sender_email
        self.__password = password
        self.__port = port

    def send(self, receiver_email: str, message: str):
        """
        Send an email to the receiver_email specified

        Args:
            receiver_email (str): The email that the message is sent to
            message (str): The body of the message
        """
        synapsis.reporter.email(email_str=message, smtp_server=self.__server, sender_email=self.__sender_email,
                               receiver_email=receiver_email, password=self.__password, port=self.__port)

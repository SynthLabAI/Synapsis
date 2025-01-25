"""
    Binance ticker class.
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

import websocket
from Synapsis.exchanges.IExchange_Ticker import IExchangeTicker
import collections
import json
import Synapsis
import threading
import time
import traceback


class Tickers(IExchangeTicker):
    def __init__(self, currency_id, log=None, WEBSOCKET_URL="wss://stream.binance.com:9443/ws"):
        """
        Create and initialize the ticker
        Args:
            currency_id: Currency to initialize on such as "BTC-USD"
            log: Fill this with a path to a log file that should be created
            WEBSOCKET_URL: Default websocket URL feed.
        """
        self.__id = currency_id

        # Initialize log file
        if log is not None:
            self.__log = True
            self.__filePath = log
            try:
                self.__file = open(log, 'xa')
                self.__file.write(
                    "time,system_time,price,open_24h,volume_24h,low_24h,high_24h,volume_30d,best_bid,best_ask,"
                    "last_size\n")
            except FileExistsError:
                self.__file = open(log, 'a')
        else:
            self.__log = False

        self.URL = WEBSOCKET_URL
        self.ws = None
        self.__response = None
        self.__most_recent_tick = None
        self.__most_recent_time = None
        self.__callbacks = []
        # This is created so that we know when a message has come back that we're waiting for
        self.__single_message = None

        # Reload preferences
        self.__preferences = Synapsis.utils.load_user_preferences()
        self.__ticker_feed = collections.deque(maxlen=self.__preferences["settings"]["ticker_buffer_size"])
        self.__time_feed = collections.deque(maxlen=self.__preferences["settings"]["ticker_buffer_size"])

        # Start the websocket
        self.start_websocket()

    def start_websocket(self):
        """
        Restart websocket if it was asked to stop.
        """
        if self.ws is None:
            self.ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                                             on_open=self.on_open,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close)
            thread = threading.Thread(target=self.read_websocket)
            thread.start()
        else:
            if self.ws.connected:
                print("Already running...")
                pass
            else:
                # Use recursion to restart, continue appending to time feed and ticker feed
                self.ws = None
                self.start_websocket()

    def read_websocket(self):
        # Main thread to sit here and run
        while True:
            self.ws.run_forever()

    def on_message(self, ws, message):
        message = json.loads(message)
        try:
            print(message['E'])
            self.__time_feed.append(message['E'])
            self.__ticker_feed.append(message)
            # Run callbacks on message
            for i in self.__callbacks:
                i(message)
        except KeyError:
            try:
                if message['result'] is None:
                    self.__response = message
            except KeyError:
                traceback.print_exc()

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        # request = """
        # {
        #     "method": "SUBSCRIBE",
        #     "params": [
        #         \"""" + self.__id + """t@trade"
        #     ],
        #     "id": 1
        # }
        # """
        # TODO make an overhaul to the front to specify trading pair because binance refuses to be normal
        request = """
                {
                    "method": "SUBSCRIBE",
                    "params": [
                        "btcusdt@trade"
                    ],
                    "id": 1
                }
                """
        ws.send(request)

    """ Logic to extract a single message when prompted """
    def __get_message(self, ws, message):
        self.__single_message = message

    def __get_single_message(self, message=None):
        # Save the current callback for later
        current_callback = self.ws.on_message

        # Switch out the callbacks and wait for response
        while self.__single_message is None:
            time.sleep(.1)
        response = self.__single_message

        # Clear this for the next run
        self.__single_message = None

        # Restore original callback
        self.ws.on_message = current_callback
        return response


    """ Required in manager """
    def is_websocket_open(self):
        return self.ws.connected

    def get_currency_id(self):
        return self.__id

    """ Required in manager """
    def append_callback(self, obj):
        self.__callbacks.append(obj)

    """ Define a variable each time so there is no array manipulation """
    """ Required in manager """
    def get_most_recent_tick(self):
        return self.__most_recent_tick

    """ Required in manager """
    def get_most_recent_time(self):
        return self.__most_recent_time

    """ Required in manager """
    def get_time_feed(self):
        return list(self.__time_feed)

    """ Parallel with time feed """
    """ Required in manager """
    def get_ticker_feed(self):
        return list(self.__ticker_feed)

    """ Required in manager """
    def get_response(self):
        return self.__response

    """ Required in manager """
    def close_websocket(self):
        if self.ws.connected:
            self.ws.close()
        else:
            print("Websocket for " + self.__id + " is already closed")

    """ Required in manager """
    def restart_ticker(self):
        self.start_websocket()


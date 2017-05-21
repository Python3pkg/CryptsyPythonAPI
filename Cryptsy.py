import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import time
import hmac
import hashlib


class Api:
    """ API wrapper for the Cryptsy API. """
    def __init__(self, key, secret):
        self.API_KEY = key
        self.SECRET = secret

    def _public_api_query(self, method, marketid=None):
        """ Call to the public api and return the loaded json. """
        request_url = 'http://pubapi.cryptsy.com/api.php?method=%s' % method
        if marketid is not None:
            request_url += '&marketid=%d' % marketid

        rv = urllib.request.urlopen(urllib.request.Request(request_url))
        return json.loads(rv.read())

    def _api_query(self, method, request_data={}):
        """ Call to the "private" api and return the loaded json. """
        request_data['method'] = method
        request_data['nonce'] = int(round(time.time() * 1000))
        post_data = urllib.parse.urlencode(request_data)

        signed_data = hmac.new(self.SECRET, post_data, hashlib.sha512)\
                          .hexdigest()
        headers = {
            'Sign': signed_data,
            'Key': self.API_KEY
        }

        rv = urllib.request.urlopen(urllib.request.Request('https://www.cryptsy.com/api',
                                             post_data,
                                             headers))

        return json.loads(rv.read())

    def market_data(self, marketid=None, v2=False):
        """ Get market data for all markets.

        Defaults to the old version of getmarketdata. Set v2 to True to use
        getmarketdatav2.
        """
        if v2 is True:
            return self._public_api_query("marketdatav2")
        if marketid is not None:
            return self._public_api_query("singlemarketdata", marketid=marketid)
        return self._public_api_query("marketdata")

    def order_book_data(self, marketid=None):
        """ Get orderbook data for all markets, or for a single one.

        :param marketid: If provided, API will only return orderbook data for
            this specific market.
        """
        if marketid is None:
            return self._public_api_query("orderdata")
        return self._public_api_query("singleorderdata", marketid=marketid)

    def info(self):
        """ Get some information about the server and your account.

        Resultset contains:

        balances_available  Array of currencies and the balances availalbe for each
        balances_hold   Array of currencies and the amounts currently on hold for open orders
        servertimestamp Current server timestamp
        servertimezone  Current timezone for the server
        serverdatetime  Current date/time on the server
        openordercount  Count of open orders on your account
        """
        return self._api_query('getinfo')

    def markets(self):
        """ Get a list of all active markets.

        Resultset contains:

        marketid    Integer value representing a market
        label   Name for this market, for example: AMC/BTC
        primary_currency_code   Primary currency code, for example: AMC
        primary_currency_name   Primary currency name, for example: AmericanCoin
        secondary_currency_code Secondary currency code, for example: BTC
        secondary_currency_name Secondary currency name, for example: BitCoin
        current_volume  24 hour trading volume in this market
        last_trade  Last trade price for this market
        high_trade  24 hour highest trade price in this market
        low_trade   24 hour lowest trade price in this market
        """
        return self._api_query('getmarkets')

    def my_transactions(self):
        """ Get all your deposits and withdrawals from your account.

        Resultset contains:

        currency    Name of currency account
        timestamp   The timestamp the activity posted
        datetime    The datetime the activity posted
        timezone    Server timezone
        type    Type of activity. (Deposit / Withdrawal)
        address Address to which the deposit posted or Withdrawal was sent
        amount  Amount of transaction
        """
        return self._api_query('mytransactions')

    def market_trades(self, marketid):
        """ Get the last 1000 trades for this market, ordered descending by
        date.

        Resultset contains:

        datetime    Server datetime trade occurred
        tradeprice  The price the trade occurred at
        quantity    Quantity traded
        total   Total value of trade (tradeprice * quantity)

        :param marketid: Market for which you are querying.
        """
        return self._api_query('markettrades', request_data={'marketid': marketid})

    def market_orders(self, marketid):
        """ Return currently open sell and buy orders.

        Resultset contains two arrays, one for sell orders, one for buy orders,
        containing the following fields:

        sellprice   If a sell order, price which order is selling at
        buyprice    If a buy order, price the order is buying at
        quantity    Quantity on order
        total   Total value of order (price * quantity)

        :param marketid: Market ID for which you are querying.
        """
        return self._api_query('marketorders',
                               request_data={'marketid': marketid})

    def my_trades(self, marketid=None, limit=200):
        """ Get all your trades for this market, ordered descending by date.

        Resultset contains:

        tradeid An integer identifier for this trade
        tradetype   Type of trade (Buy/Sell)
        datetime    Server datetime trade occurred
        tradeprice  The price the trade occurred at
        quantity    Quantity traded
        total   Total value of trade (tradeprice * quantity)

        :param marketid: Marketid for which you are querying.
        :param limit: Maximum number of results, defaults to 200.
        """
        if marketid is None:
            return self._api_query('allmytrades')
        return self._api_query('mytrades', request_data={'marketid': marketid,
                                                         'limit': limit})

    def my_orders(self, marketid=None):
        """ Get all your orders, or your orders for a specific market.

        Resultset contains:

        orderid Order ID for this order
        created Datetime the order was created
        ordertype   Type of order (Buy/Sell)
        price   The price per unit for this order
        quantity    Quantity for this order
        total   Total value of order (price * quantity)

        :param marketid: If provided, orders will be filtered by this marketid.
        """
        if marketid is None:
            return self._api_query('allmyorders')
        return self._api_query('myorders', request_data={'marketid': marketid})

    def depth(self, marketid):
        """ Get an array of buy and sell orders on the given market
        representing the market depth.

        :param marketid: A market ID.
        """
        return self._api_query('depth', request_data={'marketid': marketid})

    def _create_order(self, marketid, ordertype, quantity, price):
        """ Creates an order for buying or selling coins.

        It is preferable to buy and sell coins using the Api.buy and Api.sell
        methods.

        :param marketid: Market to buy from.
        :param ordertype: Either Buy or Sell.
        :param quantity: Number of coins to buy.
        :param price: At this price.
        :returns: A dict containing the orderid of the created order.
        """
        return self._api_query('createorder',
                               request_data={'marketid': marketid,
                                             'ordertype': ordertype,
                                             'quantity': quantity,
                                             'price': price})

    def buy(self, marketid, quantity, price):
        """ Buy a specified number of coins on the given market. """
        return self._create_order(marketid, 'Buy', quantity, price)

    def sell(self, marketid, quantity, price):
        """ Sell a specified number of coins on the given market. """
        return self._create_order(marketid, 'Sell', quantity, price)

    def cancel_order(self, orderid):
        """ Cancel a specific order.

        :param orderid: The ID of the order you want to cancel.
        :returns: A succescode if succesfull.
        """
        return self._api_query('cancelorder', request_data={'orderid': orderid})

    def cancel_all_market_orders(self, marketid):
        """ Cancel all currently pending orders for a specific market.

        :param marketid: Market ID for wich you would like to cancel orders.
        """
        return self._api_query('cancelmarketorders',
                              request_data={'marketid': marketid})

    def cancel_all_orders(self):
        """ Cancel all currently pending orders. """
        return self._api_query('cancelallorders')

    def calculate_fees(self, ordertype, quantity, price):
        """ Calculate fees that would be charged for the provided inputs.

        :param ordertype: Order type you are calculating for (Buy/Sell)
        :param quantity: Amount of units you are buying/selling
        :param price: Price per unit you are buying/selling at
        :returns: A dict containing the fee and the net total with fees.
        """
        return self._api_query('calculatefees',
                               request_data={'ordertype': ordertype,
                                             'quantity': quantity,
                                             'price': price})

    def generate_new_address(self, currencyid=None, currencycode=None):
        """ Generate a new address for a currency. Expects either a currencyid
        OR a currencycode (not both).

        :param currencyid: ID of a currency on Cryptsy.
        :param currencycode: Code of a currency on Cryptsy.
        :throws ValueError: Fails if neither of the parameters are given.
        :returns: A dict containing the newly generated address.
        """
        if currencyid is not None:
            req = {'currencyid': currencyid}
        elif currencycode is not None:
            req = {'currencycode': currencycode}
        else:
            raise ValueError('You should specify either a currencyid or a'
                             'currencycode')

        return self._api_query('generatenewaddress', request_data=req)

    def my_transfers(self):
        """ Array of all transfers into/out of your account sorted by requested
        datetime descending.

        Resultset contains:

        currency	Currency being transfered
        request_timestamp	Datetime the transfer was requested/initiated
        processed	Indicator if transfer has been processed (1) or not (0)
        processed_timestamp	Datetime of processed transfer
        from	Username sending transfer
        to	Username receiving transfer
        quantity	Quantity being transfered
        direction	Indicates if transfer is incoming or outgoing (in/out)
        """
        self._api_query('mytransfers');

    def wallet_status(self):
        """ Array of Wallet Statuses

        Resultset contains:

        currencyid	Integer value representing a currency
        name	Name for this currency, for example: Bitcoin
        code	Currency code, for example: BTC
        blockcount	Blockcount of currency hot wallet as of lastupdate time
        difficulty	Difficulty of currency hot wallet as of lastupdate time
        version	Version of currency hotwallet as of lastupdate time
        peercount	Connected peers of currency hot wallet as of lastupdate time
        hashrate	Network hashrate of currency hot wallet as of lastupdate time
        gitrepo	Git Repo URL for this currency
        withdrawalfee	Fee charged for withdrawals of this currency
        lastupdate	Datetime (EST) the hot wallet information was last updated
        """
        self._api_query('getwalletstatus')

    def make_withdrawal(self, address, amount):
        """ Make a withdrawal to a trusted withdrawal address.

        :param address: Pre-approved address for which you are withdrawing to.
        :param amount: Amount you are withdrawing, maximum of 8 decimals.
        """
        self._api_query('makewithdrawal',
                        request_data={
                            'address': address,
                            'amount': amount
                        })

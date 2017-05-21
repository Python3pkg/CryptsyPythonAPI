import pytest
import urllib.request, urllib.error, urllib.parse

from mock import Mock

from Cryptsy import Api


@pytest.fixture
def api():
    return Api('KEY', 'SECRET')


@pytest.fixture
def mock_urlopen(monkeypatch):
    def _mock_urlopen(request):
        """ Mock urllib to return the url so we can check if the url is
        constructed correctly. """
        class MockRequest:
            def read(self):
                return '{"url": "%s"}' % request._Request__original

        return MockRequest()

    monkeypatch.setattr(urllib2, 'urlopen', _mock_urlopen)


def test_cryptsy_init():
    """ The Cryptsy class constructor should accept the API Key and the Secret
    in the constructor and set it on the instance. """
    instance = Api('API Key', 'Secret')
    assert instance.API_KEY == 'API Key'
    assert instance.SECRET == 'Secret'


def test_method_should_be_added_in_the_url(mock_urlopen, api):
    rv = api._public_api_query('testmethod')
    assert rv['url'] == 'http://pubapi.cryptsy.com/api.php?method=testmethod'


def test_marketid_should_be_added_as_get_parameter(mock_urlopen, api):
    rv = api._public_api_query('testmethod', marketid=10)
    assert rv['url'] == 'http://pubapi.cryptsy.com/api.php?method=testmethod&marketid=10'


def test_create_order(api, api_query_mock):
    """ Api._create_order should pass the given values onto the api. """
    api._create_order(10, 'Buy', 100, 0.10)
    api_query_mock.assert_called_with('createorder',
                                      request_data={
                                          'marketid': 10,
                                          'ordertype': 'Buy',
                                          'quantity': 100,
                                          'price': 0.10
                                      })


@pytest.fixture
def mock_create_order(api):
    """ Mock the create order so we can check if the correct ordertype is
    used. """
    api._create_order = Mock()


def test_buy(mock_create_order, api):
    """ The buy method should call the _create_order method with the ordertyp
    as 'Buy'. """
    api.buy(26, 10, 0.0000001)
    api._create_order.assert_called_with(26, 'Buy', 10, 0.0000001)


def test_sell(mock_create_order, api):
    """ The sell method should call the _create_order method with the ordertyp
    as 'Sell'. """
    rv = api.sell(26, 10, 0.0000001)
    api._create_order.assert_called_with(26, 'Sell', 10, 0.0000001)


def test_generate_new_address_without_parameters(api):
    """ generate_new_address should raise a ValueError when no parameters are
    provided. """
    with pytest.raises(ValueError):
        api.generate_new_address()


@pytest.fixture
def api_query_mock(api):
    api._api_query = Mock()
    return api._api_query


@pytest.fixture
def public_api_query_mock(api):
    api._public_api_query = Mock()
    return api._public_api_query


def test_generate_new_address_currencycode(api, api_query_mock):
    """ Should add currencycode as request data if provided. """
    api.generate_new_address(currencycode=10)
    api_query_mock.assert_called_with('generatenewaddress', request_data={
        'currencycode': 10
    })


def test_generate_new_address_currencyid(api, api_query_mock):
    """ Should add currencyid as request data if provided. """
    api.generate_new_address(currencyid=10)
    api_query_mock.assert_called_with('generatenewaddress', request_data={
        'currencyid': 10
    })


def test_single_market_data(api, public_api_query_mock):
    """ Should call singlemarketdata if marketid is provided. """
    api.market_data(marketid=10)
    public_api_query_mock.assert_called_with('singlemarketdata', marketid=10)


def test_market_data_old(api, public_api_query_mock):
    """ Should use the old marketdata method if v2 is not set to True. """
    api.market_data()
    public_api_query_mock.assert_called_with('marketdata')


def test_market_data_v2(api, public_api_query_mock):
    """ Should use the old marketdata method if v2 is not set to True. """
    api.market_data(v2=True)
    public_api_query_mock.assert_called_with('marketdatav2')


def test_order_book_data_no_marketid(api, public_api_query_mock):
    """ Should call orderdata if no marketid is provided. """
    api.order_book_data()
    public_api_query_mock.assert_called_with('orderdata')


def test_order_book_data_with_marketid(api, public_api_query_mock):
    """ Should call singleorderdata if marketid is provided. """
    api.order_book_data(marketid=10)
    public_api_query_mock.assert_called_with('singleorderdata', marketid=10)


def test_info(api, api_query_mock):
    """ Should call getinfo. """
    api.info()
    api_query_mock.assert_called_with('getinfo')


def test_markets(api, api_query_mock):
    """ Should call getmarkets. """
    api.markets()
    api_query_mock.assert_called_with('getmarkets')


def test_my_transactions(api, api_query_mock):
    """ Should call mytransactions. """
    api.my_transactions()
    api_query_mock.assert_called_with('mytransactions')


def test_market_trades(api, api_query_mock):
    """ Should call markettrades with the provided marketid. """
    api.market_trades(marketid=10)
    api_query_mock.assert_called_with('markettrades',
                                      request_data={'marketid': 10})


def test_market_orders(api, api_query_mock):
    """ Should call mytransactions. """
    api.market_orders(marketid=10)
    api_query_mock.assert_called_with('marketorders',
                                      request_data={'marketid': 10})


def test_my_trades_no_marketid(api, api_query_mock):
    """ If no marketid is provided, it should call allmytrades. """
    api.my_trades()
    api_query_mock.assert_called_with('allmytrades')


def test_my_trades_with_marketid(api, api_query_mock):
    """ If a marketid is provided, it should call mytrades. """
    api.my_trades(marketid=10)
    api_query_mock.assert_called_with('mytrades',
                                      request_data={
                                            'marketid': 10,
                                            'limit': 200
                                      })


def test_my_trades_with_marketid_and_limit(api, api_query_mock):
    """ If limit is provided, use it.. """
    api.my_trades(marketid=10, limit=10)
    api_query_mock.assert_called_with('mytrades',
                                      request_data={
                                            'marketid': 10,
                                            'limit': 10
                                      })


def test_my_orders_no_marketid(api, api_query_mock):
    """ If no marketid is provided, it should call allmyorders. """
    api.my_orders()
    api_query_mock.assert_called_with('allmyorders')


def test_my_orders_with_marketid(api, api_query_mock):
    """ If a marketid is provided, it should call myorders. """
    api.my_orders(marketid=10)
    api_query_mock.assert_called_with('myorders',
                                      request_data={
                                        'marketid': 10,
                                      })


def test_depth(api, api_query_mock):
    """ Should call depth with given marketid. """
    api.depth(marketid=10)
    api_query_mock.assert_called_with('depth', request_data={'marketid': 10})


def test_cancel_order(api, api_query_mock):
    """ Should call cancelorders with given orderid. """
    api.cancel_order(orderid=10)
    api_query_mock.assert_called_with('cancelorder',
                                      request_data={'orderid': 10})


def test_cancel_all_market_orders(api, api_query_mock):
    """ Should call cancelmarketorders with given marketid. """
    api.cancel_all_market_orders(marketid=10)
    api_query_mock.assert_called_with('cancelmarketorders',
                                      request_data={'marketid': 10})


def test_cancel_all_orders(api, api_query_mock):
    """ Should call cancelallorders. """
    api.cancel_all_orders()
    api_query_mock.assert_called_with('cancelallorders')


def test_calculate_fees(api, api_query_mock):
    """ Should call calculatefees with the correct parameters. """
    api.calculate_fees('Buy', 200, 10)
    api_query_mock.assert_called_with('calculatefees',
                                      request_data={
                                          'ordertype': 'Buy',
                                          'quantity': 200,
                                          'price': 10
                                      })

def test_my_transfers(api, api_query_mock):
    """ Should call mytransfers. """
    api.my_transfers()
    api_query_mock.assert_called_with('mytransfers')


def test_wallet_status(api, api_query_mock):
    """ Should call getwalletstatus. """
    api.wallet_status()
    api_query_mock.assert_called_with('getwalletstatus')


def test_make_withdrawal(api, api_query_mock):
    """ Should call makewithdrawal with the given parameters. """
    api.make_withdrawal('address', 100)
    api_query_mock.assert_called_with('makewithdrawal',
                                      request_data={
                                          'address': 'address',
                                          'amount': 100
                                      })

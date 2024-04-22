from typing import Any

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils.types import Cloid

from hl_cli.utils import hprint, get_element_by_value
from hl_cli.hl.info import get_user_fills


def _parse_order_response(order_response: dict) -> dict:
    order_status = order_response['response']['data']['statuses']
    status = list(order_status[0].keys())[0]
    order_details = order_status[0][status] 

    return order_status, order_details


def _dformat_print(msg: str) -> None:
    direction = msg.split(':')[0]
    assert direction in ['LONG', 'SHORT'], 'Invalid msg direction prefix'
    color = 'GREEN' if direction == 'LONG' else 'RED'
    hprint(msg, color)


# def _derive_cloid(oid: int, uid: str) -> Cloid:
#     return Cloid.from_str(str(oid), uid)


def post_market_open(
    exchange: Exchange,
    coin: str,
    size: float,
    is_buy: bool
) -> None:
    direction = 'LONG' if is_buy else 'SHORT'
    _dformat_print(f'{direction}: Executing market open for {size} {coin}...')

    order_response = exchange.market_open(coin, is_buy, size)
    order_status, order_details = _parse_order_response(order_response)
    print('ORDER DETAILS')

    if any('error' in d for d in order_status):
        print('Error: ', order_status[0]['error']) #naive assumes only one list element
    else:
        total_size = order_details['totalSz']
        average_price = order_details['avgPx']
        _dformat_print(
            f'{direction}: Market order opened with {total_size} {coin} at an average price of ${average_price} {coin}.'
        )

    return order_details


def post_market_close(
    exchange: Exchange,
    info: Info, 
    address: str,
    coin: str,
    size: float,
) -> Any:
    order_response = exchange.market_close(coin, size)

    if order_response is None:
        print('Error: No open position for this coin.')
        return

    try:
        order_status, order_details = _parse_order_response(order_response)
        if any('error' in d for d in order_status):
            print('Error: ', order_status[0]['error']) #naive assumes only one list element
        else:
            total_size = order_details['totalSz']
            average_price = order_details['avgPx']
            closed_order = get_element_by_value(get_user_fills(info, address),'oid',order_details['oid'])
            closed_pnl = float(closed_order["closedPnl"])
            closed_pnl_sign = '+' if closed_pnl > 0 else '-'
            print(
                f'Order closed for {total_size} {coin} at an average price of ${average_price} {coin}. Closed PnL: {closed_pnl_sign}${abs(closed_pnl)}.'
            )

        return order_details
    except:
        print('Error: Position closed but error generating closed order details.')


def post_update_leverage(exchange: Exchange, coin: str, leverage: int, is_cross = True):
    response = exchange.update_leverage(leverage, coin, is_cross)

    if response['status'] == 'err':
        print(f'Error: {response["response"]}')
        return
    
    print(f'Leverage for {coin} updated to {leverage}x.')


def post_limit_open (
    exchange: Exchange,
    coin: str,
    price: float,
    size: float,
    is_buy: bool,
) -> None:
    direction = 'LONG' if is_buy else 'SHORT'
    _dformat_print(f'{direction}: Placing limit open for {size} {coin}...')

    order_response = exchange.order(
        coin,
        is_buy,
        size,
        price,
        order_type={"limit": {"tif": "Gtc"}},
        reduce_only=False,
    )
    order_status, order_details = _parse_order_response(order_response)
    if any('error' in d for d in order_status):
        print('Error: ', order_status[0]['error']) #naive assumes only one list element
    else:
        _dformat_print(
            f'{direction}: Resting limit order opened with {size} {coin} at a price of {price} {coin}.'
        )

    return order_details


def post_stop_loss(
    exchange: Exchange,
    coin: str,
    price: float,
    size: float,
    is_buy: bool,
    oid,
    is_market: bool = True,
) -> None:
    direction = 'LONG' if is_buy else 'SHORT'
    type = 'MARKET' if is_market else 'LIMIT'
    _dformat_print(f'{direction}: Placing {type} stop loss for {size} {coin}...')
    cloid = Cloid.from_int(oid)

    order_response = exchange.order(
        coin,
        is_buy,
        size,
        price,
        order_type={
            "trigger": {
                "triggerPx": price,
                "isMarket": is_market,
                "tpsl": "sl",
            }
        },
        reduce_only=True,
        cloid = cloid,
    )
    order_status, order_details = _parse_order_response(order_response)
    if any('error' in d for d in order_status):
        print('Error: ', order_status[0]['error']) #naive assumes only one list element
    else:
        _dformat_print(
            f'{direction}: Resting {type} stop loss opened with {size} {coin} at a price of {price} {coin}.'
        )

    return order_details


def post_take_profit(
    exchange: Exchange,
    coin: str,
    price: float,
    size: float,
    is_buy: bool,
    oid: int,
    is_market: bool = True,
) -> None:
    direction = 'LONG' if is_buy else 'SHORT'
    type = 'MARKET' if is_market else 'LIMIT'
    _dformat_print(f'{direction}: Placing {type} take profit for {size} {coin}...')
    # cloid = _derive_cloid(oid, exchange.account._address)
    cloid = Cloid.from_int(oid)

    order_response = exchange.order(
        coin,
        is_buy,
        size,
        price,
        order_type={
            "trigger": {
                "triggerPx": price,
                "isMarket": is_market,
                "tpsl": "tp",
            }
        },
        reduce_only=True,
        cloid = cloid,
    )

    order_status, order_details = _parse_order_response(order_response)
    if any('error' in d for d in order_status):
        print('Error: ', order_status[0]['error']) #naive assumes only one list element
    else:
        _dformat_print(f'{direction}: Resting {type} take_profit opened with {size} {coin} at a price of {price} {coin}.')

    return order_details


# def cancel_orders(
#     exchange: Exchange,
#     info: Info,
#     coin: str,
# ) -> None:
#     open_orders = exchange.get_open_orders(coin)
#     if not open_orders:
#         print('No open orders for this coin.')
#         return

#     for order in open_orders:
#         oid = order['oid']
#         response = exchange.cancel_order(oid)
#         if response['status'] == 'ok':
#             print(f'Order {oid} cancelled.')
#         else:
#             print(f'Error: {response["response"]}')
#     return

from hl_cli.hl.info import (
    get_coin_mid,
    get_coin_position,
    get_meta,
    get_positions,
)
from hl_cli.hl.exchange import (
    post_market_open,
    post_market_close,
    post_update_leverage,
    post_limit_open,
    post_stop_loss,
    post_take_profit
)
from hl_cli.parser import parse_args


class MarketOps:
    def __init__(self, hl_session):
        self.address = hl_session.address
        self.exchange = hl_session.exchange
        self.info = hl_session.info
        self.meta = get_meta(self.info)

    def _get_coin_meta(self, coin):
        return self.meta[coin]

    def _get_leverage(self, leverage, coin, is_cross):
        if leverage is None:
            leverage = self._get_coin_meta(coin)['maxLeverage']
            print(f'Leverage option not specified, using default max leverage of {leverage}...')
                
        leverage = int(leverage)
        post_update_leverage(self.exchange, coin, leverage, is_cross)
        return leverage
    
    def _round_size(self, size, coin):
        return round(size, self._get_coin_meta(coin)['szDecimals'])

    def _pcnt_size(self, pcnt, size, coin):
        return self._round_size(size * (pcnt / 100), coin)

    def _handle_tp(self, coin, tp_price, tp_pcnt, size, tp_is_market, is_buy, oid):
        if tp_price is not None:
            size = self._pcnt_size(tp_pcnt, size, coin)
            post_take_profit(
                self.exchange,coin, tp_price, size, is_buy, oid, tp_is_market
            )

    def _handle_sl(self, coin, sl_price, sl_pcnt, size, sl_is_market, is_buy, oid):
        if sl_price is not None:
            size = self._pcnt_size(sl_pcnt, size, coin)
            post_stop_loss(
                self.exchange, coin, sl_price, size, is_buy, oid, sl_is_market
            )

    def _calculate_size_open(self, size, usd, margin, coin, leverage, is_cross):
        if size is None:
            mid = get_coin_mid(self.info, coin)
            if usd is not None:
                size = usd / mid
            elif margin is not None:
                leverage = self._get_leverage(leverage, coin, is_cross)
                size = (margin * leverage) / mid
        size = self._round_size(size, coin)
        return size
    
    def _calculate_size_close(self, size, pcnt, coin):
        if size is None:
            position = get_coin_position(self.info, self.address, coin)
            position_size = float(position['szi'])
            size = float(position_size) * (pcnt / 100)
        size = self._round_size(abs(size), coin)
        is_long = position_size > 0
        return size, is_long

    def open(self, is_buy, args) -> None:
        arg_names = [
            'coin',
            '--price',
            '--size',
            '--usd',
            '--margin',
            '--pcnt',
            '--leverage',
            '--is_cross',
            '--tp_price',
            '--sl_price',
            '--tp_pcnt',
            '--sl_pcnt',
            '--tp_is_market',
            '--sl_is_market',
        ]
        parsed_args = parse_args(
            prog = 'open',
            description = 'Execute open order',
            arg_names = arg_names,
            args = args,
        )
        size = parsed_args.size
        price = parsed_args.price
        usd = parsed_args.usd
        margin = parsed_args.margin
        coin = parsed_args.coin
        leverage = parsed_args.leverage
        is_cross = parsed_args.is_cross
        tp_price = parsed_args.tp_price
        sl_price = parsed_args.sl_price
        tp_pcnt = parsed_args.tp_pcnt
        sl_pcnt = parsed_args.sl_pcnt
        tp_is_market = parsed_args.tp_is_market
        sl_is_market = parsed_args.sl_is_market

        if (
            (sum(x is not None for x in (size, usd, margin)) == 0) or 
            (sum(x is not None for x in (size, usd, margin)) > 1)
        ):
            print('Usage: open <coin> --size <size> OR --usd <usd> OR --margin <margin>')
            return

        size = self._calculate_size_open(size, usd, margin, coin, leverage, is_cross)

        if price is None:
            order_details = post_market_open(self.exchange, coin, size, is_buy)
        else:
            order_details = post_limit_open(self.exchange, coin, price, size, is_buy)

        oid = order_details['oid']
        self._handle_tp(coin, tp_price, tp_pcnt, size, tp_is_market, not is_buy, oid)
        self._handle_sl(coin, sl_price, sl_pcnt, size, sl_is_market, not is_buy, oid)

    def close(self, args):
        arg_names = ['coin', '--size', '--pcnt', '--at_mid']
        parsed_args = parse_args(
            prog = 'close',
            description = 'Execute close order',
            arg_names = arg_names,
            args = args,
        )
        coin = parsed_args.coin
        size = parsed_args.size
        pcnt = parsed_args.pcnt
        at_mid = parsed_args.at_mid
        if (sum(x is not None for x in (size, pcnt)) > 1):
            print('Usage: market_close <coin> --size <size> OR --pcnt <pcnt>')
            return
        
        if coin == 'all':
            positions, _ = get_positions(self.info, self.address)
            for position in positions:
                coin = position['coin']
                post_market_close(self.exchange, self.info, self.address, coin, size)
            return
        
        size, is_long = self._calculate_size_close(size, pcnt, coin)

        if at_mid:
            mid = get_coin_mid(self.info, coin)
            post_stop_loss(self.exchange, coin, mid, size, not is_long, False)
        else:
            post_market_close(self.exchange, self.info, self.address, coin, size)

    def update_leverage(self, args):
        arg_names = ['coin', 'leverage', '--is_cross']
        parsed_args = parse_args(
            prog = 'update_leverage',
            description = 'Update leverage for a coin',
            arg_names = arg_names,
            args = args,
        )
        coin = parsed_args.coin
        leverage = parsed_args.leverage
        is_cross = parsed_args.is_cross

        post_update_leverage(self.exchange, coin, leverage, is_cross)

    def stop_loss(self, args):
        arg_names = ['coin', 'price', '--size', '--pcnt', '--is_market']
        parsed_args = parse_args(
            prog = 'stop_loss',
            description = 'Execute stop loss order',
            arg_names = arg_names,
            args = args,
        )
        coin = parsed_args.coin
        price = parsed_args.price
        size = parsed_args.size
        pcnt = parsed_args.pcnt
        is_market = parsed_args.is_market
        if (sum(x is not None for x in (size, pcnt)) > 1):
            print('Usage: stop_loss <coin> <price> --size <size> OR --pcnt <pcnt>')
            return
        
        size, is_long = self._calculate_size_close(size, pcnt, coin)

        post_stop_loss(self.exchange, coin, price, size, not is_long, is_market)

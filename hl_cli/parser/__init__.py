import argparse

__all__ = [
    'parse_args',
]

argument_params = {
    'coin': {'type': str, 'help': 'Coin to get meta for. "all" is an open for close command (will market close all positions).'},
    'price': {'type': float, 'help': 'Price for the order to action on.'},
    '--coin': {'type': str, 'default': None, 'help': 'Coin to get meta for. "all" is an open for close command (will market close all positions).'},
    '--price': {'type': float, 'default': None, 'help': 'Price for the order to action on'},
    '--size': {'type': float, 'default': None, 'help': 'Size of the position in coin units'},
    '--usd': {'type': float, 'default': None, 'help': 'Size of the position in USD'},
    '--margin': {'type': float, 'default': None, 'help': 'Size of the position in margin'},
    '--leverage': {'type': float, 'default': None, 'help': 'Leverage to use for the position. Max leverage will be used by default.'},
    '--is_cross': {'type': bool, 'default': True, 'help': 'Is the position cross margin?'},
    '--tp_price': {'type': float, 'default': None, 'help': 'Take profit price'},
    '--sl_price': {'type': float, 'default': None, 'help': 'Stop loss price'},
    '--tp_pcnt': {'type': float, 'default': 100, 'help': 'Take profit percentage'},
    '--sl_pcnt': {'type': float, 'default': 100, 'help': 'Stop loss percentage'},
    '--tp_is_market': {'type': bool, 'default': False, 'help': 'Is take profit a market order?'},
    '--sl_is_market': {'type': bool, 'default': False, 'help': 'Is stop loss a market order?'},
    '--pcnt': {'type': float, 'default': 100.0, 'help': 'Percent of the position to take action on'},
    '--at_mid': {'type': bool, 'default': False, 'help': 'Place limit order at mid price'},
    '--is_market': {'type': bool, 'default': False, 'help': 'True if market order, False if limit order'},
}

def parse_args(prog: str, description: str, arg_names: list, args: str):
    parser = argparse.ArgumentParser(prog=prog, description=description)
    for arg in arg_names:
        parser.add_argument(arg, **argument_params[arg])
    return parser.parse_args(args.split())

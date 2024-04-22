import argparse
from colorama import init, Fore
from hl_cli.hl.info import (
    get_coin_meta,
    get_user_state,
    get_mids,
    get_meta,
    get_positions
)
from hl_cli.parser import parse_args
from hl_cli.utils import get_element_by_value

init(autoreset=True)

class InfoOps:
    def __init__(self, hl_session):
        self.address = hl_session.address
        self.info = hl_session.info
        self.meta = get_meta(self.info)
        self.liq_margin = 0.05

    def _abs_liq_mid_diff(self, liq_price: float, mid_price: float):
        return abs(1 - (liq_price / mid_price))

    def _fmt_color(self, string: str, color: str) -> str:
        return f'{color}{string}{Fore.RESET}' if color else string

    # @TODO: clean up duplicate transformations
    def _format_position(self, position, mid_price, uPNL, uROE):
        position['current_mid_price'] = f"{mid_price:.2f}"
        position['margin'] = f"${float(position['margin']):.2f}"
        position['position_value'] = f"${float(position['position_value']):.2f}"
        position['uPNL'] = f'+${uPNL}' if uPNL > 0 else f'-${abs(uPNL)}'
        position['uROE'] = f'+{uROE}' if uPNL > 0 else uROE

        return position

    def _get_color_adjust_dict(self, position, liq_price, mid_price, uPNL):
        color_adjust_dict = {}
        color_adjust_dict['coin'] = Fore.LIGHTGREEN_EX if position['direction'] == 'LONG' else Fore.LIGHTRED_EX
        color_adjust_dict['direction'] = Fore.LIGHTGREEN_EX if position['direction'] == 'LONG' else Fore.LIGHTRED_EX
        color_adjust_dict['size'] = Fore.LIGHTGREEN_EX if position['direction'] == 'LONG' else Fore.LIGHTRED_EX

        if self._abs_liq_mid_diff(liq_price, mid_price) < self.liq_margin:
            color_adjust_dict['liquidation_price'] = Fore.RED

        if uPNL < 0:
            color_adjust_dict['uPNL'] = Fore.RED
            color_adjust_dict['uROE'] = Fore.RED
        elif uPNL > 0:
            color_adjust_dict['uPNL'] = Fore.LIGHTGREEN_EX
            color_adjust_dict['uROE'] = Fore.LIGHTGREEN_EX

        return color_adjust_dict
    
    def _get_positions(self, coin: str = None):
        positions, available_to_trade = get_positions(self.info, self.address)
        if not positions:
            print('No open positions')
            raise SystemExit

        if coin:
            positions = [position for position in positions if position['coin'] == coin]
            print(positions)

        return positions, available_to_trade
    
    def _print_positions(self, positions):
        total_uPNL = 0
        print('\n' * 3)
        print('-----------------------')
        print('-------POSITIONS-------')
        for position in positions:
            assert position['direction'] in ['LONG', 'SHORT'], 'Invalid position direction'
            liq_price = float(position['liquidation_price']) if position['liquidation_price'] else 0
            uPNL = round(float(position['uPNL']), 2)
            total_uPNL += uPNL
            uROE = f"{float(position['uROE']):.2%}"
            mid_price = float(position['current_mid_price'])
            position = self._format_position(position, mid_price, uPNL, uROE)
            uPNL = float(position['uPNL'].replace('$', '').replace('+', ''))
            color_adjust_dict = self._get_color_adjust_dict(position, liq_price, mid_price, uPNL)

            for key, value in position.items():
                print(self._fmt_color(f'{key}: {value}', color_adjust_dict.get(key)))

            print('-----------------------')

        return total_uPNL

    def positions(self, args):
        arg_names = ['--coin']
        parsed_args = parse_args(
            prog = 'position',
            description = 'Get a position',
            arg_names = arg_names,
            args = args,
        )
        coin = parsed_args.coin
        positions, available_to_trade = self._get_positions(coin)
        total_uPNL = self._print_positions(positions)
        print('Total uPNL: ', total_uPNL)
        print('Available to trade: ', available_to_trade)





def coin_meta(info, args):
    parser = argparse.ArgumentParser(prog='coin_meta', description='Get a coins meta')
    parser.add_argument('coin', type=str, help='Coin to get meta for')
    try:
        parsed_args = parser.parse_args(args.split())
        coin = parsed_args.coin
        print(f'Fetching metadata for {coin}...')
        meta = get_coin_meta(info, coin)
        print(meta)
    except argparse.ArgumentError as e:
        print('Error: ', e)
    except Exception as e:
        print('Error: ', e)

# def open_positions(info, address):
#     user_state = get_user_state(info, address)
#     positions = user_state['assetPositions']
#     formatted_positions = []
#     mids = get_mids(info)
#     for position_dict in positions:
#         position = position_dict['position']
#         formatted_positions.append({
#             'coin': position['coin'],
#             'size': position['szi'],
#             'entry_price': position['entryPx'],
#             'current_mid_price': mids[position['coin']],
#             'uPNL': position['unrealizedPnl'],
#             'position_value': position['positionValue'],
#             'liquidation_price': position['liquidationPx'],
#             'cumulative_funding': position['cumFunding'],
#             'leverage': position['leverage'],
#             'margin': position['marginUsed'],
#         })

#     return formatted_positions

# def open_position(info, address, args):
#     parser = argparse.ArgumentParser(prog='coin_meta', description='Get a coins meta')
#     parser.add_argument('coin', type=str, help='Coin to get meta for')
#     try:
#         parsed_args = parser.parse_args(args.split())
#         coin = parsed_args.coin
#         positions = open_positions(info, address)
#         return get_element_by_value(positions, 'coin', coin)
#     except argparse.ArgumentError as e:
#         print('Error: ', e)
#     except Exception as e:
#         print('Error: ', e)


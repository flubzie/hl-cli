from typing import Any, List, Dict, Union

from hyperliquid.info import Info

from hl_cli import utils

def get_coin_meta(info: Info, coin: str) -> Dict[str, Union[str, int, bool]]:
    coin_meta = utils.get_element_by_value(
        info.meta()['universe'],
        'name',
        coin
    )
    return coin_meta

def get_meta(info: Info) -> Dict[str, Union[str, int, bool]]:
    formatted_meta = {
        d['name']: {
            key: value for key, value in d.items() if key != 'name'
        } for d in info.meta()['universe']
    }
    return formatted_meta

def get_mids(info: Info) -> Dict[str, str]:
    return info.all_mids()

def get_coin_mid(info: Info, coin:str) -> float:
    return float(info.all_mids()[coin])

def get_user_state(info: Info, address: str) -> Dict[str, Any]:
    return info.user_state(address)

def _get_user_state_position_element_by_value(data: list, key: str, value: Any) -> None:
    return next(
        (item for item in data if item.get('position').get(key) == value),
        None
    )

def get_coin_position(info: Info, address: str, coin: str) -> Dict[str, Any]:
    return _get_user_state_position_element_by_value(
        get_user_state(info, address)['assetPositions'],
        'coin',
        coin
    )['position']


def get_positions(info, address):
    user_state = get_user_state(info, address)
    available_to_trade = user_state['withdrawable']
    positions = user_state['assetPositions']
    formatted_positions = []
    mids = get_mids(info)
    for position_dict in positions:
        position = position_dict['position']
        formatted_positions.append({
            'coin': position['coin'],
            'direction': 'LONG' if float(position['szi']) > 0 else 'SHORT',
            'size': position['szi'],
            'position_value': position['positionValue'],
            'entry_price': position['entryPx'],
            'current_mid_price': mids[position['coin']],
            'uPNL': position['unrealizedPnl'],
            'uROE': position['returnOnEquity'],
            'liquidation_price': position['liquidationPx'],
            'margin': position['marginUsed'],
            'leverage': position['leverage'],
            'cumulative_funding': position['cumFunding'],
        })

    return formatted_positions, available_to_trade


def get_user_fills(info, address):
    return info.user_fills(address)

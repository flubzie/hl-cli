from cmd import Cmd
import os

from dotenv import load_dotenv
import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

from hl_cli.constants import URL
from hl_cli.commands import (
    MarketOps,
    InfoOps,
)
from hl_cli.decorators import command_error_handler
from hl_cli.utils import help


class HLSession(Cmd):
    prompt = ('hl-cli> ')

    def __init__(self) -> None:
        super().__init__()
        self._hl_setup()
        self.market_ops = MarketOps(self)
        self.info_ops = InfoOps(self)

    def _hl_setup(self) -> None:
        load_dotenv()
        account: LocalAccount = eth_account.Account.from_key(os.getenv('PRIVATE_KEY'))
        self.address = account._address
        self.exchange = Exchange(account, URL)
        self.info = Info(URL, skip_ws = True)

    # Market ops
    @command_error_handler
    def do_long(self, args) -> None:
        self.market_ops.open(True, args)

    @command_error_handler
    def do_short(self, args) -> None:
        self.market_ops.open(False, args)

    @command_error_handler
    def do_close(self, args) -> None:
        self.market_ops.close(args)

    @command_error_handler
    def do_update_leverage(self, args) -> None:
        self.market_ops.update_leverage(args)

    @command_error_handler
    def do_stop_loss(self, args) -> None:
        self.market_ops.stop_loss(args)

    # Info ops
    # def do_coin_meta(self, args) -> None:
    #     self.info_ops.coin_meta(args)

    @command_error_handler
    def do_positions(self, args) -> None:
        self.info_ops.positions(args)

    # def do_open_position(self, args) -> None:
    #     pprint(self.info_ops.open_position(args))
    
    @command_error_handler
    def do_exit(self, _) -> bool:
        print('Exiting the interactive shell...')
        print('Goodbye')
        return True
        
    @command_error_handler
    def do_help(self, arg):
        help(self, arg)
        

def cli() -> None:
    print('Welcome to the unofficial Hyperliquid Command Line Interface!')
    print('Type "help" for a list of commands.')
    hl_cli = HLSession()
    hl_cli.cmdloop()

if __name__ == '__main__':
    cli()

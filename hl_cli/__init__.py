# @TODO: TEMPORARY for development
import os

from dotenv import load_dotenv
import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

from hl_cli.constants import URL


class DevSetup():
    def __init__(self) -> None:
        super().__init__()
        self.hl_setup()

    def hl_setup(self) -> None:
        load_dotenv()
        account: LocalAccount = eth_account.Account.from_key(os.getenv('PRIVATE_KEY'))
        self.address = account._address
        self.exchange = Exchange(account, URL)
        self.info = Info(URL)
        
from .my_protocol import AccountsStorageProtocol
from typing import List
from ..model import Account, AccountStatus


class MockAccountsStorage(AccountsStorageProtocol):
    def __init__(self):
        self.accounts = []

    def add_account(self, account: Account):
        self.accounts.append(account)

    def get_all_accounts(self) -> List[Account]:
        return self.accounts

    def mark_account_as_blocked(self, id: str):
        for account in self.accounts:
            if account.id == id:
                account.status = AccountStatus.BLOCKED

    def set_account_processing(self, id: str):
        for account in self.accounts:
            if account.id == id:
                account.status = AccountStatus.PROCESSING

    def clear(self):
        self.accounts = []

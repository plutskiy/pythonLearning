from abc import ABC, abstractmethod
from typing import Optional, Protocol, List
from ..model import Account


class AccountsStorageProtocol(ABC):
    @abstractmethod
    def add_account(self):
        pass

    @abstractmethod
    def get_all_accounts(self) -> List[Account]:
        pass

    @abstractmethod
    def mark_account_as_blocked(self, account_id: int):
        pass

    @abstractmethod
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        pass

    @abstractmethod
    def set_account_processing(self, account_id: int) -> Optional[Account]:
        pass

    @abstractmethod
    def set_account_pending(self, account_id: int) -> Optional[Account]:
        pass

    @abstractmethod
    def clear(self):
        pass

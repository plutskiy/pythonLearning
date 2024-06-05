from .my_protocol import AccountsStorageProtocol
import redis
from ..model import Account, AccountStatus
from typing import Optional, Protocol, List


class AccountsRedisStorage(AccountsStorageProtocol):
    def __init__(self):
        self.r = redis.Redis(host='95.164.7.8', port=6379, db=0)

    def add_account(self):
        account_id = self.r.incr('account_id')

        account_data = {
            'phone_number': '777',
            'password': 'pswd',
            'status': AccountStatus.PENDING.value
        }

        self.r.hset(f"account:{account_id}", mapping=account_data)

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        account_data = self.r.hgetall(f"account:{account_id}")
        if not account_data:
            return None
        return Account(
            id=account_id,
            phone_number=account_data[b'phone_number'].decode(),
            password=account_data[b'password'].decode(),
            status=AccountStatus(account_data[b'status'].decode())
        )

    def get_all_accounts(self) -> List[Account]:
        keys = self.r.keys('account:*')
        accounts = []
        for key in keys:
            account_data = self.r.hgetall(key)
            account = Account(
                id=int(key.decode().split(':')[1]),
                phone_number=account_data[b'phone_number'].decode(),
                password=account_data[b'password'].decode(),
                status=AccountStatus(account_data[b'status'].decode())
            )
            accounts.append(account)

        accounts.sort(key=lambda x: x.id)

        return accounts

    def mark_account_as_blocked(self, id: str):
        self.r.hset(f"account:{id}", 'status', AccountStatus.BLOCKED.value)

    def set_account_processing(self, id: str):
        self.r.hset(f"account:{id}", 'status', AccountStatus.PROCESSING.value)

    def set_account_pending(self, account_id: int) -> Optional[Account]:
        self.r.hset(f"account:{id}", 'status', AccountStatus.PENDING.value)

    def clear(self):
        keys = self.r.keys('account:*')
        if keys:
            self.r.delete(*keys)

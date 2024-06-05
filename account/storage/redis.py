import redis.asyncio as aioredis
from .my_protocol import AccountsStorageProtocol
from ..model import Account, AccountStatus
from typing import Optional, List

class AccountsRedisStorage(AccountsStorageProtocol):
    def __init__(self):
        self.r = None

    async def initialize(self):
        self.r = aioredis.Redis(host='95.164.7.8', port=6379, decode_responses=True)

    async def add_account(self):
        account_id = await self.r.incr('account_id')

        account_data = {
            'phone_number': '777',
            'password': 'pswd',
            'status': AccountStatus.PENDING.value
        }

        await self.r.rpush(f"account:{account_id}", *account_data.values())

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        account_data = await self.r.lrange(f"account:{account_id}", 0, -1)
        if not account_data:
            return None
        return Account(
            id=account_id,
            phone_number=account_data[0],
            password=account_data[1],
            status=AccountStatus(account_data[2])
        )

    async def get_all_accounts(self) -> List[Account]:
        keys = await self.r.keys('account:*')
        accounts = []
        for key in keys:
            account_data = await self.r.lrange(key, 0, -1)
            account = Account(
                id=int(key.split(':')[1]),
                phone_number=account_data[0],
                password=account_data[1],
                status=AccountStatus(account_data[2])
            )
            accounts.append(account)

        accounts.sort(key=lambda x: x.id)

        return accounts

    async def mark_account_as_blocked(self, id: int):
        await self.r.lset(f"account:{id}", 2, AccountStatus.BLOCKED.value)

    async def set_account_processing(self, id: int):
        await self.r.lset(f"account:{id}", 2, AccountStatus.PROCESSING.value)

    async def set_account_pending(self, id: int):
        await self.r.lset(f"account:{id}", 2, AccountStatus.PENDING.value)

    async def clear(self):
        await self.r.flushdb()

    async def close(self):
        self.r.close()
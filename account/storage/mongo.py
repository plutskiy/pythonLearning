from motor.motor_asyncio import AsyncIOMotorClient
from .my_protocol import AccountsStorageProtocol
from ..model import Account, AccountStatus
from typing import List, Optional


class AccountsMongoStorage(AccountsStorageProtocol):
    def __init__(self, loop):
        self.client = AsyncIOMotorClient('95.164.7.8', 27017, io_loop=loop)
        self.db = self.client['Accounts']
        self.collection = self.db['accounts']

    async def initialize(self):
        # Use update_one with upsert=True to ensure 'last_id' document exists
        await self.db['last_id'].update_one(
            {'_id': 'account_id'},
            {'$setOnInsert': {'last_id': 0}},
            upsert=True
        )

    async def add_account(self):
        last_id_entry = await self.db['last_id'].find_one()
        last_id = last_id_entry['last_id'] + 1

        await self.db['last_id'].update_one(
            {'_id': 'account_id'},
            {'$set': {'last_id': last_id}}
        )

        account_data = {
            'id': last_id,
            'phone_number': '777',
            'password': 'pswd',
            'status': AccountStatus.PENDING.value
        }

        await self.collection.insert_one(account_data)

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        account_data = await self.collection.find_one({'id': account_id})
        if not account_data:
            return None
        return Account(
            id=account_id,
            phone_number=account_data['phone_number'],
            password=account_data['password'],
            status=AccountStatus(account_data['status'])
        )

    async def get_all_accounts(self) -> List[Account]:
        accounts = []
        async for account_data in self.collection.find():
            account = Account(
                id=account_data['id'],
                phone_number=account_data['phone_number'],
                password=account_data['password'],
                status=AccountStatus(account_data['status'])
            )
            accounts.append(account)

        accounts.sort(key=lambda x: x.id)

        return accounts

    async def mark_account_as_blocked(self, id: int):
        await self.collection.update_one({'id': id}, {'$set': {'status': AccountStatus.BLOCKED.value}})

    async def set_account_processing(self, id: int):
        await self.collection.update_one({'id': id}, {'$set': {'status': AccountStatus.PROCESSING.value}})

    async def set_account_pending(self, id: int):
        await self.collection.update_one({'id': id}, {'$set': {'status': AccountStatus.PENDING.value}})

    async def clear(self):
        await self.collection.drop()

    async def close(self):
        self.client.close()

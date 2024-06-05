import asyncio
import unittest
from account.model import AccountStatus, Account
from account.storage.my_protocol import AccountsStorageProtocol
from account.storage.postgres import AccountsPostgresStorage
from account.storage.mongo import AccountsMongoStorage
from account.storage.redis import AccountsRedisStorage


class AccountManager:
    def __init__(self, accounts_storage: AccountsStorageProtocol):
        self.accounts_storage = accounts_storage

    async def register_10_accounts(self):
        for _ in range(10):
            await self.accounts_storage.add_account()

    async def block_last_account(self):
        accounts = await self.accounts_storage.get_all_accounts()
        last_account = accounts[-1]
        await self.accounts_storage.mark_account_as_blocked(last_account.id)

    async def work_with_2_and_4_accounts(self):
        accounts = await self.accounts_storage.get_all_accounts()
        second = accounts[1]
        fourth = accounts[3]
        await self.accounts_storage.set_account_processing(second.id)
        await self.accounts_storage.set_account_processing(fourth.id)

    async def clear(self):
        await self.accounts_storage.clear()


class TestAccountManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.loop = asyncio.get_running_loop()

    async def asyncTearDown(self):
        await self.storage.close()

    async def test_account_manager_redis(self):
        self.storage = AccountsRedisStorage()
        await self.storage.initialize()
        await self._run_test(self.storage)

    async def test_account_manager_postgres(self):
        self.storage = AccountsPostgresStorage()
        await self.storage.initialize()
        await self._run_test(self.storage)

    async def test_account_manager_mongo(self):
        self.storage = AccountsMongoStorage(asyncio.get_running_loop())
        await self.storage.initialize()
        await self._run_test(self.storage)

    async def _run_test(self, storage: AccountsStorageProtocol):
        am = AccountManager(storage)
        try:
            accounts = await am.accounts_storage.get_all_accounts()
            self.assertEqual(len(accounts), 0)
            await am.register_10_accounts()
            await am.work_with_2_and_4_accounts()
            await am.block_last_account()
            accounts = await am.accounts_storage.get_all_accounts()
            self.assertEqual(len(accounts), 10)
            self.assertEqual(accounts[0].status, AccountStatus.PENDING)
            self.assertEqual(accounts[1].status, AccountStatus.PROCESSING)
            self.assertEqual(accounts[2].status, AccountStatus.PENDING)
            self.assertEqual(accounts[3].status, AccountStatus.PROCESSING)
            self.assertEqual(accounts[4].status, AccountStatus.PENDING)
            self.assertEqual(accounts[5].status, AccountStatus.PENDING)
            self.assertEqual(accounts[6].status, AccountStatus.PENDING)
            self.assertEqual(accounts[7].status, AccountStatus.PENDING)
            self.assertEqual(accounts[8].status, AccountStatus.PENDING)
            self.assertEqual(accounts[9].status, AccountStatus.BLOCKED)
            print(f'С реализацией {type(storage).__name__} все в порядке')
        finally:
            await am.clear()


if __name__ == '__main__':
    unittest.main()
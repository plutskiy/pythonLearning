import unittest
from dataclasses import dataclass
from account.model import AccountStatus, Account
from account.storage.my_protocol import AccountsStorageProtocol
from account.storage.postgres import AccountsPostgresStorage
from account.storage.mongo import AccountsMongoStorage
from account.storage.redis import AccountsRedisStorage


@dataclass
class AccountManager:
    accounts_storage: AccountsStorageProtocol

    def register_10_accounts(self):
        for i in range(10):
            self.accounts_storage.add_account()

    def block_last_account(self):
        accounts = self.accounts_storage.get_all_accounts()
        last_account = accounts[-1]
        self.accounts_storage.mark_account_as_blocked(last_account.id)

    def work_with_2_and_4_accounts(self):
        accounts = self.accounts_storage.get_all_accounts()
        second = accounts[1]
        fourth = accounts[3]
        self.accounts_storage.set_account_processing(second.id)
        self.accounts_storage.set_account_processing(fourth.id)

    def clear(self):
        self.accounts_storage.clear()


class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.realisations = [AccountsRedisStorage, AccountsPostgresStorage, AccountsMongoStorage]

    def test_account_manager_redis(self):
        self._run_test(AccountsRedisStorage())

    def test_account_manager_postgres(self):
        self._run_test(AccountsPostgresStorage())

    def test_account_manager_mongo(self):
        self._run_test(AccountsMongoStorage())

    def _run_test(self, storage):
        am = AccountManager(storage)
        try:
            accounts = am.accounts_storage.get_all_accounts()
            self.assertEqual(len(accounts), 0)
            am.register_10_accounts()
            am.work_with_2_and_4_accounts()
            am.block_last_account()
            accounts = am.accounts_storage.get_all_accounts()
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
            print(f'With realisation {type(storage).__name__} everything is OK')
        finally:
            am.clear()


if __name__ == '__main__':
    unittest.main()

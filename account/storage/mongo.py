from pymongo import MongoClient
from .my_protocol import AccountsStorageProtocol
from ..model import Account, AccountStatus
from typing import List, Optional


class AccountsMongoStorage(AccountsStorageProtocol):
    def __init__(self):
        self.client = MongoClient('95.164.7.8', 27017)
        self.db = self.client['Accounts']
        self.collection = self.db['accounts']

    def add_account(self):
        last_id_entry = self.db['last_id'].find_one()
        if last_id_entry is None:
            last_id = 1
            self.db['last_id'].insert_one({'_id': 'account_id', 'last_id': last_id})
        else:
            last_id = last_id_entry['last_id'] + 1
            self.db['last_id'].update_one({'_id': 'account_id'}, {'$set': {'last_id': last_id}})

        account_data = {
            'id': last_id,
            'phone_number': '777',
            'password': 'pswd',
            'status': AccountStatus.PENDING.value
        }

        self.collection.insert_one(account_data)

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        account_data = self.collection.find_one({'id': account_id})
        if not account_data:
            return None
        return Account(
            id=account_id,
            phone_number=account_data['phone_number'],
            password=account_data['password'],
            status=AccountStatus(account_data['status'])
        )

    def get_all_accounts(self) -> List[Account]:
        accounts = []
        for account_data in self.collection.find():
            account = Account(
                id=account_data['id'],
                phone_number=account_data['phone_number'],
                password=account_data['password'],
                status=AccountStatus(account_data['status'])
            )
            accounts.append(account)

        accounts.sort(key=lambda x: x.id)

        return accounts

    def mark_account_as_blocked(self, id: str):
        self.collection.update_one({'id': id}, {'$set': {'status': AccountStatus.BLOCKED.value}})

    def set_account_processing(self, id: str):
        self.collection.update_one({'id': id}, {'$set': {'status': AccountStatus.PROCESSING.value}})

    def set_account_pending(self, account_id: int) -> Optional[Account]:
        self.collection.update_one({'id': id}, {'$set': {'status': AccountStatus.PENDING.value}})

    def clear(self):
        self.collection.delete_many({})

import asyncpg
from .my_protocol import AccountsStorageProtocol
from ..model import Account, AccountStatus
from typing import Optional, List

class AccountsPostgresStorage(AccountsStorageProtocol):
    def __init__(self):
        self.conn = None

    async def initialize(self):
        self.conn = await asyncpg.connect(database="mydatabase", host="95.164.7.8", port="5432", user='user', password="password")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(255),
            password VARCHAR(255),
            status VARCHAR(255)
        )
        """
        await self.conn.execute(create_table_query)

    async def add_account(self):
        phone_number = '777'
        password = 'pswd'
        status = AccountStatus.PENDING
        query = "INSERT INTO accounts (phone_number, password, status) VALUES ($1, $2, $3)"
        await self.conn.execute(query, phone_number, password, status.value)

    async def get_all_accounts(self) -> List[Account]:
        rows = await self.conn.fetch("SELECT id, phone_number, password, status FROM accounts")
        accounts = [Account(id=row['id'], phone_number=row['phone_number'], password=row['password'], status=AccountStatus(row['status'])) for row in rows]
        accounts.sort(key=lambda x: x.id)
        return accounts

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        query = "SELECT id, phone_number, password, status FROM accounts WHERE id = $1"
        row = await self.conn.fetchrow(query, account_id)
        if not row:
            return None
        return Account(id=row['id'], phone_number=row['phone_number'], password=row['password'], status=AccountStatus(row['status']))

    async def mark_account_as_blocked(self, id: str):
        query = "UPDATE accounts SET status = $1 WHERE id = $2"
        await self.conn.execute(query, AccountStatus.BLOCKED.value, id)

    async def set_account_processing(self, id: str):
        query = "UPDATE accounts SET status = $1 WHERE id = $2"
        await self.conn.execute(query, AccountStatus.PROCESSING.value, id)

    async def set_account_pending(self, id: str):
        query = "UPDATE accounts SET status = $1 WHERE id = $2"
        await self.conn.execute(query, AccountStatus.PENDING.value, id)

    async def clear(self):
        await self.conn.execute("DROP TABLE IF EXISTS accounts")

    async def close(self):
        await self.conn.close()

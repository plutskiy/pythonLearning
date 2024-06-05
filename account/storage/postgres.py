from .my_protocol import AccountsStorageProtocol
import psycopg2
from ..model import Account, AccountStatus
from typing import Optional, Protocol, List


class AccountsPostgresStorage(AccountsStorageProtocol):
    def __init__(self):
        self.conn = psycopg2.connect(database="mydatabase", host="95.164.7.8", port="5432", user='user',
                                     password="password")
        self.cursor = self.conn.cursor()

        create_table_query = """
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        phone_number VARCHAR(255),
        password VARCHAR(255),
        status VARCHAR(255)
    )
    """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def add_account(self):
        phone_number = '777'
        password = 'pswd'
        status = AccountStatus.PENDING
        query = "INSERT INTO accounts (phone_number, password, status) VALUES (%s, %s, %s)"
        values = (phone_number, password, status.value)
        self.cursor.execute(query, values)
        self.conn.commit()

    def get_all_accounts(self) -> List[Account]:
        self.cursor.execute("SELECT id, phone_number, password, status FROM accounts")
        rows = self.cursor.fetchall()

        accounts = []
        for row in rows:
            account = Account(id=row[0], phone_number=row[1], password=row[2], status=AccountStatus(row[3]))
            accounts.append(account)

        accounts.sort(key=lambda x: x.id)

        return accounts

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        query = "SELECT id, phone_number, password, status FROM accounts WHERE id = %s"
        values = (account_id,)
        self.cursor.execute(query, values)
        row = self.cursor.fetchone()

        if not row:
            return None

        return Account(id=row[0], phone_number=row[1], password=row[2], status=AccountStatus(row[3]))

    def mark_account_as_blocked(self, id: str):
        query = "UPDATE accounts SET status = %s WHERE id = %s"
        values = (AccountStatus.BLOCKED.value, id)
        self.cursor.execute(query, values)
        self.conn.commit()

    def set_account_processing(self, id: str):
        query = "UPDATE accounts SET status = %s WHERE id = %s"
        values = (AccountStatus.PROCESSING.value, id)
        self.cursor.execute(query, values)
        self.conn.commit()

    def set_account_pending(self, id: str):
        query = "UPDATE accounts SET status = %s WHERE id = %s"
        values = (AccountStatus.PENDING.value, id)
        self.cursor.execute(query, values)
        self.conn.commit()

    def clear(self):
        self.cursor.execute("DROP TABLE IF EXISTS accounts")
        self.conn.commit()

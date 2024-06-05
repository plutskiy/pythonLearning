import json
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum

class AccountStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    BLOCKED = 'blocked'

@dataclass
class Account:
    id: int
    phone_number: str
    password: str
    status: AccountStatus

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        data['status'] = AccountStatus(data['status'])
        return cls(**data)

    @classmethod
    def from_json(cls, data: str) -> 'Account':
        return cls.from_dict(json.loads(data))
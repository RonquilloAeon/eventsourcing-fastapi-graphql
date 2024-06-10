from typing import Optional

from decimal import Decimal
from uuid import UUID

import strawberry

from src.app.bank_accounts import BankAccounts

accounts = BankAccounts()


@strawberry.type
class Account:
    id: UUID
    full_name: str
    email_address: str
    balance: Decimal
    overdraft_limit: Optional[Decimal] = None


@strawberry.type
class Error:
    error: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def open_account(self, full_name: str, email_address: str) -> UUID:
        try:
            return accounts.open_account(full_name, email_address)
        except Exception as e:
            return Error(error=e.__class__.__name__)

    @strawberry.mutation
    def deposit_funds(self, account_id: UUID, amount: Decimal) -> Optional[Account]:
        try:
            accounts.deposit_funds(credit_account_id=account_id, amount=amount)
            return accounts.get_account(account_id)
        except Exception as e:
            return Error(error=e.__class__.__name__)

    @strawberry.mutation
    def withdraw_funds(self, account_id: UUID, amount: Decimal) -> Optional[Account]:
        try:
            accounts.withdraw_funds(debit_account_id=account_id, amount=amount)
            return accounts.get_account(account_id)
        except Exception as e:
            return Error(error=e.__class__.__name__)

    @strawberry.mutation
    def transfer_funds(
        self, account_id: UUID, to_account_id: UUID, amount: Decimal
    ) -> Optional[Account]:
        try:
            accounts.transfer_funds(
                debit_account_id=account_id,
                credit_account_id=to_account_id,
                amount=amount,
            )
            return accounts.get_account(account_id)
        except Exception as e:
            return Error(error=e.__class__.__name__)

    @strawberry.mutation
    def set_overdraft_limit(
        self, account_id: UUID, limit: Decimal
    ) -> Optional[Account]:
        try:
            accounts.set_overdraft_limit(account_id=account_id, overdraft_limit=limit)
            return accounts.get_account(account_id)
        except Exception as e:
            return Error(error=e.__class__.__name__)

    @strawberry.mutation
    def close_account(self, account_id: UUID) -> Optional[Account]:
        try:
            accounts.close_account(account_id)
            return accounts.get_account(account_id)
        except Exception as e:
            return Error(error=e.__class__.__name__)


@strawberry.type
class Query:
    @strawberry.field
    def get_account(self, account_id: UUID) -> Optional[Account]:
        try:
            return accounts.get_account(account_id)
        except Exception as e:
            return Error(error=e.__class__.__name__)

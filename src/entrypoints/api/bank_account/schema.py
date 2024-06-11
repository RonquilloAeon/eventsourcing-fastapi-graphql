import logging
import typing

from decimal import Decimal
from uuid import UUID

import strawberry
from strawberry import relay
from strawberry.relay import to_base64

from src.app.bank_accounts import BankAccounts
from src.entrypoints.api.common import graphql

logger = logging.getLogger(__name__)


@strawberry.input
class DepositFundsInput:
    bankAccount: relay.GlobalID
    amount: Decimal


@strawberry.input
class OpenBankAccountInput:
    email: str
    full_name: str


@strawberry.type
class BankAccountMutations:
    @strawberry.mutation
    def open(self, input: OpenBankAccountInput) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            id = accounts.open_account(input.full_name, input.email)

            return graphql.Success(
                entities=[to_base64("BankAccount", str(id))],
                is_message_displayable=False,
                message="OK",
            )
        except Exception as e:
            logger.info("Error opening an account: %s", e)

            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def deposit_funds(
        self,
        input: DepositFundsInput,
    ) -> graphql.MutationResponse:
        account_id = input.bankAccount.node_id
        accounts = BankAccounts()

        try:
            accounts.deposit_funds(str(account_id), input.amount)

            return graphql.Success(
                entities=[],
                is_message_displayable=True,
                message="Funds deposited",
            )
        except Exception as e:
            logger.info("Error depositing funds: %s", e)

            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def withdraw_funds(
        self, account_id: UUID, amount: Decimal
    ) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.withdraw_funds(debit_account_id=account_id, amount=amount)
            return accounts.get_account(account_id)
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def transfer_funds(
        self, account_id: UUID, to_account_id: UUID, amount: Decimal
    ) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.transfer_funds(
                debit_account_id=account_id,
                credit_account_id=to_account_id,
                amount=amount,
            )
            return accounts.get_account(account_id)
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def set_overdraft_limit(
        self, account_id: UUID, limit: Decimal
    ) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.set_overdraft_limit(account_id=account_id, overdraft_limit=limit)
            return accounts.get_account(account_id)
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def close_account(self, account_id: UUID) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.close_account(account_id)
            return accounts.get_account(account_id)
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)


@strawberry.type
class Mutation:
    @strawberry.field
    def bank_account(self) -> BankAccountMutations:
        return BankAccountMutations()


@strawberry.type
class BankAccount(relay.Node):
    id: relay.NodeID[UUID]
    balance: Decimal
    email: str
    full_name: str
    overdraft_limit: typing.Optional[Decimal] = None

    @classmethod
    def resolve_nodes(
        cls,
        *,
        info: strawberry.Info,
        node_ids: typing.Iterable[str],
        required: bool = False,
    ):
        nodes = []
        accounts = BankAccounts()

        for node_id in node_ids:
            try:
                account = accounts.get_account(UUID(node_id))

                instance = BankAccount(
                    id=account.id,
                    balance=account.balance,
                    email=account.email_address,
                    full_name=account.full_name,
                    overdraft_limit=account.overdraft_limit,
                )

                nodes.append(instance)
            except Exception:
                return None

        return nodes


@strawberry.type
class Query:
    bankAccount: BankAccount = relay.node()

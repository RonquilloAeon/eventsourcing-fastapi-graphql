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
class CloseBankAccountInput:
    bank_account: relay.GlobalID


@strawberry.input
class DepositFundsInput:
    bank_account: relay.GlobalID
    amount: Decimal


@strawberry.input
class OpenBankAccountInput:
    email: str
    full_name: str


@strawberry.input
class SetBankAccountOverdraftLimitInput:
    bank_account: relay.GlobalID
    limit: Decimal


@strawberry.input
class TransferBankAccountFundsInput:
    credit_bank_account: relay.GlobalID
    debit_bank_account: relay.GlobalID
    amount: Decimal


@strawberry.input
class WithdrawFundsFromBankAccountInput:
    bank_account: relay.GlobalID
    amount: Decimal


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
        account_id = input.bank_account.node_id
        accounts = BankAccounts()

        try:
            accounts.deposit_funds(UUID(account_id), input.amount)

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
        self, input: WithdrawFundsFromBankAccountInput
    ) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.withdraw_funds(UUID(input.bank_account.node_id), input.amount)

            return graphql.Success(
                entities=[],
                is_message_displayable=True,
                message="Funds withdrawn",
            )
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def transfer_funds(
        self, input: TransferBankAccountFundsInput
    ) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.transfer_funds(
                UUID(input.debit_bank_account.node_id),
                UUID(input.credit_bank_account.node_id),
                input.amount,
            )

            return graphql.Success(
                entities=[],
                is_message_displayable=True,
                message="Funds transferred",
            )
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def set_overdraft_limit(
        self, input: SetBankAccountOverdraftLimitInput
    ) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.set_overdraft_limit(UUID(input.bank_account.node_id), input.limit)

            return graphql.Success(
                entities=[],
                is_message_displayable=True,
                message="Overdraft limit set",
            )
        except Exception as e:
            return graphql.Error(message=e.__class__.__name__)

    @strawberry.mutation
    def close(self, input: CloseBankAccountInput) -> graphql.MutationResponse:
        accounts = BankAccounts()

        try:
            accounts.close_account(UUID(input.bank_account.node_id))

            return graphql.Success(
                entities=[],
                is_message_displayable=True,
                message="Bank account closed",
            )
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

from decimal import Decimal
from uuid import uuid4

import pytest

from src.app.bank_accounts import BankAccounts
from src.domain.exceptions import (
    AccountClosedError,
    AccountNotFoundError,
    InsufficientFundsError,
)


def test_bank_accounts():
    accounts = BankAccounts()

    # Check account not found error.
    with pytest.raises(AccountNotFoundError):
        accounts.get_balance(uuid4())

    # Create an account.
    account_id1 = accounts.open_account(
        full_name="Alice",
        email_address="alice@example.com",
    )

    # Check balance.
    assert accounts.get_balance(account_id1) == Decimal("0.00")

    # Deposit funds.
    accounts.deposit_funds(
        credit_account_id=account_id1,
        amount=Decimal("200.00"),
    )

    # Check balance.
    assert accounts.get_balance(account_id1) == Decimal("200.00")

    # Withdraw funds.
    accounts.withdraw_funds(
        debit_account_id=account_id1,
        amount=Decimal("50.00"),
    )

    # # Check balance.
    assert accounts.get_balance(account_id1) == Decimal("150.00")

    # Fail to withdraw funds - insufficient funds.
    with pytest.raises(InsufficientFundsError):
        accounts.withdraw_funds(
            debit_account_id=account_id1,
            amount=Decimal("151.00"),
        )

    # Check balance - should be unchanged.
    assert accounts.get_balance(account_id1) == Decimal("150.00")

    # Create another account.
    account_id2 = accounts.open_account(
        full_name="Bob",
        email_address="bob@example.com",
    )

    # Transfer funds.
    accounts.transfer_funds(
        debit_account_id=account_id1,
        credit_account_id=account_id2,
        amount=Decimal("100.00"),
    )

    # Check balances.
    assert accounts.get_balance(account_id1) == Decimal("50.00")
    assert accounts.get_balance(account_id2) == Decimal("100.00")

    # Fail to transfer funds - insufficient funds.
    with pytest.raises(InsufficientFundsError):
        accounts.transfer_funds(
            debit_account_id=account_id1,
            credit_account_id=account_id2,
            amount=Decimal("1000.00"),
        )

    # Check balances - should be unchanged.
    assert accounts.get_balance(account_id1) == Decimal("50.00")
    assert accounts.get_balance(account_id2) == Decimal("100.00")

    # Close account.
    accounts.close_account(account_id1)

    # Fail to transfer funds - account closed.
    with pytest.raises(AccountClosedError):
        accounts.transfer_funds(
            debit_account_id=account_id1,
            credit_account_id=account_id2,
            amount=Decimal("50.00"),
        )

    # Fail to transfer funds - account closed.
    with pytest.raises(AccountClosedError):
        accounts.transfer_funds(
            debit_account_id=account_id2,
            credit_account_id=account_id1,
            amount=Decimal("50.00"),
        )

    # Fail to withdraw funds - account closed.
    with pytest.raises(AccountClosedError):
        accounts.withdraw_funds(
            debit_account_id=account_id1,
            amount=Decimal("1.00"),
        )

    # Fail to deposit funds - account closed.
    with pytest.raises(AccountClosedError):
        accounts.deposit_funds(
            credit_account_id=account_id1,
            amount=Decimal("1000.00"),
        )

    # Check balance - should be unchanged.
    assert accounts.get_balance(account_id1) == Decimal("50.00")

    # Check overdraft limit.
    assert accounts.get_overdraft_limit(account_id2) == Decimal("0.00")

    # Set overdraft limit.
    accounts.set_overdraft_limit(
        account_id=account_id2,
        overdraft_limit=Decimal("500.00"),
    )

    # Can't set negative overdraft limit.
    with pytest.raises(AssertionError):
        accounts.set_overdraft_limit(
            account_id=account_id2,
            overdraft_limit=Decimal("-500.00"),
        )

    # Check overdraft limit.
    assert accounts.get_overdraft_limit(account_id2), Decimal("500.00")

    # Withdraw funds.
    accounts.withdraw_funds(
        debit_account_id=account_id2,
        amount=Decimal("500.00"),
    )

    # Check balance - should be overdrawn.
    assert accounts.get_balance(account_id2) == Decimal("-400.00")

    # Fail to withdraw funds - insufficient funds.
    with pytest.raises(InsufficientFundsError):
        accounts.withdraw_funds(
            debit_account_id=account_id2,
            amount=Decimal("101.00"),
        )

    # Fail to set overdraft limit - account closed.
    with pytest.raises(AccountClosedError):
        accounts.set_overdraft_limit(
            account_id=account_id1,
            overdraft_limit=Decimal("500.00"),
        )

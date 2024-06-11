async def test_bank_account_open_and_deposit_funds(fake, graphql_test_client):
    # Open bank account
    input_data = {
        "email": fake.email(),
        "fullName": fake.name(),
    }

    response = await graphql_test_client(
        """
        mutation ($input: OpenBankAccountInput!) {
            bankAccount {
                open(input: $input) {
                    ... on Success {
                        entities
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["open"]
    bank_account_global_id = data["entities"][0]

    # Query for bank account
    response = await graphql_test_client(
        """
        query ($id: GlobalID!) {
            bankAccount(id: $id) {
                id
                balance
                email
                fullName
                overdraftLimit
            }
        }
        """,
        variables={"id": bank_account_global_id},
    )

    data = response.json()["data"]["bankAccount"]

    expected_data = {
        "id": bank_account_global_id,
        "balance": "0.00",
        "email": input_data["email"],
        "fullName": input_data["fullName"],
        "overdraftLimit": "0.00",
    }

    assert data == expected_data

    # Deposit funds
    input_data = {"bankAccount": bank_account_global_id, "amount": "5.00"}

    response = await graphql_test_client(
        """
        mutation ($input: DepositFundsInput!) {
            bankAccount {
                depositFunds(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["depositFunds"]

    assert data["message"] == "Funds deposited"

    # Query for bank account again
    response = await graphql_test_client(
        """
        query ($id: GlobalID!) {
            bankAccount(id: $id) {
                balance
            }
        }
        """,
        variables={"id": bank_account_global_id},
    )

    data = response.json()["data"]["bankAccount"]

    expected_data = {
        "balance": "5.00",
    }

    assert data == expected_data


async def test_bank_account_management(fake, graphql_test_client):
    # Open bank account
    input_data = {
        "email": fake.email(),
        "fullName": fake.name(),
    }

    response = await graphql_test_client(
        """
        mutation ($input: OpenBankAccountInput!) {
            bankAccount {
                open(input: $input) {
                    ... on Success {
                        entities
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["open"]
    bank_account_global_id = data["entities"][0]

    # Deposit funds
    input_data = {"bankAccount": bank_account_global_id, "amount": "50.50"}

    await graphql_test_client(
        """
        mutation ($input: DepositFundsInput!) {
            bankAccount {
                depositFunds(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    # Withdraw funds
    input_data = {"bankAccount": bank_account_global_id, "amount": "30.00"}

    response = await graphql_test_client(
        """
        mutation ($input: WithdrawFundsFromBankAccountInput!) {
            bankAccount {
                withdrawFunds(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["withdrawFunds"]

    assert data["message"] == "Funds withdrawn"

    # Query bank account
    response = await graphql_test_client(
        """
        query ($id: GlobalID!) {
            bankAccount(id: $id) {
                balance
            }
        }
        """,
        variables={"id": bank_account_global_id},
    )

    data = response.json()["data"]["bankAccount"]

    expected_data = {
        "balance": "20.50",
    }

    assert data == expected_data


async def test_bank_account_funds_transfer(fake, graphql_test_client):
    # Open bank account A
    input_data = {
        "email": fake.email(),
        "fullName": fake.name(),
    }

    response = await graphql_test_client(
        """
        mutation ($input: OpenBankAccountInput!) {
            bankAccount {
                open(input: $input) {
                    ... on Success {
                        entities
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["open"]
    bank_account_a_global_id = data["entities"][0]

    input_data = {"bankAccount": bank_account_a_global_id, "amount": "500.00"}

    await graphql_test_client(
        """
        mutation ($input: DepositFundsInput!) {
            bankAccount {
                depositFunds(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    # Open bank account B
    input_data = {
        "email": fake.email(),
        "fullName": fake.name(),
    }

    response = await graphql_test_client(
        """
        mutation ($input: OpenBankAccountInput!) {
            bankAccount {
                open(input: $input) {
                    ... on Success {
                        entities
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["open"]
    bank_account_b_global_id = data["entities"][0]

    # Transfer from account A to account B
    input_data = {
        "debitBankAccount": bank_account_a_global_id,
        "creditBankAccount": bank_account_b_global_id,
        "amount": "240.00",
    }

    response = await graphql_test_client(
        """
        mutation ($input: TransferBankAccountFundsInput!) {
            bankAccount {
                transferFunds(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["transferFunds"]

    assert data["message"] == "Funds transferred"

    # Query account A
    response = await graphql_test_client(
        """
        query ($id: GlobalID!) {
            bankAccount(id: $id) {
                balance
            }
        }
        """,
        variables={"id": bank_account_a_global_id},
    )

    data = response.json()["data"]["bankAccount"]

    expected_data = {
        "balance": "260.00",
    }

    assert data == expected_data

    # Query account B
    response = await graphql_test_client(
        """
        query ($id: GlobalID!) {
            bankAccount(id: $id) {
                balance
            }
        }
        """,
        variables={"id": bank_account_b_global_id},
    )

    data = response.json()["data"]["bankAccount"]

    expected_data = {
        "balance": "240.00",
    }

    assert data == expected_data


async def test_bank_account_set_overdraft_limit(fake, graphql_test_client):
    # Open bank account
    input_data = {
        "email": fake.email(),
        "fullName": fake.name(),
    }

    response = await graphql_test_client(
        """
        mutation ($input: OpenBankAccountInput!) {
            bankAccount {
                open(input: $input) {
                    ... on Success {
                        entities
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["open"]
    bank_account_global_id = data["entities"][0]

    # Set overdraft limit
    input_data = {"bankAccount": bank_account_global_id, "limit": "300.00"}

    response = await graphql_test_client(
        """
        mutation ($input: SetBankAccountOverdraftLimitInput!) {
            bankAccount {
                setOverdraftLimit(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["setOverdraftLimit"]

    assert data["message"] == "Overdraft limit set"

    # Query bank account
    response = await graphql_test_client(
        """
        query ($id: GlobalID!) {
            bankAccount(id: $id) {
                overdraftLimit
            }
        }
        """,
        variables={"id": bank_account_global_id},
    )

    data = response.json()["data"]["bankAccount"]

    expected_data = {
        "overdraftLimit": "300.00",
    }

    assert data == expected_data


async def test_bank_account_close(fake, graphql_test_client):
    # Open bank account
    input_data = {
        "email": fake.email(),
        "fullName": fake.name(),
    }

    response = await graphql_test_client(
        """
        mutation ($input: OpenBankAccountInput!) {
            bankAccount {
                open(input: $input) {
                    ... on Success {
                        entities
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["open"]
    bank_account_global_id = data["entities"][0]

    # Close account
    input_data = {"bankAccount": bank_account_global_id}

    response = await graphql_test_client(
        """
        mutation ($input: CloseBankAccountInput!) {
            bankAccount {
                close(input: $input) {
                    ... on Success {
                        entities
                        message
                    }
                    ... on Error {
                        message
                    }
                }
            }
        }
        """,
        variables={"input": input_data},
    )

    data = response.json()["data"]["bankAccount"]["close"]

    assert data["message"] == "Bank account closed"

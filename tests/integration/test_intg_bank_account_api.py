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

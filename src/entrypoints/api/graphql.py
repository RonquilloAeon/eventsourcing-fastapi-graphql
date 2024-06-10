import strawberry
from strawberry.fastapi import GraphQLRouter

from src.entrypoints.api.bank_account import schema as bank_account_schema


@strawberry.type
class Mutation(bank_account_schema.Mutation):
    ...


@strawberry.type
class Query(bank_account_schema.Query):
    ...


schema = strawberry.federation.Schema(
    Query,
    Mutation,
    enable_federation_2=True,
)
router = GraphQLRouter(schema)

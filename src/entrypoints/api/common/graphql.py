import typing

import strawberry
from strawberry.relay import GlobalID
from strawberry.scalars import JSON


@strawberry.type
class Success:
    entities: list[GlobalID]
    is_message_displayable: bool
    message: str

    data: JSON | None = None


@strawberry.type
class Error:
    message: str


OperationUnion = strawberry.union(
    "MutationResponse",
    types=(Error, Success),
)
MutationResponse = typing.Annotated[
    typing.Union[Error, Success],
    OperationUnion,
]

import pytest
from faker import Faker


@pytest.fixture
def fake() -> Faker:
    return Faker()

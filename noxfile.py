import nox
from nox_poetry import session

nox.options.sessions = ["test_integration"]

TEST_ENV_VARS = {
    "DM_LOG_LEVEL": "info",
    "PERSISTENCE_MODULE": "eventsourcing.postgres",
    "POSTGRES_DBNAME": "test_bank",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PASSWORD": "pgpass",
    "POSTGRES_PORT": "4432",
    "POSTGRES_USER": "esdemo",
}


@session(python="3.12", reuse_venv=True)
def test_integration(local_session):
    """Run all integration tests"""
    local_session.run_always("poetry", "install", external=True)

    local_session.run(
        "pytest",
        "--disable-warnings",
        "tests/integration",
        *local_session.posargs,
        env=TEST_ENV_VARS,
    )

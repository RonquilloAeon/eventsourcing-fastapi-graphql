# example-fastapi
Example of eventsourcing with FastAPI and Strawberry GraphQL

## Getting Started
1. Install dependencies
```zsh
pyenv install 3.12
pip install nox
pip install nox-poetry
pyenv local 3.12
poetry install
pre-commit install
```
2. Start FastAPI process
```zsh
docker compose up
```
3. Open local API docs [http://localhost:5000/docs](http://localhost:5000/docs)

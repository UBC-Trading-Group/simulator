# Backend Tests

The backend test suite is split into fast, pure-Python unit tests and slow,
end-to-end API tests that exercise the running FastAPI service plus backing
datastores.

## Directory layout

| Path                | Description                                        |
| ------------------- | -------------------------------------------------- |
| `tests/unit`        | Deterministic unit tests with no external services |
| `tests/api`         | API smoke/contract tests that hit HTTP endpoints   |
| `tests/api/conftest.py` | Shared API fixtures and helpers                |

Both suites use pytest markers:

- `@pytest.mark.unit` — run with `pytest -m unit`
- `@pytest.mark.api` — run with `pytest -m api` (requires a live API)

BOTH TESTS ACTUALLY REQUIRE LIVE API LOL (this is a todo)
## Running tests locally

All helper commands live under `backend/scripts/run_tests.sh`.

### Unit tests

```bash
cd backend
uv run pytest -m unit
```

### API tests

API tests need a reachable FastAPI instance and data services. Point the tests
to the running base URL via `API_BASE_URL` (defaults to `http://api:8000`,
which matches the docker-compose service name).

```bash
cd backend
API_BASE_URL=http://localhost:8000 uv run pytest -m api
```

### All tests

```bash
cd backend
API_BASE_URL=http://localhost:8000 uv run pytest
```

### Coverage

```bash
cd backend
uv run pytest --cov=app --cov-report=html
```

## Adding new tests

1. Choose the right directory (`tests/unit` for pure Python, `tests/api` for HTTP).
2. Import shared fixtures from `tests/api/conftest.py`.
3. Add the appropriate marker at file or test level.

API tests should rely on the provided `http_client` fixture rather than the
FastAPI `TestClient` so that they always traverse the real network stack and
exercise migrations, middleware, and persistence layers.



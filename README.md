# developer-challenge
developer challenge to build a rest api pulling data from an external service

## Architecture

```
hr_mock_service/   -> "System A": a tiny Flask app serving synthetic HR
                       employee data (including deliberately awkward
                       records) over a real REST endpoint.
config/, sync/      -> "System B" + the integration layer: a Django Ninja
                       app that consumes the HR API, validates/transforms
                       each record, and upserts it into a SQLite table.
```

Two independent services, talking over HTTP — closer to how HR and
payroll systems actually integrate than reading a local file would be.

| Layer | Location |
|---|---|
| Models (`Employee`, `SyncException`) | `sync/models.py` |
| Ninja schemas | `sync/schemas.py` |
| Validation / transform rules | `sync/transform.py` |
| Sync orchestration (fetch → validate → upsert) | `sync/services.py` |
| API endpoints | `sync/api.py` |
| CLI entry point | `sync/management/commands/sync_employees.py` |
| Tests | `sync/tests/` |
| Mock HR REST API | `hr_mock_service/app.py` |

## Endpoints

- `GET /api/employees/{employee_id}` — look up an employee in the
  consolidated store. 404 if not found.
- `POST /api/sync` — fetch from the HR API, validate/transform, upsert
  into the store. Returns a run report (`fetched/created/updated/failed`
  + error messages), and never raises just because some records were bad.

## Running locally (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r hr_mock_service/requirements.txt

# terminal 1 — the mock HR system
python hr_mock_service/app.py            # http://localhost:8001/employees

# terminal 2 — the integration service
cp .env.example .env                     # HR_API_URL already points at :8001
python manage.py migrate
python manage.py runserver 8000
```

Then, from a third terminal:

```bash
curl -X POST http://localhost:8000/api/sync          # run the sync
curl -X POST http://localhost:8000/api/sync          # run it again — no duplicates
curl http://localhost:8000/api/employees/EMP10452     # look one up

# or via the CLI, without going through the API:
python manage.py sync_employees
```

## Running with Docker

```bash
docker compose up --build
curl -X POST http://localhost:8000/api/sync
curl http://localhost:8000/api/employees/EMP10452
```

This starts two containers: `hr_mock` (the mock HR REST API on `:8001`)
and `web` (the integration service on `:8000`), talking to each other
over the compose network. SQLite data persists in the `sqlite_data`
volume across container restarts.

## Tests

```bash
pip install -r requirements.txt
pytest -v
```
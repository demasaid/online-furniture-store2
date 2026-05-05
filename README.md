# Online Furniture Store

Starter backend project for the Advanced Programming final project.

## Stack

- Python
- FastAPI
- Pytest

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test

```bash
pytest --cov=app --cov-report=term-missing
```

## Testing Strategy

- Unit tests:
  - `tests/test_inventory_service.py`
  - Validates service-level business logic in isolation.
- Integration tests:
  - `tests/test_api.py`
  - Validates API endpoints and their interaction with services.
- Regression tests:
  - `tests/test_regression_inventory_flow.py`
  - `tests/test_regression_checkout_flow.py`
  - Protects critical lifecycle flows from future breakage.

## Implemented in v0

- Furniture domain model (`Furniture` + 5 types)
- Inventory service (add/remove/update/list/search)
- Basic API endpoints:
  - `GET /health`
  - `POST /users/register`
  - `POST /users/login`
  - `GET /users/{user_id}`
  - `GET /furniture`
  - `GET /furniture/{item_id}`
  - `POST /furniture`
  - `PUT /furniture/{item_id}`
  - `PUT /inventory/{item_id}/quantity`
  - `DELETE /furniture/{item_id}`
  - `POST /cart/{user_id}/items`
  - `DELETE /cart/{user_id}/items/{item_id}`
  - `GET /cart/{user_id}`
  - `POST /checkout/{user_id}`
  - `GET /orders/{user_id}`
  - `PUT /orders/{user_id}/{order_id}/status`
- Unit, integration, and regression tests

## Next Steps

- Add promotions strategies (different discount rules)
- Add persistence layer (SQLite/JSON)
- Add CI workflow (tests + lint + coverage)

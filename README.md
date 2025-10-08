# FastAPI CRUD with Authentication

This project is a FastAPI-based REST API that demonstrates CRUD operations for items, with user authentication using Argon2 password hashing. SQLAlchemy is used for ORM, and SQLite is the default database.

## Features

- User registration and authentication (Basic Auth)
- CRUD operations for items (Create, Read, Update, Delete)
- Protected endpoints (only authenticated users can access item routes)
- Secure password storage using Argon2

## Project Structure

```
fastapi_crud/
├── .gitignore
├── auth.py
├── crud.py
├── database.py
├── main.py
├── models.py
├── README.md
├── schemas.py
├── requirements.txt
```

## Setup & Usage

### 1. Create a Virtual Environment

Open a terminal in your project folder and run:

```sh
python -m venv venv
```

Activate the virtual environment:

- On **Windows**:
  ```sh
  venv\Scripts\activate
  ```
- On **macOS/Linux**:
  ```sh
  source venv/bin/activate
  ```

### 2. Install Dependencies

```sh
pip install fastapi uvicorn sqlalchemy passlib[argon2]
```

### 3. Run the API Server

```sh
uvicorn main:app --reload
```

## API Endpoints

- `POST /auth/register` — Register a new user
- `POST /items/` — Create an item (requires authentication)
- `GET /items/` — List items (requires authentication)
- `GET /items/{item_id}` — Get item by ID (requires authentication)
- `PUT /items/{item_id}` — Update item (requires authentication)
- `DELETE /items/{item_id}` — Delete item (requires authentication)

## Example Request

```sh
curl -X POST "http://127.0.0.1:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "user1", "password": "pass123"}'
```

## Notes

- All item endpoints require HTTP Basic authentication.
- Passwords are securely hashed using Argon2.
- The database is SQLite (`test.db`) by default.

## License

MIT
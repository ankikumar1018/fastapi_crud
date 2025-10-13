from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# --- Setup test database (SQLite in-memory) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./unit_test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Recreate tables before each test run
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency override for DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a TestClient instance
client = TestClient(app)


# --- Utility function ---
def create_test_user(username="testuser", password="testpass"):
    response = client.post(
        "/auth/signup",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()


# --- Test Cases ---

def test_signup_success():
    """✅ Test creating a new user"""
    response = client.post("/auth/signup", json={"username": "alice", "password": "wonderland"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["message"] == "User created successfully"


def test_signup_duplicate_username():
    """❌ Test duplicate user creation"""
    client.post("/auth/signup", json={"username": "bob", "password": "builder"})
    response = client.post("/auth/signup", json={"username": "bob", "password": "builder"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_login_and_me_endpoint():
    """✅ Test /auth/me protected route"""
    create_test_user("john", "doe123")
    response = client.get("/auth/me", auth=("john", "doe123"))
    assert response.status_code == 200
    assert response.json()["username"] == "john"


def test_change_password_success():
    """✅ Test password change"""
    create_test_user("changepass", "old123")
    response = client.put(
        "/auth/change-password",
        json={"old_password": "old123", "new_password": "new123"},
        auth=("changepass", "old123")
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    # Verify new password works
    response = client.get("/auth/me", auth=("changepass", "new123"))
    assert response.status_code == 200


def test_change_password_wrong_old_password():
    """❌ Test incorrect old password"""
    create_test_user("wrongpass", "abcd")
    response = client.put(
        "/auth/change-password",
        json={"old_password": "wrong", "new_password": "xyz"},
        auth=("wrongpass", "abcd")
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Old password is incorrect"


# ------------------------
# CRUD Item Tests
# ------------------------

def test_create_and_read_items():
    """✅ Test creating and fetching items"""
    create_test_user("itemuser", "pass123")

    # Create item
    response = client.post(
        "/items/",
        json={"name": "Laptop", "description": "Gaming", "price": 1200},
        auth=("itemuser", "pass123"),
    )
    assert response.status_code == 200
    item_data = response.json()
    assert item_data["name"] == "Laptop"

    # Fetch all items
    response = client.get("/items/", auth=("itemuser", "pass123"))
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Laptop"


def test_update_item():
    """✅ Test updating item"""
    create_test_user("updater", "secret")
    # Create item
    response = client.post(
        "/items/",
        json={"name": "Phone", "description": "Old", "price": 500},
        auth=("updater", "secret"),
    )
    item_id = response.json()["id"]

    # Update item
    response = client.put(
        f"/items/{item_id}",
        json={"description": "New Model"},
        auth=("updater", "secret"),
    )
    assert response.status_code == 200
    assert response.json()["description"] == "New Model"


def test_delete_item():
    """✅ Test deleting item"""
    create_test_user("deleter", "passdel")
    # Create item
    response = client.post(
        "/items/",
        json={"name": "Book", "description": "Novel", "price": 100},
        auth=("deleter", "passdel"),
    )
    item_id = response.json()["id"]

    # Delete it
    response = client.delete(f"/items/{item_id}", auth=("deleter", "passdel"))
    assert response.status_code == 200
    assert response.json()["message"] == "Item deleted successfully"

    # Verify it's gone
    response = client.get(f"/items/{item_id}", auth=("deleter", "passdel"))
    assert response.status_code == 404

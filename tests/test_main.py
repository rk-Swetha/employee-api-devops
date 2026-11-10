import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[main.get_db] = override_get_db

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Employee Management API is running"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_employee(client):
    response = client.post(
        "/employees",
        json={
            "name": "Swetha",
            "role": "DevOps Engineer",
            "department": "Engineering",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Swetha"


def test_list_employees(client):
    client.post(
        "/employees",
        json={
            "name": "Swetha",
            "role": "DevOps Engineer",
            "department": "Engineering",
        },
    )

    response = client.get("/employees")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Swetha"


def test_get_employee_not_found(client):
    response = client.get("/employees/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


def test_delete_employee(client):
    create_response = client.post(
        "/employees",
        json={
            "name": "Swetha",
            "role": "DevOps Engineer",
            "department": "Engineering",
        },
    )
    employee_id = create_response.json()["id"]

    response = client.delete(f"/employees/{employee_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted successfully"

    get_response = client.get(f"/employees/{employee_id}")
    assert get_response.status_code == 404

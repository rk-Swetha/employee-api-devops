from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)


def setup_function():
    main.employees.clear()
    main.next_employee_id = 1


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Employee Management API is running"
    )


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_employee():
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


def test_list_employees():
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


def test_employee_not_found():
    response = client.get("/employees/999")

    assert response.status_code == 404


def test_delete_employee():
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
    assert client.get(f"/employees/{employee_id}").status_code == 404
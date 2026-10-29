from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Employee Management API")

# Data is stored in memory for this beginner project.
employees: dict[int, dict] = {}
next_employee_id = 1


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    department: str = Field(min_length=1, max_length=100)


class Employee(EmployeeCreate):
    id: int


@app.get("/")
def home():
    return {"message": "Employee Management API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/employees", response_model=Employee, status_code=201)
def create_employee(employee: EmployeeCreate):
    global next_employee_id

    new_employee = {
        "id": next_employee_id,
        **employee.model_dump(),
    }

    employees[next_employee_id] = new_employee
    next_employee_id += 1

    return new_employee


@app.get("/employees", response_model=list[Employee])
def list_employees():
    return list(employees.values())


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int):
    employee = employees.get(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")

    del employees[employee_id]

    return {"message": "Employee deleted successfully"}
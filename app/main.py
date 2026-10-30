from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app import models, schemas
from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables when the application starts.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {"message": "Employee Management API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/employees",
    response_model=schemas.EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
):
    db_employee = models.Employee(**employee.model_dump())

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


@app.get(
    "/employees",
    response_model=list[schemas.EmployeeResponse],
)
def list_employees(db: Session = Depends(get_db)):
    statement = select(models.Employee).order_by(models.Employee.id)
    return db.scalars(statement).all()


@app.get(
    "/employees/{employee_id}",
    response_model=schemas.EmployeeResponse,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.get(models.Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.get(models.Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}

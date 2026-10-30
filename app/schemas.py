
from pydantic import BaseModel, ConfigDict


class EmployeeCreate(BaseModel):
    name: str
    role: str
    department: str


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: str
    department: str

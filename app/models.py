from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EmployeeIn(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=200)
    department: str = Field(..., min_length=1, max_length=200)
    salary: int = Field(..., ge=0)
    joining_date: date
    skills: List[str] = Field(default_factory=list)


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    department: Optional[str] = Field(None, min_length=1, max_length=200)
    salary: Optional[int] = Field(None, ge=0)
    joining_date: Optional[date] = None
    skills: Optional[List[str]] = None


class EmployeeOut(EmployeeIn):
    model_config = ConfigDict(from_attributes=True)
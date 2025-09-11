from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from .models import EmployeeIn, EmployeeUpdate, EmployeeOut
from .db import get_employees_collection
from .employees_repo import EmployeesRepository

router = APIRouter(prefix="/employees", tags=["employees"])


def get_repo() -> EmployeesRepository:
    return EmployeesRepository(get_employees_collection())


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeIn, repo: EmployeesRepository = Depends(get_repo)) -> Any:
    return await repo.create_employee(payload.model_dump())


@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str, repo: EmployeesRepository = Depends(get_repo)) -> Any:
    doc = await repo.get_by_employee_id(employee_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return doc


@router.put("/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, updates: EmployeeUpdate, repo: EmployeesRepository = Depends(get_repo)) -> Any:
    update_dict: Dict[str, Any] = {k: v for k, v in updates.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    return await repo.update_employee(employee_id, update_dict)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: str, repo: EmployeesRepository = Depends(get_repo)) -> None:
    await repo.delete_employee(employee_id)


@router.get("", response_model=List[EmployeeOut])
async def list_by_department(
    department: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    repo: EmployeesRepository = Depends(get_repo),
) -> Any:
    items, _ = await repo.list_by_department(department, page, page_size)
    return items


@router.get("/avg-salary")
async def average_salary(repo: EmployeesRepository = Depends(get_repo)) -> Any:
    return await repo.average_salary_by_department()


@router.get("/search")
async def search_by_skill(skill: str, repo: EmployeesRepository = Depends(get_repo)) -> Any:
    return await repo.search_by_skill(skill)
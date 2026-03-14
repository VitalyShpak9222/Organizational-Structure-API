from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.deps import get_db
from app.schemas import Employee, EmployeeCreate
from app.services import employee as service

router = APIRouter(prefix="/employees", tags=["employees"])

"""
Создает нового сотрудника.

- **department_id**: ID подразделения (обязательный query параметр)
- **full_name**: полное имя сотрудника
- **position**: должность
- **hired_at**: дата найма (опционально)
"""
@router.post("/", 
             response_model=Employee, 
             status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate,
    department_id: int = Query(..., description="ID подразделения"),
    db: Session = Depends(get_db)
):

    return service.create_employee(db, department_id, employee)

# Получить сотрудника по ID.
@router.get("/{employee_id}", 
            response_model=Employee)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return employee

# Обновляет данные сотрудника.
@router.patch("/{employee_id}", 
              response_model=Employee)
def update_employee(
    employee_id: int,
    full_name: Optional[str] = None,
    position: Optional[str] = None,
    hired_at: Optional[date] = None,
    db: Session = Depends(get_db)
):
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if position is not None:
        update_data["position"] = position
    if hired_at is not None:
        update_data["hired_at"] = hired_at
    
    employee = service.update_employee(db, employee_id, update_data)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return employee

# Удаляет сотрудника.
@router.delete("/{employee_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    deleted = service.delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return None

# Перемещает сотрудника в другое подразделение.
@router.post("/{employee_id}/move",
             response_model=Employee)
def move_employee(
    employee_id: int,
    new_department_id: int = Query(..., description="ID нового подразделения"),
    db: Session = Depends(get_db)
):
    employee = service.move_employee_to_department(db, employee_id, new_department_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сотрудник с ID {employee_id} не найден"
        )
    return employee
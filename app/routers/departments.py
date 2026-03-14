from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db
from app.schemas import (
    Department, DepartmentCreate, DepartmentUpdate,
    Employee, EmployeeCreate, DepartmentNode
)
from app.services import department as service
from app.services import employee as emp_service

router = APIRouter(prefix="/departments", tags=["departments"])

"""
Создает новое подразделение.

- **name**: название подразделения (не пустое, уникальное в пределах родителя)
- **parent_id**: ID родительского подразделения (опционально)
"""
@router.post("/", 
             response_model=Department, 
             status_code=status.HTTP_201_CREATED)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
):
    return service.create_department(db, department)

"""
Получает подразделение по ID с вложенными подразделениями и сотрудниками.

- **depth**: глубина вложенности (макс. 5)
- **include_employees**: включать ли сотрудников в ответ
"""
@router.get("/{department_id}", 
            response_model=DepartmentNode)
def get_department(
    department_id: int,
    depth: int = Query(1, ge=1, le=5, description="Глубина вложенных подразделений (1-5)"),
    include_employees: bool = Query(True, description="Включать сотрудников в ответ"),
    db: Session = Depends(get_db)
):
    department = service.get_department_with_tree(
        db, department_id, depth, include_employees
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Подразделение с ID {department_id} не найдено"
        )
    return department

"""
Обновляет подразделение.

- **name**: новое название (опционально)
- **parent_id**: новый родитель (опционально, null для корневого)
"""
@router.patch("/{department_id}", 
              response_model=Department)
def update_department(
    department_id: int,
    update_data: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    department = service.update_department(db, department_id, update_data)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Подразделение с ID {department_id} не найдено"
        )
    return department

"""
Удаляет подразделение.

- **mode**: режим удаления
    - `cascade` - удалить всё (подразделение, сотрудников, дочерние)
    - `reassign` - удалить подразделение, сотрудников перевести в другое
- **reassign_to_department_id**: ID подразделения для перевода сотрудников (обязателен при mode=reassign)
"""
@router.delete("/{department_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    mode: str = Query(..., pattern="^(cascade|reassign)$"),
    reassign_to_department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    if mode == "reassign" and reassign_to_department_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reassign_to_department_id обязателен при mode=reassign"
        )
    
    deleted = service.delete_department(db, department_id, mode, reassign_to_department_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Подразделение с ID {department_id} не найдено"
        )
    
    return None

# Получает всех сотрудников подразделения.
@router.get("/{department_id}/employees",
            response_model=List[Employee])
def get_department_employees(
    department_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("created_at", pattern="^(created_at|full_name)$"),
    db: Session = Depends(get_db)
):
    department = service.get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Подразделение с ID {department_id} не найдено"
        )
    
    return emp_service.get_employees_by_department(db, department_id, skip, limit, sort_by)

# Создает сотрудника в указанном подразделении.
@router.post("/{department_id}/employees/",
             response_model=Employee,
             status_code=status.HTTP_201_CREATED)
def create_department_employee(
    department_id: int,
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    return emp_service.create_employee(db, department_id, employee)
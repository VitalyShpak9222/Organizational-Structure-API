from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models import Employee, Department
from app.schemas import EmployeeCreate


# Создает сотрудника в подразделении.
def create_employee(
    db: Session, 
    department_id: int, 
    employee_data: EmployeeCreate
) -> Employee:
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Подразделение с ID {department_id} не найдено"
        )
    
    db_employee = Employee(
        department_id=department_id,
        **employee_data.model_dump()
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return db_employee

# Получает всех сотрудников подразделения с сортировкой.
def get_employees_by_department(
    db: Session, 
    department_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at"
) -> List[Employee]:
    query = db.query(Employee).filter(Employee.department_id == department_id)
    
    if sort_by == "full_name":
        query = query.order_by(Employee.full_name)
    else:
        query = query.order_by(Employee.created_at)
    
    return query.offset(skip).limit(limit).all()


# Получает сотрудника по ID.
def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    return db.get(Employee, employee_id)


# Обновляет данные сотрудника.
def update_employee(
    db: Session, 
    employee_id: int, 
    employee_data: dict
) -> Optional[Employee]:
    employee = db.get(Employee, employee_id)
    if not employee:
        return None
    
    for field, value in employee_data.items():
        if value is not None:
            setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    return employee

# Удаляет сотрудника.
def delete_employee(db: Session, employee_id: int) -> bool:
    employee = db.get(Employee, employee_id)
    if not employee:
        return False
    
    db.delete(employee)
    db.commit()
    return True

# Перемещает сотрудника в другое подразделение.
def move_employee_to_department(
    db: Session,
    employee_id: int,
    new_department_id: int
) -> Optional[Employee]:
    employee = db.get(Employee, employee_id)
    if not employee:
        return None
    
    department = db.get(Department, new_department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Подразделение с ID {new_department_id} не найдено"
        )
    
    employee.department_id = new_department_id
    db.commit()
    db.refresh(employee)
    
    return employee
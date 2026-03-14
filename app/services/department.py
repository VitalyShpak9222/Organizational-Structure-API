from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any

from app.models import Department, Employee
from app.schemas import DepartmentCreate, DepartmentUpdate
from app.services import employee as employee_service

# Создает новое подразделение с проверками.
def create_department(db: Session, department_data: DepartmentCreate) -> Department:
    if department_data.parent_id:
        parent = db.get(Department, department_data.parent_id)

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Родительское подразделение с ID {department_data.parent_id} не найдено"
            )
    
    existing = db.query(Department).filter(
        Department.name == department_data.name,
        Department.parent_id == department_data.parent_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Подразделение с именем '{department_data.name}' уже существует в этом родителе"
        )
    
    db_dept = Department(**department_data.model_dump())
    db.add(db_dept)
    
    try:
        db.commit()
        db.refresh(db_dept)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка целостности данных"
        )
    
    return db_dept

# Получает подразделение по ID.
def get_department(db: Session, department_id: int) -> Optional[Department]:
    return db.get(Department, department_id)

# Получает подразделение с деревом до указанной глубины.
def get_department_with_tree(
    db: Session, 
    department_id: int, 
    depth: int = 1,
    include_employees: bool = True
) -> Optional[Dict[str, Any]]:
    query = db.query(Department).filter(Department.id == department_id)
    
    if include_employees:
        query = query.options(joinedload(Department.employees))
    
    department = query.first()
    
    if not department:
        return None

    result = {
        "id": department.id,
        "name": department.name,
        "parent_id": department.parent_id,
        "created_at": department.created_at,
        "employees": [],
        "children": []
    }
    
    if include_employees:
        result["employees"] = sorted(
            department.employees,
            key=lambda e: e.created_at or e.full_name
        )
    
    if depth > 1:
        children = db.query(Department).filter(
            Department.parent_id == department_id
        ).all()
        
        for child in children:
            child_tree = get_department_with_tree(db, child.id, depth - 1, include_employees)
            if child_tree:
                result["children"].append(child_tree)
    
    return result

# Обновляет подразделение с проверками.
def update_department(
    db: Session, 
    department_id: int, 
    update_data: DepartmentUpdate
) -> Optional[Department]:
    department = db.get(Department, department_id)

    if not department:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if "parent_id" in update_dict and update_dict["parent_id"] != department.parent_id:
        _check_cycle(db, department_id, update_dict["parent_id"])
    
    if "name" in update_dict and update_dict["name"] != department.name:
        parent_id = update_dict.get("parent_id", department.parent_id)
        existing = db.query(Department).filter(
            Department.name == update_dict["name"],
            Department.parent_id == parent_id,
            Department.id != department_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Подразделение с таким именем уже существует в этом родителе"
            )
    
    for field, value in update_dict.items():
        setattr(department, field, value)
    
    try:
        db.commit()
        db.refresh(department)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка целостности данных"
        )
    
    return department

# Удаляет подразделение.
def delete_department(
    db: Session,
    department_id: int,
    mode: str,
    reassign_to_id: Optional[int] = None
) -> bool:
    department = db.get(Department, department_id)

    if not department:
        return False
    
    if mode == "cascade":
        db.delete(department)

    elif mode == "reassign":
        target = db.get(Department, reassign_to_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Целевое подразделение с ID {reassign_to_id} не найдено"
            )
        
        db.query(Employee).filter(
            Employee.department_id == department_id
        ).update({"department_id": reassign_to_id})
        
        db.delete(department)
    
    db.commit()
    return True

# Получает прямых потомков подразделения.
def get_department_children(db: Session, department_id: int) -> List[Department]:
    return db.query(Department).filter(Department.parent_id == department_id).all()

# Проверяет, не создаст ли перемещение цикл.
def _check_cycle(db: Session, dept_id: int, new_parent_id: int):
    if dept_id == new_parent_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя сделать подразделение родителем самого себя"
        )
    
    current = new_parent_id
    visited = set()
    
    while current is not None:
        if current in visited:
            break
        
        if current == dept_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Нельзя переместить подразделение внутрь своего поддерева"
            )
        
        visited.add(current)
        parent = db.query(Department.parent_id).filter(Department.id == current).scalar()
        current = parent
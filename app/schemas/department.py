from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer
from typing import Optional, List
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[int] = Field(None)

    @field_validator('name')
    @classmethod
    def trim_name(cls, v: str) -> str:
        return v.strip()

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def trim_name(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v

class Department(DepartmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

class DepartmentNode(Department):
    employees: Optional[List[Employee]] = None
    children: List[DepartmentNode] = []

    model_config = ConfigDict(from_attributes=True)

from .employee import Employee
DepartmentNode.model_rebuild()
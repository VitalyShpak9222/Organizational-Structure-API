from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer
from typing import Optional
from datetime import date, datetime

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    hired_at: Optional[date] = None

    @field_validator('full_name', 'position')
    @classmethod
    def trim_strings(cls, v: str) -> str:
        return v.strip() if v else v

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    department_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
    
    @field_serializer('hired_at')
    def serialize_date(self, d: Optional[date]) -> Optional[str]:
        return d.isoformat() if d else None

Employee.model_rebuild()
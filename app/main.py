from fastapi import FastAPI
from app.routers import departments, employees

app = FastAPI(
    title="Organizational Structure API",
    description="API для управления организационной структурой",
    version="1.0.0"
)

app.include_router(departments.router)
app.include_router(employees.router)

@app.get("/")
def root():
    return {
        "message": "Organizational Structure API",
        "docs": "/docs",
        "endpoints": {
            "departments": "/departments",
            "employees": "/employees"
        }
    }
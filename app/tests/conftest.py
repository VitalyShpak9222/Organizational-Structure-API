import pytest
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import date

from app.core.base import Base
from app.core.database import get_db
from app.core.config import settings
from app.main import app
from app.models import Department, Employee

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/org_structure_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    def override_get_db_test():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db_test
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_department(db_session):
    dept = Department(name="Тестовый отдел")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept

@pytest.fixture
def sample_employee(db_session, sample_department):
    emp = Employee(
        department_id=sample_department.id,
        full_name="Иван Петров",
        position="Разработчик",
        hired_at=date(2024, 1, 15)
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp
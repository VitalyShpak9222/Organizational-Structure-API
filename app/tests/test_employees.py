import pytest
from fastapi import status

def test_create_employee(client, sample_department):
    response = client.post(
        f"/departments/{sample_department.id}/employees/",
        json={
            "full_name": "Мария Сидорова",
            "position": "Менеджер",
            "hired_at": "2024-02-01"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["full_name"] == "Мария Сидорова"
    assert data["position"] == "Менеджер"
    assert data["department_id"] == sample_department.id

def test_create_employee_invalid_department(client):
    response = client.post(
        "/departments/99999/employees/",
        json={
            "full_name": "Иван Петров",
            "position": "Разработчик"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_employee(client, sample_employee):
    response = client.get(f"/employees/{sample_employee.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_employee.id
    assert data["full_name"] == sample_employee.full_name

def test_update_employee(client, sample_employee):
    response = client.patch(
        f"/employees/{sample_employee.id}",
        params={"full_name": "Петр Иванов"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Петр Иванов"

def test_delete_employee(client, sample_employee):
    response = client.delete(f"/employees/{sample_employee.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_move_employee(client, sample_employee, sample_department):
    new_dept = client.post(
        "/departments/",
        json={"name": "Новый отдел"}
    ).json()
    
    response = client.post(
        f"/employees/{sample_employee.id}/move",
        params={"new_department_id": new_dept["id"]}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["department_id"] == new_dept["id"]
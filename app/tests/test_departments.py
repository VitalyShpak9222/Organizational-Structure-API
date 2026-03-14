import pytest
from fastapi import status

def test_create_department(client):
    response = client.post(
        "/departments/",
        json={"name": "IT отдел", "parent_id": None}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "IT отдел"
    assert data["id"] is not None

def test_create_department_with_parent(client, sample_department):
    response = client.post(
        "/departments/",
        json={"name": "Backend отдел", "parent_id": sample_department.id}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Backend отдел"
    assert data["parent_id"] == sample_department.id

def test_create_department_duplicate_name(client, sample_department):
    response = client.post(
        "/departments/",
        json={"name": sample_department.name, "parent_id": None}
    )
    assert response.status_code == status.HTTP_409_CONFLICT

def test_get_department(client, sample_department):
    response = client.get(f"/departments/{sample_department.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_department.id
    assert data["name"] == sample_department.name

def test_get_department_not_found(client):
    response = client.get("/departments/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_department(client, sample_department):
    response = client.patch(
        f"/departments/{sample_department.id}",
        json={"name": "Обновленный отдел"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Обновленный отдел"

def test_delete_department_cascade(client, sample_department):
    response = client.delete(
        f"/departments/{sample_department.id}",
        params={"mode": "cascade"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_get_department_employees(client, sample_department, sample_employee):
    response = client.get(f"/departments/{sample_department.id}/employees")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["department_id"] == sample_department.id
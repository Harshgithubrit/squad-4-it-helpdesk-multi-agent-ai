from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def token_for(username: str, password: str) -> str:
    response = client.post('/auth/login', json={'username': username, 'password': password})
    assert response.status_code == 200, response.text
    return response.json()['access_token']

def test_invalid_login_rejected():
    response = client.post('/auth/login', json={'username': 'bad', 'password': 'bad'})
    assert response.status_code == 401

def test_query_requires_authentication():
    response = client.post('/helpdesk/query', json={'query': 'Wi-Fi is not working for me'})
    assert response.status_code == 401

def test_pydantic_rejects_short_query():
    token = token_for('squad4-user', 'ChangeMe123!')
    response = client.post('/helpdesk/query', headers={'Authorization': f'Bearer {token}'}, json={'query': 'no'})
    assert response.status_code == 422

def test_user_cannot_access_admin_tools():
    token = token_for('squad4-user', 'ChangeMe123!')
    response = client.get('/admin/tools', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403

def test_admin_can_access_admin_tools():
    token = token_for('squad4-admin', 'ChangeAdmin123!')
    response = client.get('/admin/tools', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

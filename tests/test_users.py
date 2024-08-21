from http import HTTPStatus

from app.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
            'cpf': '01303175002',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    user = response.json()
    assert user['username'] == 'alice'
    assert user['email'] == 'alice@example.com'
    assert user['id'] == 1


def test_create_user_username_exist(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_exist(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'Alice',
            'email': user.email,
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_create_invalid_cpf(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'Alice',
            'email': 'test@teste.com',
            'password': 'secret',
            'cpf': '11111111111',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid CPF'}


def test_read_user(client, user):
    response = client.get(f'/users/{user.id}')

    user_response = response.json()
    assert response.status_code == HTTPStatus.OK
    assert user_response['username'] == user.username
    assert user_response['email'] == user.email
    assert user_response['id'] == 1


def test_read_user_not_found(client, user, token):
    response = client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    user_schema['created_at'] = user.created_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
    user_schema['updated_at'] = user.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%f')
    response = client.get('/users/')

    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'paulo',
            'email': 'paulo@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.OK
    user_response = response.json()
    assert user_response['username'] == 'paulo'
    assert user_response['email'] == 'paulo@example.com'


def test_update_different_id(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'paulo',
            'email': 'paulo@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_with_no_username(client, user, token):
    client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'paulo',
            'email': 'paulo@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_user(client, user, token):
    response = client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_different_id(client, other_user, token):
    response = client.delete(f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}

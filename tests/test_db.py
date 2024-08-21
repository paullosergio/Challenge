from sqlalchemy import select

from app.models import User


def test_create_user(session):
    user = User(username='paulo', email='paulo@gmail.com', password='minha_senha', cpf='01303175002')
    session.add(user)
    session.commit()
    result = session.scalar(select(User).where(User.email == 'paulo@gmail.com'))

    assert result.id == 1

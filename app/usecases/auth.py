from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.repositories.users import UserRepository


class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def register(self, email: str, password: str) -> User:
        existing_user = await self._user_repo.get_by_email(email)
        if existing_user:
            raise ConflictError("Email already exists")

        password_hash = hash_password(password)

        return await self._user_repo.create(
            email=email,
            password_hash=password_hash,
        )

    async def login(self, email: str, password: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        return create_access_token(
            user_id=user.id,
            role=user.role,
        )

    async def get_user(self, user_id: int) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        return user

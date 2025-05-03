from fastapi import Depends

from src.core.services.user.user import UserService
from src.core.dependencies.db_helper import DBDI
from src.core.services.database.postgres.models.user import UserModel
from src.core.services.auth.auth import oauth2_scheme

def get_user_service(db: DBDI) -> UserService:
    return UserService(db)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> UserModel:
    return user_service.verify_access_token(token)
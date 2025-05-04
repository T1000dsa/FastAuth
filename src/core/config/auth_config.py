from fastapi import HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from src.core.config.config import settings
from src.core.services.database.postgres.models.refresh_token import RefreshTokenModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.jwt.key
ALGORITHM = settings.jwt.algorithm

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

ACCESS_TYPE = 'access'
REFRESH_TYPE = 'refresh'

credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

from pydantic import BaseModel, field_validator
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

ACCESS_TYPE = 'access'
REFRESH_TYPE = 'refresh'

class Token(BaseModel):
    token: str
    token_type: str
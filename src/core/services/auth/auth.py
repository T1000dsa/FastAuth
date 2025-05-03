from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from typing import Annotated


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
TokenDep = Annotated[str, Depends(oauth2_scheme)]
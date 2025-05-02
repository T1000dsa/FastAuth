from fastapi import Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm


form_data = Annotated[OAuth2PasswordRequestForm, Depends()]
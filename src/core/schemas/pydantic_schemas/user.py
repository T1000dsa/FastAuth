from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class UserLogin(BaseModel):
    username: str
    password: str

class UserSchema(UserLogin):
    password_again:str
    public_name:Optional[str] = None
    email:Optional[str] = None
    bio:Optional[str] = None

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_again:
            raise ValueError("Passwords do not match")
        return self
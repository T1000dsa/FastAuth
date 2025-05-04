from jose import JWTError, jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from src.core.config.auth_config import (
    SECRET_KEY, 
    ALGORITHM,
    credentials_exception,
    pwd_context,
    ACCESS_TYPE,
    REFRESH_TYPE,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    RefreshTokenModel
    )

from src.core.schemas.pydantic_schemas.auth_schema import RefreshToken
from src.core.schemas.pydantic_schemas.user import UserSchema
from src.core.services.database.postgres.models.user import UserModel
from src.core.services.database.postgres.orm.token_crud import (
    insert_data, 
    select_data, 
    delete_data, 
    delete_all_user_tokens, 
    get_refresh_token_data)


logger = logging.getLogger(__name__)

class TokenService:
    def __init__(self):
        self.pwd_context = pwd_context
        
    async def create_token(self, data: dict, expires_delta: timedelta, token_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def create_access_token(self, data:dict):
        return await self.create_token(
            data, 
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            ACCESS_TYPE
            )
    
    async def create_refresh_token(self, data:dict):
        return await self.create_token(
            data, 
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            REFRESH_TYPE
            )


    def verify_token(self, token: str, token_type: str) -> dict:
        """
        Generic token verification method
        """
        
        try:
            payload:dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                raise credentials_exception
            return payload
        except JWTError:
            raise credentials_exception
    
    def hash_token(self, token: str) -> str:
        return self.pwd_context.hash(token)
    
    def verify_access_token(self, token: str) -> dict:
        return self.verify_token(token, ACCESS_TYPE)

    def verify_refresh_token(self, token: str) -> dict:
        return self.verify_token(token, REFRESH_TYPE)
    
    async def refresh_tokens(self, refresh_token: str) -> tuple[str]:
        """
        Generate new access token using refresh token
        """
        try:
            payload = self.verify_refresh_token(refresh_token)
            user_id = payload.get("id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # You might want to verify user still exists
            data_user = {"id": user_id}
            new_access_token = self.create_token(data_user, ACCESS_TOKEN_EXPIRE_MINUTES, ACCESS_TYPE)
            new_refresh_token = self.create_token(data_user, REFRESH_TOKEN_EXPIRE_DAYS, REFRESH_TYPE)
            
            return {ACCESS_TYPE:new_access_token, REFRESH_TYPE:new_refresh_token}
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        
    async def get_refresh_token(session, token:str) -> RefreshTokenModel:
        return await get_refresh_token_data(session, token)

    async def store_refresh_token(
            session,
            data:RefreshToken) -> None:
        await insert_data(
            session,
            data)

    async def revoke_token(
            session,
            data:UserModel,
            token:Optional[str],
            user_id:Optional[int]) -> None:
        await delete_data(
            session,
            data,
            token,
            user_id)

    async def revoke_all_user_tokens(
            session,
            data:UserModel
            ):
        await delete_all_user_tokens(session, data)

token_service = TokenService()
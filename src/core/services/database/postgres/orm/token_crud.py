from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete, join
from typing import Union, Optional
from datetime import datetime, timezone
import logging

from src.core.services.database.postgres.models.refresh_token import RefreshTokenModel
from src.core.services.database.postgres.models.user import UserModel
from src.core.schemas.pydantic_schemas.auth_schema import RefreshToken
from src.core.schemas.pydantic_schemas.user import UserSchema


logger = logging.getLogger(__name__)

async def select_data(
    session: AsyncSession,
    token: str,
    model_type: type[RefreshToken] | type[UserSchema]  # Use the type itself instead of instance
) -> list[RefreshTokenModel] | list[UserModel]:
    """
    Retrieve data based on token and model type.
    
    Args:
        session: Async database session
        token: The token to search for
        model_type: The schema type (RefreshToken or UserSchema) to determine which model to query
    
    Returns:
        List of model instances matching the token
    """
    try:
        if model_type is RefreshToken:
            # Query RefreshTokenModel by token
            result = await session.execute(
                select(RefreshTokenModel)
                .where(RefreshTokenModel.token == token)
            )
            return result.scalars().all()
        
        elif model_type is UserSchema:
            # Query UserModel by joining with refresh tokens
            result = await session.execute(
                select(UserModel)
                .join(RefreshTokenModel, RefreshTokenModel.user_id == UserModel.id)
                .where(RefreshTokenModel.token == token)
            )
            return result.scalars().all()
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
    except SQLAlchemyError as e:
        logger.error(f"Database error in select_data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in select_data: {e}")
        raise
    
async def insert_data(
    session: AsyncSession,
    data: RefreshToken
) -> RefreshTokenModel:
    """Properly handles refresh token insertion with error handling"""
    try:
        token_model = RefreshTokenModel(
            user_id=data.user_id,
            token=data.token,
            expires_at=data.expires_at,
            revoked=data.revoked,
            replaced_by_token=data.replaced_by_token,
            family_id=data.family_id,
            previous_token_id=data.previous_token_id,
            # created_at is automatically set by the model
            device_info=data.device_info if hasattr(data, 'device_info') else None
        )
        
        session.add(token_model)
        await session.commit()
        await session.refresh(token_model)
        return token_model
        
    except IntegrityError as err:
        await session.rollback()
        logger.error(f"Database integrity error: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error inserting token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store token"
        )
    
async def delete_data(
    session: AsyncSession,
    data: UserModel,
    token:Optional[str],
    user_id:Optional[int]
) -> None:
    try:
        if isinstance(data, UserModel):
            if token and user_id: # 1 1
                await session.execute(
                delete(RefreshTokenModel)
                .where(RefreshTokenModel.token == token and RefreshTokenModel.user_id == user_id))
                await session.commit()

            if token and not user_id: # 1 0
                await session.execute(
                delete(RefreshTokenModel)
                .where(RefreshTokenModel.token == token))
                await session.commit()
            
            if not token and user_id: # 0 1
                await session.execute(
                delete(RefreshTokenModel)
                .where(RefreshTokenModel.user_id == user_id))
                await session.commit()
            else:

                logger.error('Invalid data type provided')
                raise ValueError("Invalid data type provided")

        else:
            logger.error('Invalid data type provided')
            raise ValueError("Invalid data type provided")
        
    except ValueError as err:
        logger.error('Invalid data type provided')
        raise err
    
    except Exception as err:
        logger.critical(f'Something unpredictable: {err}')
        await session.rollback()
        raise err

async def delete_all_user_tokens(
        session:AsyncSession,
          data: UserModel
          ):
    try:
        await session.execute(
                delete(RefreshTokenModel)
                .where(RefreshTokenModel.user_id == data.id))
        await session.commit()
    except Exception as err:
        logger.critical(f'Something unpredictable: {err}')
    
async def get_refresh_token_data(session: AsyncSession, token:str) -> RefreshTokenModel:
    stm = (select(RefreshTokenModel).where(RefreshTokenModel.token == token))
    result = (await session.execute(stm)).scalars().all()
    valid_tokens:list[RefreshTokenModel] = []
    for i in result:
        if i.revoked:
            continue
        if i.expires_at <= datetime.now(timezone.utc):
            continue
        valid_tokens.append(i)

    freshest = sorted(valid_tokens, key=lambda x:x.created_at)[:-1]
    if freshest:
        return freshest


async def nuclear_option(session: AsyncSession):
    """Delete ALL refresh tokens in the system (admin only)"""
    try:
        await session.execute(delete(RefreshTokenModel))
        await session.commit()
        logger.warning("Nuclear option executed - all refresh tokens purged")

    except Exception as e:
        await session.rollback()
        logger.critical(f"Failed nuclear option: {e}")
        raise e
    

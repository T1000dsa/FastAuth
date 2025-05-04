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
    data: RefreshToken = None
) -> None:
    logger.debug(f'{type(data)}')
    try:
        if isinstance(data, RefreshToken):
            res = data.model_validate(data, from_attributes=True)
            token_data = {i: k for i, k in res.model_dump().items()}
            new_data = RefreshTokenModel(**token_data)

            existing = await session.get(RefreshTokenModel, token_data.get('id'))
            if existing:
                await session.merge(new_data)

            await session.commit()
            await session.refresh(new_data)  # Refresh to get any database-generated values
            logger.debug('Create refresh success')
            return new_data
        else:
            logger.error('Invalid data type provided')
            raise ValueError("Invalid data type provided")
        
    except IntegrityError as err:
        logger.info(f'{err}') 
        raise err
        
    except Exception as e:
        logger.error(f'Error inserting refresh token: {e}')
        await session.rollback()
        raise e
    
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
    
async def get_refresh_token_data(session: AsyncSession, token:str):
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
    

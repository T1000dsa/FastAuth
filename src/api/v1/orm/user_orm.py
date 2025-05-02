from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, join
from typing import Union, Optional
import logging

from src.core.services.database.postgres.models.user import UserModel
from src.core.schemas.pydantic_schemas.user import UserSchema as User_pydantic
from src.core.config.config import settings


logger = logging.getLogger(__name__)

async def select_data_user(
    session: AsyncSession,
    data: Union[User_pydantic, str, int]
) -> Optional[UserModel]:
   
    try:
        if isinstance(data, User_pydantic):
            query = select(UserModel).where(UserModel.username == data.username)
        elif isinstance(data, str):
            query = select(UserModel).where(UserModel.username == data)
        elif isinstance(data, int):
            query = select(UserModel).where(UserModel.id == data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    except ValueError as err:
        logger.error(f"select_data_user doesn't support such method {type(data)} {str(err)}")
        raise err

    except Exception as err:
        logger.error(f"Failed to select user data: {str(err)}")
        raise err
    
async def select_user_email(
    session: AsyncSession,
    data: Union[User_pydantic, str, int]
    ) -> Optional[UserModel]:
    try:
        if isinstance(data, str):
            query = select(UserModel).where(UserModel.mail == data)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    except ValueError as err:
        logger.error(f"select_user_email doesn't support such method {type(data)} {str(err)}")
        raise err
    
    except Exception as err:
        logger.error(f"Failed to select user data: {str(err)}")
        raise err

    
async def insert_data(
          session:AsyncSession,
          data:User_pydantic=None
          ):
    if type(data) == User_pydantic:
        res = User_pydantic.model_validate(data, from_attributes=True)
        user_data = {i:k for i, k in res.model_dump().items() if i != 'password_again'}
        new_data = UserModel(**user_data)
        new_data.set_password(new_data.password)
        session.add(new_data)
        await session.commit()

async def update_data(
            session:AsyncSession,
            data_id:int=None, 
            data:User_pydantic=None
            ):
    if type(data) == User_pydantic:
        res = User_pydantic.model_validate(data, from_attributes=True)
        stm = (update(UserModel).where(UserModel.id==data_id).values(**res))

        await session.execute(stm)
        await session.commit()

async def delete_data(
            session:AsyncSession,
            data_id:int=None
            ):

    stm = (delete(UserModel).where(UserModel.id==data_id)) 

    await session.execute(stm)
    await session.commit()
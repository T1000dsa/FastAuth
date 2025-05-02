from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.requests import Request
import logging

from src.core.dependencies.form_data import form_data
from src.core.services.auth.auth import TokenDep
from src.core.config.config import settings
from src.core.schemas.pydantic_schemas.user import UserSchema
from src.core.config.config import templates
from src.core.utils.prepared_templates import prepare_template
from src.core.dependencies.db_helper import DBDI


logger = logging.getLogger(__name__)
router = APIRouter(prefix=settings.prefix.api_data.prefix)


@router.post("/login")
async def login_for_access_token(
    session:DBDI,
    request:Request,
    form_data: form_data,
    user_service: TokenDep
):
    user = await user_service.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    
    access_token = user_service.create_access_token(data={"sub": user.mail})

    prepared_data = {
        "title":"Sign In"
        }
    
    template_response_body_data = await prepare_template(
        data=prepared_data,
        additional_data={
            "request":request,
            "access_token": access_token, 
            "token_type": "bearer"
            }
        )
    response = templates.TemplateResponse('login.html', template_response_body_data)
    return response


@router.post("/registration")
async def login_for_access_token(
    session:DBDI,
    request:Request,
    user_form:UserSchema,

):  
    user_service = ''#oauth2_scheme
    try:
        await user_service.create_user(session=session, data=user_form)
    except Exception as err:
        logger.error(f'{err}')
    
    prepared_data = {
        "title":"Sign Up"
        }
    
    template_response_body_data = await prepare_template(
        data=prepared_data,
        additional_data={
            "request":request,
            }
        )
    response = templates.TemplateResponse('register.html', template_response_body_data)
    return response
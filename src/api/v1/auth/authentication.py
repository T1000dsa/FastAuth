from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from urllib.parse import quote
from typing import Optional
import logging

from src.core.dependencies.form_data import form_data
from src.core.services.auth.auth import TokenDep
from src.core.config.config import settings
from src.core.schemas.pydantic_schemas.user import UserSchema
from src.core.config.config import templates
from src.core.utils.prepared_templates import prepare_template
from src.core.dependencies.db_helper import DBDI
from src.core.services.user.user import UserService
from src.core.menu.urls import choice_from_menu, menu_items


logger = logging.getLogger(__name__)
router = APIRouter(prefix=settings.prefix.api_data.prefix)

@router.get("/login")
async def html_login(
    request:Request,
    error:str|None = None
    ):

    prepared_data = {
        "title":"Sigh In",
        "template_action":settings.prefix.api_data.prefix+'/login/process',
        "error":error
        }
    
    template_response_body_data = await prepare_template(
        data=prepared_data,
        additional_data={
            "request":request,
            "menu_data":choice_from_menu,
            "menu":menu_items
        })

    response = templates.TemplateResponse('users/login.html', template_response_body_data)
    return response


@router.post("/login/process")
async def login(
    request:Request,
    session:DBDI,
    form_data: form_data,
    ):
    user = UserService(session)

    try:
        login_data = await user.authenticate_user(
        username=form_data.username,
        password=form_data.password
        
   )
    except Exception as err:
        logger.error(err)
        raise err
    
    if login_data is None:
        error_data = 'There is no such user!'
        return await html_login(request=request, error=error_data)
        
    response = RedirectResponse(url='/', status_code=302)
    return response

@router.get("/register")
async def html_register(
    request:Request
):
    logger.info('inside html_register')

    prepared_data = {
        "title":"Sigh Up",
        "template_action":settings.prefix.api_data.prefix+'/register/process',
        }
    
    template_response_body_data = await prepare_template(
        data=prepared_data,
        additional_data={
            "request":request,
            "menu_data":choice_from_menu,
            "menu":menu_items
        })
    
    response = templates.TemplateResponse('users/register.html', template_response_body_data)
    return response

@router.post("/register/process")
async def register(
    request:Request,
    session: DBDI,
    username: str = Form(...),
    password: str = Form(...),
    password_again: str = Form(...),
    mail: str = Form(""),
    bio: str = Form("")
):

    logger.info('inside register')

    user_data = UserSchema(
        username=username,
        password=password,
        password_again=password_again,
        mail=mail,
        bio=bio
    )

    user = UserService(session)
    try:
        await user.create_user(user_data)
 
    except IntegrityError as err:
        logger.info(f'{err}') 
        return "Such user already in database"

    except Exception as err:
        logger.error(f'{err}')
        raise err
    
    prepared_data = {
        "title":"Registration success",
        "content":"Registration was success!"
        }
    
    logger.info('success registration')
    template_response_body_data = await prepare_template(
        data=prepared_data,
        additional_data={
            "request":request,
            "menu_data":choice_from_menu,
            "menu":menu_items
        })
    return templates.TemplateResponse('users/register_success.html', template_response_body_data)


@router.get('/logout')
async def logout():
    response = RedirectResponse(url=router.prefix + "/login")
    #response.delete_cookie(ACCESS_TYPE)
    #response.delete_cookie(REFRESH_TYPE)
    return response
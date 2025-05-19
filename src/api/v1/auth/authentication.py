from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
import logging

from src.core.services.auth.token_service import TokenService
from src.core.services.auth.user_service import UserService
from src.core.schemas.pydantic_schemas.user import UserSchema
from src.core.config.config import templates, settings
from src.core.utils.prepared_templates import prepare_template
from src.core.dependencies.db_helper import DBDI
from src.core.menu.urls import choice_from_menu, menu_items
from src.core.dependencies.auth_deps import GET_TOKEN_SERVICE, GET_CURRENT_ACTIVE_USER, GET_AUTH_SERVICE, GET_CURRENT_USER
from src.core.config.auth_config import (
    ACCESS_TYPE, 
    REFRESH_TYPE,
    CSRF_TYPE, 
    form_scheme,
    oauth2_scheme
    )

logger = logging.getLogger(__name__)
router = APIRouter(prefix=settings.prefix.api_data.prefix, tags=['auth'])


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
    request: Request,
    form_data: form_scheme,
    auth_service: GET_AUTH_SERVICE
):
    try:
        tokens = await auth_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )
        
        if not tokens:
            return await html_login(request=request, error='Invalid credentials')
        
        response = RedirectResponse(url='/', status_code=302)
        await auth_service.token_service.set_secure_cookies(
            response=response,
            tokens=tokens
        )
        return response
        
    except Exception as err:
        logger.error(f"Login failed: {err}")
        return await html_login(request=request, error='Login failed')

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
    auth_service: GET_AUTH_SERVICE,
    username: str = Form(...),
    password: str = Form(...),
    password_again: str = Form(...),
    mail: str = Form(""),
    bio: str = Form("")
    
):

    logger.info(f'User: {username} tries to regist...')

    user_data = UserSchema(
        username=username,
        password=password,
        password_again=password_again,
        mail=mail,
        bio=bio
    )

    user = auth_service
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
async def logout(
    request: Request,
    auth_service: GET_AUTH_SERVICE
):
    response = RedirectResponse(url=router.prefix + "/login")
    
    try:
        response = await auth_service.logout_user(request=request, response=response)
    except (JWTError, ValueError) as e:
        logger.debug(f"Token error during logout: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
    
    return response


@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    session: DBDI,
    token_service: GET_TOKEN_SERVICE
):
    refresh_token = request.cookies.get(REFRESH_TYPE)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    try:
        new_tokens = await token_service.rotate_tokens(session, refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token rotation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    response = RedirectResponse(url='/', status_code=302)
    await token_service.set_secure_cookies(
        response=response,
        access_token=new_tokens[ACCESS_TYPE],
        refresh_token=new_tokens[REFRESH_TYPE],
        csrf_token=new_tokens.get(CSRF_TYPE)
    )
    return response

@router.post('/test1')
async def test_auth_1(user: GET_CURRENT_USER):
    return {"message": "Authenticated", "user": user.username}

@router.post('/test2') 
async def test_auth_2(user: GET_CURRENT_ACTIVE_USER):
    return {"message": "Active user", "user": user.username}
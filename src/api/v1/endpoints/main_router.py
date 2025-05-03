from fastapi import APIRouter
from fastapi.requests import Request
import logging

from src.core.config.config import templates
from src.core.utils.prepared_templates import prepare_template
from src.core.menu.urls import choice_from_menu, get_menu


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get('/')
async def index_func(request:Request):
    prepared_data = {
        "title":"Main page"
        }
    
    template_response_body_data = await prepare_template(
        data=prepared_data,
        additional_data={
            "request":request,
            "menu_data":choice_from_menu,
            "menu":get_menu()
            }
        )

    response = templates.TemplateResponse('index.html', template_response_body_data)
    return response
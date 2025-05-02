from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from concurrent.futures import ProcessPoolExecutor
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
import logging

from src.core.config.config import settings
from src.core.config.config import templates
from src.core.utils.prepared_templates import prepare_template


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
            "request":request
            }
        )

    response = templates.TemplateResponse('index.html', template_response_body_data)
    return response
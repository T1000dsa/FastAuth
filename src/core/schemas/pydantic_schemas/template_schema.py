from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class TemplateData(BaseModel):
    title: Optional[str] = Field(default=None, description="Page title")
    content: Optional[str] = Field(default=None, description="Main content")
    description: Optional[str] = Field(default=None, description="Additional description")
    data: Optional[dict] = Field(default=None, description="Additional dynamic data")
    error:Optional[str] = Field(default=None, description="Error's data")
    form_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Form's data")
    template_action:Optional[str] = Field(default=None, description="Teplate's action (endpoint's url)")
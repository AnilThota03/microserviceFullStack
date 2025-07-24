from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    name: Optional[str]
    type: Optional[str]
    is_translated: Optional[bool] = Field(None, alias="isTranslated")
    original_document: Optional[str] = Field(None, alias="originalDocument")
    translated_document: Optional[str] = Field(None, alias="translatedDocument")
    project_id: Optional[str] = Field(None, alias="projectId")
    source_language: Optional[str] = Field(None, alias="sourceLanguage")
    target_language: Optional[str] = Field(None, alias="targetLanguage")
    user_id: Optional[str] = Field(None, alias="userId")

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    name: Optional[str]
    type: Optional[str]
    is_translated: Optional[bool]
    original_document: Optional[str]
    translated_document: Optional[str]

class DocumentOut(DocumentBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[datetime] = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(alias="updatedAt")

    class Config:
        validate_by_name = True
        from_attributes = True

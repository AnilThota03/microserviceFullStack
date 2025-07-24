from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId: {value}")
        return ObjectId(value)

class ProjectBase(BaseModel):
    name: str
    description: str
    userId: PyObjectId = Field(...)
    serviceType: str

class ProjectCreate(ProjectBase):
    serviceType: Optional[str] = None

class ProjectOut(ProjectBase):
    id: PyObjectId = Field(alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
        }

class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

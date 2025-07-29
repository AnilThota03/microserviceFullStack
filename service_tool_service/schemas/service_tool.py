from pydantic import BaseModel

class ServiceToolSchema(BaseModel):
    _id: str  # fixed values like "translation", "comparison", "annotation"
    name: str

    class Config:
        orm_mode = True

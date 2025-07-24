from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ComparisonDocumentBase(BaseModel):
    name: str
    originalDocument: Optional[str] = None
    modifiedDocument: Optional[str] = None
    comparedDocument: Optional[str] = None
    isCompared: bool = False
    model: Optional[str] = None
    projectId: str
    type: str
    userId: str
    comparisonData: Optional[List[Dict[str, Any]]] = None

class ComparisonDocumentCreate(ComparisonDocumentBase):
    pass

class ComparisonDocumentUpdate(BaseModel):
    name: Optional[str] = None
    originalDocument: Optional[str] = None
    modifiedDocument: Optional[str] = None
    comparedDocument: Optional[str] = None
    isCompared: Optional[bool] = None
    model: Optional[str] = None
    projectId: Optional[str] = None
    userId: Optional[str] = None
    comparisonData: Optional[List[Dict[str, Any]]] = None

class ComparisonDocumentOut(ComparisonDocumentBase):
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class ComparisonDocumentListOut(BaseModel):
    message: str
    data: List[ComparisonDocumentOut]

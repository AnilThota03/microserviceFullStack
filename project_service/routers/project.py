from fastapi import APIRouter
from project_service.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from project_service.services.project import (
    create_project,
    get_projects,
    get_projects_by_user_id,
    get_project_details_by_id,
    delete_project,
    update_project_details,
    get_projects_by_user_id_and_service
)
from typing import List

router = APIRouter(
    prefix="/project/api",
    tags=["Projects"]
)

@router.get("/user-service", response_model=dict)
async def get_projects_by_user_and_service(user_id: str, service_type: str):
    result = await get_projects_by_user_id_and_service(user_id, service_type)
    return {"message": "Projects retrieved by user and service", "data": result}

@router.get("/", response_model=dict)
async def get_all_projects():
    result = await get_projects()
    return {"message": "Projects retrieved successfully", "data": result}

@router.post("/create-translation", response_model=dict)
async def create_translation_project(project: ProjectCreate):
    project.serviceType = "translation"
    result = await create_project(project)
    return {"message": "Translation project created", "data": result}

@router.post("/create-comparison", response_model=dict)
async def create_comparison_project(project: ProjectCreate):
    project.serviceType = "comparison"
    result = await create_project(project)
    return {"message": "Comparison project created", "data": result}

@router.post("/create-annotation", response_model=dict)
async def create_annotation_project(project: ProjectCreate):
    project.serviceType = "annotation"
    result = await create_project(project)
    return {"message": "Annotation project created", "data": result}

@router.get("/user/{user_id}", response_model=dict)
async def get_projects_by_user(user_id: str):
    result = await get_projects_by_user_id(user_id)
    return {"message": "Projects retrieved by userID", "data": result}

@router.get("/details/{project_id}", response_model=dict)
async def get_project_by_id(project_id: str):
    result = await get_project_details_by_id(project_id)
    return {"message": "Project retrieved", "data": result}

@router.put("/{project_id}", response_model=dict)
async def update_project(project_id: str, project: ProjectUpdate):
    result = await update_project_details(project_id, project)
    return {"message": "Project updated", "data": result}

@router.delete("/{project_id}", response_model=dict)
async def delete_project_by_id(project_id: str):
    await delete_project(project_id)
    return {"message": "Project deleted"}

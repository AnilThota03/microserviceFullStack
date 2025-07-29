
import logging
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/project/api",
    tags=["Projects"]
)

@router.get("/user-service", response_model=dict)
async def get_projects_by_user_and_service(user_id: str, service_type: str):
    logger.debug(f"[get_projects_by_user_and_service] Called with user_id={user_id}, service_type={service_type}")
    try:
        result = await get_projects_by_user_id_and_service(user_id, service_type)
        logger.info(f"[get_projects_by_user_and_service] Retrieved {len(result) if result else 0} projects")
        return {"message": "Projects retrieved by user and service", "data": result}
    except Exception as e:
        logger.error(f"[get_projects_by_user_and_service] Failed: {e}")
        raise

@router.get("/", response_model=dict)
async def get_all_projects():
    logger.debug("[get_all_projects] Called")
    try:
        result = await get_projects()
        logger.info(f"[get_all_projects] Retrieved {len(result) if result else 0} projects")
        return {"message": "Projects retrieved successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_all_projects] Failed: {e}")
        raise

@router.post("/create-translation", response_model=dict)
async def create_translation_project(project: ProjectCreate):
    logger.debug(f"[create_translation_project] Called with project={project}")
    try:
        project.serviceType = "translation"
        result = await create_project(project)
        logger.info(f"[create_translation_project] Translation project created for user {getattr(project, 'userId', 'unknown')}")
        return {"message": "Translation project created", "data": result}
    except Exception as e:
        logger.error(f"[create_translation_project] Failed: {e}")
        raise

@router.post("/create-comparison", response_model=dict)
async def create_comparison_project(project: ProjectCreate):
    logger.debug(f"[create_comparison_project] Called with project={project}")
    try:
        project.serviceType = "comparison"
        result = await create_project(project)
        logger.info(f"[create_comparison_project] Comparison project created for user {getattr(project, 'userId', 'unknown')}")
        return {"message": "Comparison project created", "data": result}
    except Exception as e:
        logger.error(f"[create_comparison_project] Failed: {e}")
        raise

@router.post("/create-annotation", response_model=dict)
async def create_annotation_project(project: ProjectCreate):
    logger.debug(f"[create_annotation_project] Called with project={project}")
    try:
        project.serviceType = "annotation"
        result = await create_project(project)
        logger.info(f"[create_annotation_project] Annotation project created for user {getattr(project, 'userId', 'unknown')}")
        return {"message": "Annotation project created", "data": result}
    except Exception as e:
        logger.error(f"[create_annotation_project] Failed: {e}")
        raise

@router.get("/user/{user_id}", response_model=dict)
async def get_projects_by_user(user_id: str):
    logger.debug(f"[get_projects_by_user] Called with user_id={user_id}")
    try:
        result = await get_projects_by_user_id(user_id)
        logger.info(f"[get_projects_by_user] Retrieved {len(result) if result else 0} projects for user {user_id}")
        return {"message": "Projects retrieved by userID", "data": result}
    except Exception as e:
        logger.error(f"[get_projects_by_user] Failed for user {user_id}: {e}")
        raise

@router.get("/details/{project_id}", response_model=dict)
async def get_project_by_id(project_id: str):
    logger.debug(f"[get_project_by_id] Called with project_id={project_id}")
    try:
        result = await get_project_details_by_id(project_id)
        logger.info(f"[get_project_by_id] Project retrieved for id={project_id}")
        return {"message": "Project retrieved", "data": result}
    except Exception as e:
        logger.error(f"[get_project_by_id] Failed for id {project_id}: {e}")
        raise

@router.put("/{project_id}", response_model=dict)
async def update_project(project_id: str, project: ProjectUpdate):
    logger.debug(f"[update_project] Called with project_id={project_id}, project={project}")
    try:
        result = await update_project_details(project_id, project)
        logger.info(f"[update_project] Project updated for id={project_id}")
        return {"message": "Project updated", "data": result}
    except Exception as e:
        logger.error(f"[update_project] Failed for id {project_id}: {e}")
        raise

@router.delete("/{project_id}", response_model=dict)
async def delete_project_by_id(project_id: str):
    await delete_project(project_id)
    return {"message": "Project deleted"}

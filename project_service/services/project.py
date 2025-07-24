

def serialize_project(project):
    project["_id"] = str(project["_id"])
    if "userId" in project and hasattr(project["userId"], "__str__"):
        project["userId"] = str(project["userId"])
    from ..schemas.project import ProjectOut
    return ProjectOut(**project)

from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from project_service.models.project import get_project_collection
from project_service.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

async def get_projects():
    projects = get_project_collection()
    result = []
    async for project in projects.find({}):
        result.append(serialize_project(project))
    return result

async def create_project(project: ProjectCreate):
    projects = get_project_collection()
    project_dict = project.dict(by_alias=True)
    if project_dict.get("userId"):
        project_dict["userId"] = ObjectId(project_dict["userId"])
    project_dict["createdAt"] = datetime.utcnow()
    project_dict["updatedAt"] = datetime.utcnow()
    result = await projects.insert_one(project_dict)
    project_dict["_id"] = str(result.inserted_id)
    project_dict["userId"] = str(project_dict["userId"])
    from ..schemas.project import ProjectOut
    return ProjectOut(**project_dict)

async def get_projects_by_user_id(user_id: str):
    projects = get_project_collection()
    result = []
    try:
        query = {"userId": ObjectId(user_id)}
    except Exception:
        query = {"userId": user_id}
    async for project in projects.find(query):
        result.append(serialize_project(project))
    return result

async def get_project_details_by_id(id: str):
    projects = get_project_collection()
    project = await projects.find_one({"_id": ObjectId(id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return serialize_project(project)

async def update_project_details(id: str, project: ProjectUpdate):
    projects = get_project_collection()
    update_data = {k: v for k, v in project.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    updated = await projects.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return serialize_project(updated)

async def delete_project(id: str):
    projects = get_project_collection()
    result = await projects.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

async def get_projects_by_user_id_and_service(user_id: str, service_type: str):
    projects = get_project_collection()
    try:
        query = {"userId": ObjectId(user_id), "serviceType": service_type}
    except Exception:
        query = {"userId": user_id, "serviceType": service_type}
    cursor = projects.find(query)
    result = []
    async for project in cursor:
        result.append(serialize_project(project))
    return result

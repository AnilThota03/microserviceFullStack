import logging
from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from translation_document_service.schemas.translation_document import DocumentOut
from translation_document_service.services.translation_document import (
    create_document_with_file,
    delete_document,
    get_document_by_id,
    get_documents_by_project_id,
    update_document_with_file
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/translation-document/api/document",
    tags=["Documents"]
)

@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document_with_file_route(
    name: str = Form(...),
    project_id: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = File(...),
    target_language: str = Form(...)
):
    logger.debug(f"[create_document_with_file_route] Called with name={name}, project_id={project_id}, user_id={user_id}, target_language={target_language}")
    try:
        result = await create_document_with_file(
            name=name,
            project_id=project_id,
            file=file,
            user_id=user_id,
            target_language=target_language
        )
        logger.info(f"[create_document_with_file_route] Successfully created document '{name}' for project '{project_id}' by user '{user_id}'")
        return {"message": "Document created successfully", "data": result}
    except Exception as e:
        logger.error(f"[create_document_with_file_route] Failed to create document '{name}': {e}")
        raise

@router.get("/project/{project_id}", response_model=dict)
async def get_documents_by_project_id_route(project_id: str):
    logger.debug(f"[get_documents_by_project_id_route] Called with project_id={project_id}")
    try:
        result = await get_documents_by_project_id(project_id)
        logger.info(f"[get_documents_by_project_id_route] Found {len(result)} documents for project ID: {project_id}")
        return {"message": "Documents fetched successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_documents_by_project_id_route] Failed for project_id={project_id}: {e}")
        raise

@router.get("/{document_id}", response_model=dict)
async def get_document_by_id_route(document_id: str):
    logger.debug(f"[get_document_by_id_route] Called with document_id={document_id}")
    try:
        result = await get_document_by_id(document_id)
        logger.info(f"[get_document_by_id_route] Document fetched for ID: {document_id}")
        return {"message": "Document fetched successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_document_by_id_route] Failed for document_id={document_id}: {e}")
        raise

@router.put("/{document_id}", response_model=dict)
async def update_document_with_file_route(
    document_id: str,
    file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None)
):
    logger.debug(f"[update_document_with_file_route] Called with document_id={document_id}, file={'Yes' if file else 'No'}, name={name}")
    if not file and not name:
        logger.error(f"[update_document_with_file_route] Update failed for document {document_id}: No file or name provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least a file or a new name must be provided to update."
        )
    try:
        result = await update_document_with_file(document_id, file, name)
        logger.info(f"[update_document_with_file_route] Successfully updated document with ID: {document_id}")
        return {"message": "Document updated successfully", "data": result}
    except Exception as e:
        logger.error(f"[update_document_with_file_route] Failed for document_id={document_id}: {e}")
        raise

@router.delete("/{document_id}", response_model=dict)
async def delete_document_route(document_id: str):
    logger.debug(f"[delete_document_route] Called with document_id={document_id}")
    try:
        logger.warning(f"[delete_document_route] Request to delete document with ID: {document_id}")
        await delete_document(document_id)
        logger.info(f"[delete_document_route] Successfully deleted document with ID: {document_id}")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"[delete_document_route] Failed to delete document_id={document_id}: {e}")
        raise

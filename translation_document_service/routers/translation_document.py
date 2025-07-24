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
    # --- FIX ---
    # The function signature now exactly matches the fields sent by your FormData
    name: str = Form(...),
    project_id: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = File(...),
    target_language: str = Form(...)
):
    logger.info(f"Request to upload document '{name}' for project '{project_id}' by user '{user_id}'.")
    
    # The call to the service function is now clean and correct.
    result = await create_document_with_file(
        name=name,
        project_id=project_id,
        file=file,
        user_id=user_id,
        target_language=target_language
    )
    
    # doc_id = getattr(result, 'id', result.get('id', 'N/A'))
    logger.info(f"Successfully created document '{name}' with ID: ")
    
    return {"message": "Document created successfully", "data": result}

@router.get("/project/{project_id}", response_model=dict)
async def get_documents_by_project_id_route(project_id: str):
    logger.info(f"Fetching all documents for project ID: {project_id}")
    result = await get_documents_by_project_id(project_id)
    logger.info(f"Found {len(result)} documents for project ID: {project_id}")
    return {"message": "Documents fetched successfully", "data": result}

@router.get("/{document_id}", response_model=dict)
async def get_document_by_id_route(document_id: str):
    logger.info(f"Fetching document with ID: {document_id}")
    result = await get_document_by_id(document_id)
    return {"message": "Document fetched successfully", "data": result}

@router.put("/{document_id}", response_model=dict)
async def update_document_with_file_route(
    document_id: str,
    file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None)
):
    if not file and not name:
        logger.error(f"Update failed for document {document_id}: No file or name provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least a file or a new name must be provided to update."
        )
    logger.info(f"Updating document with ID: {document_id}. File included: {'Yes' if file else 'No'}")
    result = await update_document_with_file(document_id, file, name)
    logger.info(f"Successfully updated document with ID: {document_id}")
    return {"message": "Document updated successfully", "data": result}

@router.delete("/{document_id}", response_model=dict)
async def delete_document_route(document_id: str):
    logger.warning(f"Request to delete document with ID: {document_id}")
    await delete_document(document_id)
    logger.info(f"Successfully deleted document with ID: {document_id}")
    return {"message": "Document deleted successfully"}
